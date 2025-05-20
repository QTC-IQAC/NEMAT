import subprocess
import sys
import os
from pmx.utils import create_folder
import shutil
import acpype
from acpype.topol import ACTopol, MolTopol
import yaml
from AZtutorial import *



class InputPreparations():
    """
    Prepares directories and input files for ligands and proteins for GROMACS MD simulations
    """
    def __init__(self, inputDirName="input",**kwargs):
        
        self.inputDirName = inputDirName

        self.mdppath = f"{os.getcwd()}/mdppath"
        
        self.cwd = os.getcwd()
        self.inputDirPath = os.path.join(self.cwd, self.inputDirName)
        
        self.ligand_files = [] # Can also be dictionary {filename : chargeType(str = "default","resp")}
        self.protein_files = []
        self.membrane_files = []

        self.defaultChargeType = "default" # or "resp" also
        
        print(f"Input directory will be {self.inputDirPath}")

        for key, val in kwargs.items():
            setattr(self,key,val)
    
    def convertStrToPath(self):
        """
        Converts strings in ligands and protein lists to absolute paths
        """
        # ALBERT: added membrane

        ####################
        #     LIGANDS      #
        ####################

        if type(self.ligand_files) is list:
            ligand_paths = [os.path.abspath(lig) for lig in self.ligand_files]
        elif type(self.ligand_files) is dict:
            ligand_paths = {os.path.abspath(lig):mode for lig,mode in self.ligand_files.items()}
        self.ligand_files = ligand_paths
        print(self.ligand_files)

        ####################
        #     PROTEIN      #
        ####################

        protein_paths = [os.path.abspath(prot) for prot in self.protein_files]
        self.protein_files = protein_paths
        print(self.protein_files)
        
        ####################
        #     MEMBRANE     #
        ####################
        membrane_paths = [os.path.abspath(memb) for memb in self.membrane_files]
        self.membrane_files = membrane_paths
        print(self.membrane_files)

    def prepareInputDir(self)->None:
        """
        Creates directory and its sub-structures where to store the input files
        """
        # ALBERT: added membrane directory

        print(f"Preparing input directories")

        create_folder(self.inputDirPath)
        os.chdir(self.inputDirPath)

        # Create sub-folders
        create_folder("ligands")
        create_folder("proteins")
        create_folder("membrane")
        subprocess.run(["cp","-r",self.mdppath,"."])

        os.chdir(self.cwd)

    def genLigInputs(self,clean=True)-> None:
        """
        Generates inputs for different ligands. Generates topology with acpype and
        puts their inputs in their corresponding directories.
        ligand_files :: list of ligans .mol2 files
        """

        for ligFile in self.ligand_files:
            ligName = os.path.basename(ligFile).split(".")[0]
            print(f"\nGenerating inputs for ligand: {ligName}")

            # Check type of ligand_files
            if type(self.ligand_files) is dict:
                chargeType = self.ligand_files[ligFile]
            else:
                chargeType = self.defaultChargeType
            
            print(f"\nNOTE: {ligName} has charge type {chargeType}")
            
            print("\n--Generating Topology...")
            self._genLigTopol(ligFile,chargeType)
            
            print("\n--Copying Files...")
            self._cpLigFiles(ligName)
            
            print("\n--Isolating Atom Types...")
            self._isolateAtomTypes(ligName)

            print("\n--Changing Molecule Type to MOL...")
            topolFile = os.path.join(self.inputDirName,"ligands",ligName,"ligTopol.itp")
            self._changeMolType(topolFile,"MOL")

            if clean:
                self._cleanAcpypeFolders(ligName)

    def _genLigTopol(self,ligand_file:str,chargeMode:str)->None:
        """
        Generates GROMACS input files for the ligands

        ligand_file :: relative path of ligand .mol2 file
        """
        ligand_file = os.path.abspath(ligand_file)

        # Use acpype to generate topology files
        if chargeMode == "resp":
            molecule = ACTopol(ligand_file,chargeType="user")
        else:
            molecule = ACTopol(ligand_file)

        molecule.createACTopol()
        molecule.createMolTopol()

    def _cpLigFiles(self,ligand:str)->None:
        """
        Copies the input files for the ligand into its corresponding folder
        ligand :: ligand name
        """

        # Locate acpype folder
        acpype_dir = os.path.abspath(ligand+".acpype")
        print(acpype_dir)

        # Locate relevant input files
        files = {ligand+"_GMX.itp":"ligTopol.itp",
                ligand+"_NEW.pdb":"ligGeom.pdb", # Better format if using AZtutorial
                "posre_"+ligand+".itp":"ligPosre.itp"}

        # Copy files to ligands folder
        ligand_dir = os.path.join(self.inputDirPath,"ligands",ligand)
        print(ligand_dir)
        create_folder(ligand_dir)

        for file,new_file in files.items():
            old_path = os.path.join(acpype_dir, file)
            new_path = os.path.join(ligand_dir, new_file)
            if os.path.isfile(old_path):
                print(f"Writing {old_path} to {new_path}")
                shutil.copy(old_path,new_path)

    def _isolateAtomTypes(self,ligand:str):
        """
        Generate new file with atom types header and rewrite ligTopol
        ligand :: ligand name
        """
        ligand_dir = os.path.join(self.inputDirPath,"ligands",ligand)
        # ligand_dir = os.path.abspath("input_test_py/ligands/"+ligand)
        ligTopolFile = os.path.join(ligand_dir,"ligTopol.itp")

        # Read the ligand topology file
        with open(ligTopolFile, 'r') as file:
            lines = file.readlines()

        # Extract AtomType lines
        atomTypeLines = []
        extracting = False
        for line in lines[1:]:
            if line.startswith("[ atomtypes ]"):
                extracting = True
            
            if line.startswith("[ moleculetype ]"):
                extracting = False
                break

            if extracting:
                atomTypeLines.append(line)

        # Rewrite ligTopol file without atomtype lines
        topol_lines = [line for line in lines if line not in atomTypeLines[:-1]] # Last line is an intro so we want to keep them
        with open(ligTopolFile, 'w') as file:
            file.write("".join(topol_lines))

        # Check if there is bond_type column
        existsBondTypeColumn = "bond_type" in atomTypeLines[1]

        if not existsBondTypeColumn:
            print(" bond_type column not found. Proceeding normally")
            # Write new file with atom type lines
            atomTypesFile = os.path.join(ligand_dir,"ligAtomTypes.itp")
            with open(atomTypesFile, 'w') as file:
                file.write("".join(atomTypeLines[:-1]))
        
        else:
            print(" bond_type column found. Removing it")
            # Write new file with atom type lines
            atomTypesFile = os.path.join(ligand_dir,"ligAtomTypes_original.itp")
            with open(atomTypesFile, 'w') as file:
                file.write("".join(atomTypeLines[:-1]))

            # Write new file with atom types lines but without bond_type column
            atomTypesFileTrim = os.path.join(ligand_dir,"ligAtomTypes.itp")
            with open(atomTypesFileTrim, 'w') as file:
                for ii,line in enumerate(atomTypeLines[:-1]):
                    if ii == 0 :
                        file.write(line) # Write first line (which is atom types)
                    else:
                        trimmed_line = line.split()
                        trimmed_line.pop(1)
                        file.write("    ".join(trimmed_line)+"\n")
            

    def _cleanAcpypeFolders(self,ligand:str) -> None:
        """
        Removes ACPype folders for ligands
        ligand :: ligand name
        """
        acpype_dir = os.path.abspath(ligand+".acpype")
        print(f"Cleaning ACPype folder {acpype_dir}")

        if os.path.exists(acpype_dir):
            shutil.rmtree(acpype_dir)

    def _getMolType(self, itpFile): ##BertaChanged
        """
        Extract molecule type from any topology file
        """
        with open(itpFile, "r") as file:
            lines = file.readlines()

        # Find line number where [ moleculetype ] is defined 
        for i, line in enumerate(lines):
            if '[ moleculetype ]' in line:
                molTypeIdx = i
                break
        
        # Extract molecule types from the itp file
        molTypes = lines[molTypeIdx+2].strip().split()[0]
        
        return molTypes

    def _changeMolType(self,topolFile:str,newMolType:str="MOL") -> None:
        """
        Changes the name of the molecule in topology file to be MOL
        """
        with open(topolFile,"r") as file:
            lines = file.readlines()

        # Find line number where [ moleculetype ] is defined 
        for i, line in enumerate(lines):
            if '[ moleculetype ]' in line:
                molTypeIdx = i
                break
        
        # Extract molecule types from the itp file
        molType = lines[molTypeIdx+2].strip().split()[0]

        if molType == "MOL":
            print("Ligand molecule type is already MOL. Skipping...")
        else:
            # Change molecule type
            lines[molTypeIdx+2] = lines[molTypeIdx+2].replace(molType,newMolType)

            with open(topolFile,"w") as file:
                for line in lines:
                    file.write(line)

    def genProteinInputs(self) -> None:
        # ALBERT: now it assumes that the files were pregenerated.
        """
        Generates input files for protein
        protein_file :: list of protein files to be included
        """
        
        print(f"\nGenerating inputs for protein:")
        for protFile in self.protein_files:
            try:
                os.mkdir(f"{self.inputDirPath}/proteins/{protFile.split('/')[-2]}")
            except FileExistsError:
                pass
            if os.path.isdir(protFile):
                try:
                    shutil.copytree(protFile, f"{self.inputDirPath}/proteins/{'/'.join(protFile.split('/')[-2:])}")
                except FileExistsError:
                    print(f"\t--> Directory {'/'.join(protFile.split('/')[-2:])} already exists. Skipping...")
                    continue
            else:
                shutil.copy(protFile, f"{self.inputDirPath}/proteins/{'/'.join(protFile.split('/')[-2:])}") # move files here
            print('\t  -->  ',"/".join(protFile.split('/')[-2:]))
    def genMembraneInputs(self) -> None:
        # ALBERT: It assumes that the files were pregenerated.
        """
        Generates input files for protein
        protein_file :: list of protein files to be included
        """
        
        print(f"\nGenerating inputs for membrane.")
        for membFile in self.membrane_files:
            if os.path.isdir(membFile):
                try:
                    shutil.copytree(membFile, f"{self.inputDirPath}/membrane/{membFile.split('/')[-1]}")
                except FileExistsError:
                    print(f"\t--> Directory {membFile.split('/')[-1]} already exists. Skipping...")
                    continue
            else:
                shutil.copy(membFile, f"{self.inputDirPath}/membrane/{membFile.split('/')[-1]}") # move files here
            print('\t --> ',membFile.split('/')[-1])
            

    def genProteinInputs_old(self,manual:bool=True) -> None:
        """
        Generates input files for protein
        protein_file :: list of protein.pdb files
        """
        for protFile in self.protein_files:
            protName = os.path.basename(protFile).split('.')[0]
            print(f"\nGenerating inputs for protein: {protName}")
            self._genProtTopol(protFile,manual=manual)
                

    def _genProtTopol(self,protein_file:str,manual:bool=True) -> None:
        """
        Generates GROMACS input files for the protein

        protein_file :: relative path of protein.pdb file
        """
        
        # Get protein name
        protein = os.path.basename(protein_file).split('.')[0]
        protein_file = os.path.abspath(protein_file)

        # Create folder for protein
        protein_dir = os.path.join(self.inputDirPath,"proteins",protein)
        print(protein_dir)
        create_folder(protein_dir)

        # Move to input folder so gmx detects forcefield and run pdb2gmx
        os.chdir(self.inputDirPath) 
        protein_Hpdb = os.path.join(protein_dir,"protGeom.pdb")
        command = ["gmx","pdb2gmx", "-f", protein_file, "-o", protein_Hpdb,
                "-p", os.path.join(protein_dir,"protTopol.top"),"-i",os.path.join(protein_dir,"protPosre.itp")]
        
        if manual:
            subprocess.run(command)
        else: 
            subprocess.run(command,input="1\n1",text=True)

        # Move back to cwd
        os.chdir(self.cwd)

        # Separate topology in .itp and .top
        self._splitTopol(protein_dir)
    
    def _splitTopol(self, protein_dir:str)->None:
        """
        Splits protein topology into separate.itp and.top files
        protein_dir :: relative path of protein folder
        """
        protTopolFile = os.path.join(protein_dir,"protTopol.top")
        with open(protTopolFile, 'r') as file:
            lines = file.readlines()

        # Find [ moleculetype ] line
        molTypeLine = [line for line in lines if line.startswith("[ moleculetype ]")]

        # Find ; Include water topology line
        includeWaterLine = [line for line in lines if line.startswith("; Include water topology")]
        
        # Split into itp and top files
        itpLines = lines[lines.index(molTypeLine[0]):lines.index(includeWaterLine[0])]
        itpLines.insert(0,"\n")
        # topLines = lines[lines.index(molTypeLine[0]):]

        itpFile = os.path.join(protein_dir,"protTopol.itp")
        # topFile = os.path.join(protein_dir,"prot.top")

        with open(itpFile, 'w') as file:
            for line in itpLines:
                file.write(line)


def read_input(f='input.yaml'):
    

    with open("input.yaml") as f:
        config = yaml.safe_load(f)


    # initialize the free energy environment object: it will store the main parameters for the calculations
    fe = AZtutorial(**config)

    fe.prepareAttributes() # don't comment

    return fe



def main(prot_list, lig_files=None, input_dir='input'):
    az = InputPreparations(input_dir) # Pass input folder name. Default is input
    az.defaultChargeType="default"
    lpath = f"{os.getcwd()}/ligands"
    az.ligand_files = [os.path.join(lpath, lig) for lig in lig_files]
    
    ppath = f"{os.getcwd()}/proteins"
    for prot in prot_list:
        az.protein_files.extend([f"{ppath}/{prot}/system.top", f"{ppath}/{prot}/system.gro", f"{ppath}/{prot}/toppar"]) # List of protein files 

    mpath = f"{os.getcwd()}/membrane" # path to the membrane
    az.membrane_files = [f"{mpath}/membrane.gro", f"{mpath}/membrane.top", f"{mpath}/toppar"] # List of membrane files (.gro)
    
    az.convertStrToPath() # Recomended. Transforms relative paths in ligand and protein files to absolute paths
    az.prepareInputDir() # 1. Generates folder structure
    
    az.genLigInputs(clean=True) # 2. Generates ligand inputs. clean=True (default) removes acpype folders after usage
    az.genProteinInputs() 
    az.genMembraneInputs()

    print("GROMACS input files for ligands generated.")


if __name__ == "__main__":
    fe = read_input()
    edges = []
    for edge in fe.edges:
        edges.append(fe.edges[edge])
    lig_files = [f'{i}.mol2' for i in np.unique(edges)]
    main(prot_list=[fe.proteinName], input_dir=fe.inputDirName, lig_files=lig_files)


