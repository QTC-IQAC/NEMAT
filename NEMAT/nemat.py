import pmx
from pmx.utils import create_folder
from pmx import gmx, ligand_alchemy, jobscript
import sys
import os,shutil
import re
import subprocess
import glob
import random
import pandas as pd
import numpy as np
from math import floor
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

class NEMAT:
    """Class contains parameters for setting up free energy calculations

    Parameters
    ----------
    ...

    Attributes
    ----------
    ....

    """

    def __init__(self, **kwargs):
        
        # set gmxlib path
        gmx.set_gmxlib()
        
        # the results are summarized in a pandas framework
        self.resultsAll = pd.DataFrame()
        self.resultsSummary = pd.DataFrame()
        self.precision = 3 # precision for the analysis
        
        # paths
        self._workPath = None
        self._mdpPath = None
        self._proteinPath = None
        self._ligandPath = None
        self._membranePath = None
        self._inputDirName = None
        self._proteinName = None
        
        # information about inputs
        self.protein = {} # protein[path]=path,protein[str]=pdb,protein[itp]=[itps],protein[posre]=[posres],protein[mols]=[molnames]
        self.ligands = {} # ligands[ligname]=path
        self.edges = {} # edges[edge_lig1_lig2] = [lig1,lig2]
        
        # parameters for the general setup
        self._replicas = None        
        self.simTypes = ['em','eq', 'md', 'transitions']
        self.states = ['stateA','stateB']
        self.thermCycleBranches = ['water','protein', 'membrane']
        self.frameNum = 80 # Number of frames to extract to make transitions
        self.maxDiff = 2.0 # maximum difference between the results of two replicas in kJ/mol
                
        # simulation setup
        self.ff = 'amber99sb-star-ildn-mut.ff'
        self.boxshape = 'dodecahedron'
        self.boxd = 1.5
        self.water = 'tip3p'
        self.conc = 0.15
        self.pname = 'NaJ'
        self.nname = 'ClJ'
        self.temp = 298 # temperature in K
        self.bootstrap = 100 # number of bootstrap samples
        
        # job submission params
        self.slotsToUse = None
        self.JOBqueue = 'SLURM' # could be SLURM
        self.JOBsimtime = "" # XX-XX:XX
        self.JOBsimcpu = 8 # CPU default
        self.JOBbGPU = True
        self.JOBmodules = []
        self.JOBsource = []
        self.JOBexport = []
        self.JOBcommands = []
        self.JOBgmx = 'gmx mdrun'
        self.JOBpartition = "long"
        self.JOBmpi = False
        self.JOBmem = '' # memory for the job
        self.JOBbackup = True # gromacs backup files



        for key, val in kwargs.items():
            setattr(self,key,val)
        
        # PREPARE AND CHANGE SOME ARGUMENTS

    @property
    def inputDirName(self):
        return self._inputDirName

    @inputDirName.setter
    def inputDirName(self, dir):
        cwd = os.getcwd()
        invalid = ['mdppath','proteins','ligands','membrane']
        if dir in invalid:
            raise ValueError(f"'{dir}' is not a valid input directory name. Invalid names are {invalid}")     
        elif dir == self.workPath:
            raise ValueError(f"'{dir}' is already the name of the workpath. Please choose another name.")

        self._inputDirName = f'{cwd}/{dir}'


    @property
    def workPath(self):
        return self._workPath

    @workPath.setter
    def workPath(self, dir):
        cwd = os.getcwd()
        invalid = ['mdppath','proteins','ligands','membrane']
        if dir in invalid:
            raise ValueError(f"'{dir}' is not a valid input directory name. Invalid names are {invalid}")     
        elif dir == self.inputDirName:
            raise ValueError(f"'{dir}' is already the name of the input directory. Please choose another name.")
        
        self._workPath = f'{cwd}/{dir}'

    @property
    def replicas(self):
        return self._replicas
    
    @replicas.setter
    def replicas(self, num):
        if num < 1:
            raise ValueError("Number of replicas must be greater than 0")
        if type(num) != int:
            raise TypeError("Number of replicas must be an integer.")
        
        self._replicas = num

    
    @property
    def proteinName(self):
        return self._proteinName
    
    @proteinName.setter
    def proteinName(self, name):
        prots = os.listdir(f'{os.getcwd()}/proteins')
        if name not in prots:
            raise ValueError(f"Please provide a protein that exists: {prots}")
        if not isinstance(name, str):
            raise TypeError("Protein name must be a string")
        
        self._proteinName = name

    @property
    def proteinPath(self):
        self._proteinPath = f'{self.inputDirName}/proteins/{self.proteinName}'
        return self._proteinPath
    
    @property
    def ligandPath(self):
        self._ligandPath = f'{self.inputDirName}/ligands'
        return self._ligandPath
    
    @property
    def membranePath(self):
        self._membranePath = f'{self.inputDirName}/membrane'
        return self._membranePath
 
    @property
    def mdpPath(self):
        self._mdpPath = f'{self.inputDirName}/mdppath'
        return self._mdpPath
        

    def prepareAttributes(self):
        """
        NEEDED AFTER DECLARATING VARIABLES AND BEFOR RUNNING ANY METHOD

        Updates paths to Path type and changes some variables
        """
        # protein={}
        # protein[path] = [path], protein[str] = pdb, protein[itp] = [itp], protein[posre] = [posre]
        # self.proteinPath = self._read_path( self.proteinPath )
        self._protein = self._read_protein()
        
        # read ligands
        # self.ligandPath = self._read_path( self.ligandPath )
        self._read_ligands()
        
        # read edges (directly or from a file)
        self._read_edges()
        print(self.edges,"From read edges")
        
        # read mdpPath
        # self.mdpPath = self._read_path( self.mdpPath )
        
        # workpath
        # self.workPath = self._read_path( self.workPath )


            
    def prepareFreeEnergyDir( self ):
        """
        Generates directory structure for the calculations
        """

        create_folder( self.workPath )
        
        # create folder structure
        self._create_folder_structure( )
        
        # print summary
        self._print_summary( )
                        
        # print folder structure
        self._print_folder_structure( )    
        
        print('DONE')
        
        
    # _functions to quickly get a path at different levels, e.g wppath, edgepath... like in _create_folder_structure
    def _get_specific_path( self, edge=None, bHybridStrTop=False, wp=None, state=None, r=None, sim=None ):
        """
        Finds specific route within the predetermined folder structure
        """
        if edge==None:
            return(self.workPath)       
        edgepath = '{0}/{1}'.format(self.workPath,edge)
        
        if bHybridStrTop==True:
            hybridStrPath = '{0}/hybridStrTop'.format(edgepath)
            return(hybridStrPath)

        if wp==None:
            return(edgepath)
        wppath = '{0}/{1}'.format(edgepath,wp)
        
        if state==None:
            return(wppath)
        statepath = '{0}/{1}'.format(wppath,state)
        
        if r==None:
            return(statepath)
        runpath = '{0}/run{1}'.format(statepath,r)
        
        if sim==None:
            return(runpath)
        simpath = '{0}/{1}'.format(runpath,sim)
        return(simpath)
                
    def _read_path( self, path ):
        """
        Generates absolute path form relative path
        """
        return(os.path.abspath(path))
        
    def _read_ligands( self ):
        """
        Updates .ligands property to dict
        """
        # read ligand folders
        ligs = glob.glob('{0}/*'.format(self.ligandPath))
        # get ligand names
        for l in ligs:
            lname = l.split('/')[-1]
            lnameTrunc = lname
            # if lname.startswith('lig_'): #
            #     lnameTrunc = lname[4:]
            # elif lname.startswith('lig'):
            #     lnameTrunc = lname[3:]
            lpath = '{0}/{1}'.format(self.ligandPath,lname)
            self.ligands[lnameTrunc] = os.path.abspath(lpath)
 
    def _read_protein( self ):
        """
        Updates .protein property to dict
        """
        # read protein folder
        self.protein['path'] = os.path.abspath(self.proteinPath)
        # get folder contents
        self.protein['posre'] = []
        self.protein['itp'] = []
        self.protein['mols'] = [] # mols to add to .top
        self.protein['str'] = ''
        for l in glob.glob('{0}/*'.format(self.proteinPath)):
            fname = l.split('/')[-1]
            if '.itp' in fname: # posre or top
                if 'posre' in fname.lower(): #
                    self.protein['posre'].append(os.path.abspath(l))
                else:
                    self.protein['itp'].append(os.path.abspath(l))
                    molTypes = self._getMolType(os.path.abspath(l))
                    self.protein["mols"].append(molTypes)
                    # if fname.startswith('topol_'): #
                    #     self.protein['mols'].append(fname[6:-4])
                    # else:
                    #     self.protein['mols'].append(fname[:-4])                        
            if '.pdb' in fname:
                self.protein['str'] = fname
        self.protein['mols'].sort()

    def _getMolType(self, itpFile): #
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

                
    def _read_edges( self ):
        """
        Updates.edges property to dict
        """
        # read from file
        try:
            if os.path.isfile( self.edges ):
                self._read_edges_from_file( self )
        # edge provided as an array
        except: 
            foo = {}
            for e in self.edges:
                key = 'edge_{0}_{1}'.format(e[0],e[1])
                foo[key] = e
            self.edges = foo
            
    def _read_edges_from_file( self ):
        """
        Indicates that edges are read from file
        """
        self.edges = 'Edges read from file'
        
        
    def _create_folder_structure( self, edges=None ):
        """
        Generates folder structure
        """
        # edge
        if edges==None:
            edges = self.edges      
        
        for edge in edges.keys():
            print(edge)            
            edgepath = '{0}/{1}'.format(self.workPath,edge)
            create_folder(edgepath)
            
            # folder for hybrid ligand structures
            hybridTopFolder = '{0}/hybridStrTop'.format(edgepath)
            create_folder(hybridTopFolder)
            
            # water/protein/membrane
            for wp in self.thermCycleBranches:
                wppath = '{0}/{1}'.format(edgepath,wp)
                create_folder(wppath)
                
                # stateA/stateB
                for state in self.states:
                    statepath = '{0}/{1}'.format(wppath,state)
                    create_folder(statepath)
                    
                    # run1/run2/run3
                    for r in range(1,self.replicas+1):
                        runpath = '{0}/run{1}'.format(statepath,r)
                        create_folder(runpath)
                        
                        # em/eq/md/transitions
                        for sim in self.simTypes:
                            simpath = '{0}/{1}'.format(runpath,sim)
                            create_folder(simpath)
                            
    def _print_summary( self ):
        """
        Prints the summary from the defined workspace. Indicates name of inputs, paths, etc.
        """
        print('\n---------------------\nSummary of the setup:\n---------------------\n')
        print('   workpath: {0}'.format(self.workPath))
        print('   mdp path: {0}'.format(self.mdpPath))
        print('   protein files: {0}'.format(self.proteinPath))
        print('   ligand files: {0}'.format(self.ligandPath))
        print('   membrane files: {0}'.format(self.membranePath))
        print('   number of replicase: {0}'.format(self.replicas))        
        print('   edges:')
        for e in self.edges.keys():
            print('        {0}'.format(e))    
            
    def _print_folder_structure( self ):
        """
        Prints the folder structure in a human-readable format.
        """
        print('\n---------------------\nDirectory structure:\n---------------------\n')
        print('{0}/'.format(self.workPath))
        print('|')
        print('|--edge_X_Y')
        print('|--|--water')
        print('|--|--|--stateA')
        print('|--|--|--|--run1/2/3')
        print('|--|--|--|--|--em/eq/md/transitions')
        print('|--|--|--stateB')
        print('|--|--|--|--run1/2/3')
        print('|--|--|--|--|--em/eq/md/transitions')
        print('|--|--membrane')
        print('|--|--|--stateA')
        print('|--|--|--|--run1/2/3')
        print('|--|--|--|--|--em/eq/md/transitions')
        print('|--|--|--stateB')
        print('|--|--|--|--run1/2/3')
        print('|--|--|--|--|--em/eq/md/transitions')
        print('|--|--protein')
        print('|--|--|--stateA')
        print('|--|--|--|--run1/2/3')
        print('|--|--|--|--|--em/eq/md/transitions')
        print('|--|--|--stateB')
        print('|--|--|--|--run1/2/3')
        print('|--|--|--|--|--em/eq/md/transitions')
        print('|--|--hybridStrTop')        
        print('|--edge_..')
        
    def _be_verbose( self, process, bVerbose=False ):
        out = process.communicate()            
        if bVerbose==True:
            printout = out[0].splitlines()
            for o in printout:
                print(o)
        # error is printed every time                  
        printerr = out[1].splitlines()                
        for e in printerr:
            print(e)              
        
    def atom_mapping( self, edges=None, bVerbose=False ):
        """
        Calls pmx atomMapping to perform a mapping between 2 ligands and returns overlapped geometry
        """
        print('-----------------------')
        print('Performing atom mapping')
        print('-----------------------')
        
        if edges==None:
            edges = self.edges        
        for edge in edges:
            print(edge)
            lig1 = self.edges[edge][0]
            lig2 = self.edges[edge][1]
            lig1path = '{0}/{1}'.format(self.ligandPath,lig1) #
            lig2path = '{0}/{1}'.format(self.ligandPath,lig2) #
            outpath = self._get_specific_path(edge=edge,bHybridStrTop=True)
            
            # params
            i1 = '{0}/ligGeom.pdb'.format(lig1path) #
            i2 = '{0}/ligGeom.pdb'.format(lig2path) #
            o1 = '{0}/pairs1.dat'.format(outpath)
            o2 = '{0}/pairs2.dat'.format(outpath)            
            opdb1 = '{0}/out_pdb1.pdb'.format(outpath)
            opdb2 = '{0}/out_pdb2.pdb'.format(outpath)
            opdbm1 = '{0}/out_pdbm1.pdb'.format(outpath)
            opdbm2 = '{0}/out_pdbm2.pdb'.format(outpath)
            score = '{0}/score.dat'.format(outpath)
            log = '{0}/mapping.log'.format(outpath)
            
            process = subprocess.Popen(['pmx','atomMapping',
                                '-i1',i1,
                                '-i2',i2,
                                '-o1',o1,
                                '-o2',o2,
                                '-opdb1',opdb1,
                                '-opdb2',opdb2,                                        
                                '-opdbm1',opdbm1,
                                '-opdbm2',opdbm2,
                                '-score',score,
                                '-log',log],
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)

            self._be_verbose( process, bVerbose=bVerbose )              
                
            process.wait()      
        print('DONE')            
            
            
    def hybrid_structure_topology( self, edges=None, bVerbose=False ):
        """
        Calls pmx ligandHybrid to create hybrid structure and topology. Returns topology.
        """
        print('----------------------------------')
        print('Creating hybrid structure/topology')
        print('----------------------------------')

        if edges==None:
            edges = self.edges        
        for edge in edges:
            print(edge)
            lig1 = self.edges[edge][0]
            lig2 = self.edges[edge][1]
            lig1path = '{0}/{1}'.format(self.ligandPath,lig1) #
            lig2path = '{0}/{1}'.format(self.ligandPath,lig2) #
            outpath = self._get_specific_path(edge=edge,bHybridStrTop=True)
            
            # params
            i1 = '{0}/ligGeom.pdb'.format(lig1path) #
            i2 = '{0}/ligGeom.pdb'.format(lig2path) #
            itp1 = '{0}/ligTopol.itp'.format(lig1path) #
            itp2 = '{0}/ligTopol.itp'.format(lig2path) #
            pairs = '{0}/pairs1.dat'.format(outpath)            
            oA = '{0}/mergedA.pdb'.format(outpath)
            oB = '{0}/mergedB.pdb'.format(outpath)
            oitp = '{0}/merged.itp'.format(outpath)
            offitp = '{0}/ffmerged.itp'.format(outpath)
            log = '{0}/hybrid.log'.format(outpath)
            
            process = subprocess.Popen(['pmx','ligandHybrid',
                                '-i1',i1,
                                '-i2',i2,
                                '-itp1',itp1,
                                '-itp2',itp2,
                                '-pairs',pairs,
                                '-oA',oA,  
                                '-oB',oB,
                                '-oitp',oitp,
                                '-offitp',offitp,
                                '-log',log],
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)

            self._be_verbose( process, bVerbose=bVerbose )                    
                
            process.wait()    
        print('DONE')
            
            
    def _make_clean_pdb(self, fnameIn,fnameOut,bAppend=False):
        """
        Generates a pdb with only atomic fields. Can append pdbs
        """
        # read 
        fp = open(fnameIn,'r')
        lines = fp.readlines()
        out = []
        for l in lines:
            if l.startswith('ATOM') or l.startswith('HETATM'):
                out.append(l)
        fp.close()
        
        # write
        if bAppend==True:
            fp = open(fnameOut,'a')
        else:
            fp = open(fnameOut,'w')
        for l in out:
            fp.write(l)
        fp.close()

    def assemble_systems(self, edges=None):
        # ALBERT: adding membrane to the system.

        red = "\033[31m"
        green = "\033[92m"
        end = "\033[0m"
        blink = '\033[5m'
        blue = '\033[34m'

        print('----------------------')
        print('Assembling the systems')
        print('----------------------')

        if edges==None:
            edges = self.edges

        for edge in edges:
            print(f'\n\t ---> {blue}{edge}{end}  <---\n')

            #######################
            #     LIG + WATER     #
            #######################

            lig1 = self.edges[edge][0]
            lig2 = self.edges[edge][1]
            lig1path = '{0}/{1}'.format(self.ligandPath,lig1)
            lig2path = '{0}/{1}'.format(self.ligandPath,lig2)
            outLigPath = self._get_specific_path(edge=edge,wp='water')
            hybridStrTopPath = self._get_specific_path(edge=edge,bHybridStrTop=True)                    

            # move mergedA.pdb file to the water folder which will be the initial.pdb
            self._make_clean_pdb('{0}/mergedA.pdb'.format(hybridStrTopPath),'{0}/init.pdb'.format(outLigPath))

            # Ligand topology
            # ffitp
            ffitpOut = '{0}/ffmerged.itp'.format(hybridStrTopPath)
            ffitpIn1 = '{0}/ligAtomTypes.itp'.format(lig1path)
            ffitpIn2 = '{0}/ligAtomTypes.itp'.format(lig2path)
            ffitpIn3 = '{0}/ffmerged.itp'.format(hybridStrTopPath)
            pmx.ligand_alchemy._merge_FF_files( ffitpOut, ffsIn=[ffitpIn1,ffitpIn2,ffitpIn3] )   
            
            # top
            ligTopFname = '{0}/topol.top'.format(outLigPath)
            ligFFitp = '{0}/ffmerged.itp'.format(hybridStrTopPath)
            ligItp ='{0}/merged.itp'.format(hybridStrTopPath)
            itps = [ligFFitp,ligItp]
            systemName = 'ligand in water'
            self._create_top(edge,fname=ligTopFname,itp=itps,systemName=systemName)



            #######################
            #    LIG + PROTEIN    #
            #######################

            outProtPath = self._get_specific_path(edge=edge,wp='protein')

            # Move system gro file to the protein folder
            shutil.copyfile('{0}/system.gro'.format(self.protein['path']),'{0}/system.gro'.format(outProtPath))

            # create a gro file of the ligand
            
            
            with open('{0}/mergedA.pdb'.format(hybridStrTopPath), 'r') as f:
                lines_lig = f.readlines()
                lines_lig = lines_lig[2:-1]

            gro_lines = []
            lig_coords = []
            for i,l in enumerate(lines_lig):
                l = l.split()
                gro_lines.append(f"{'1':>5}{l[3]:<5}{l[2]:>5}{i:>5}{float(l[6])/10:8.3f}{float(l[7])/10:8.3f}{float(l[8])/10:8.3f}\n")
                lig_coords.append([float(l[6])/10,float(l[7])/10,float(l[8])/10])
            
            # add the ligand to the protein gro file
            with open(f"{self.protein['path']}/system.gro", 'r') as f:
                lines = f.readlines()

            with open('{0}/system.gro'.format(outProtPath), 'w') as f:
                for l in lines:
                    if l == lines[1]:
                        f.write(f'{int(l)+len(gro_lines)}\n')
                    elif len(l.split()) == 9:
                        # add the ligand before the box line
                        for li in gro_lines:
                            f.write(li)
                        f.write(l)
                    else:
                        f.write(l)

            # protein topology
            protTopFname = '{0}/topol.top'.format(outProtPath)
            protTop = f"{self.protein['path']}/system.top"
            mols = []
            for m in self.protein['mols']:
                mols.append([m,1])
            mols.append(['MOL',1])
            systemName = 'Protein + Membrane + ligand system'

            # add the ligand to the topology
            self.create_prot_top(protTopFname, itps, mols, protTop, systemName)
            
            # create the tpr for the min run.
            mdpath = self.mdpPath
            tpr = '{0}/em.tpr'.format(outProtPath)
            gmx.grompp(f=f"{mdpath}/prot_em_l0.mdp", c=f"{outProtPath}/system.gro", p=f"{protTopFname}", o=f"{tpr}", maxwarn=1) #create the tpr for minimization. the warinig is sc-alpha != 0




            #######################
            #   LIG + MEMBRANE    #
            #######################

            outMembPath = self._get_specific_path(edge=edge,wp='membrane')

            # Move system gro file to the protein folder
            shutil.copyfile('{0}/membrane.gro'.format(self.membranePath),'{0}/membrane.gro'.format(outMembPath))

            # add the ligand to the membrane gro file
            with open(f"{outMembPath}/membrane.gro", 'r') as f:
                lines = f.readlines()

            with open(f"{outMembPath}/membrane.gro", 'w') as f:
                for l in lines:
                    if l == lines[1]:
                        f.write(f'{int(l)+len(gro_lines)}\n')
                    elif len(l.split()) == 9:
                        # get the centre of the box which will be inside the membrane
                        xb,yb,zb = l.split()[:3]
                        
                        # center of the box
                        xb = float(xb)/2
                        yb = float(yb)/2
                        zb = float(zb)/2

                        # lig gc
                        lig_gc = np.mean(lig_coords, axis=0) 

                        shift = np.array([xb, yb, zb]) - lig_gc

                        lig_coords_shifted = lig_coords + shift

                        gro_lines_shifted = []
                        for i,l_ in enumerate(lines_lig):
                            l_ = l_.split()
                            gro_lines_shifted.append(f"{'1':>5}{l_[3]:<5}{l_[2]:>5}{i:>5}{lig_coords_shifted[i][0]:8.3f}{lig_coords_shifted[i][1]:8.3f}{lig_coords_shifted[i][2]:8.3f}\n")

                        # add the ligand before the box line
                        for li in gro_lines_shifted:
                            f.write(li)
                        f.write(l)
                    else:
                        f.write(l)

            # membrane topology
            membOutTop = '{0}/topol.top'.format(outMembPath)
            membTop = f"{self.membranePath}/membrane.top"
            mols = []
            mols.append(['MOL',1])
            systemName = 'Membrane + ligand system'

            # add the ligand to the topology
            self.create_memb_top(membOutTop, itps, mols, membTop, systemName)

            # create the tpr for the min run.
            # mdpath = self.mdpPath
            # tpr = '{0}/em.tpr'.format(outMembPath)
            # gmx.grompp(f=f"{mdpath}/memb_em_l0.mdp", c=f"{outMembPath}/membrane.gro", p=f"{membOutTop}", o=f"{tpr}", maxwarn=1) #create the tpr for minimization. the warinig is sc-alpha != 0




    def create_prot_top(self, fname, lig_itps, mols, topol, sys_name):
        # ALBERT: creating the protein + ligand topology
        with open(topol, 'r') as ftop:
            lines = ftop.readlines()
        
        with open(fname, 'w') as fout:
            for line in lines:
                line = line.replace("toppar", f"{self.protein['path']}/toppar")
                line = line.replace("Title", sys_name)
                if 'forcefield.itp' in line:
                    fout.write(line)
                    for i in lig_itps:
                        fout.write(f'#include "{i}"\n')
                else:
                    fout.write(line)
            
            for mol in mols:
                fout.write('%s %s\n' %(mol[0],mol[1]))


    def create_memb_top(self, fname, lig_itps, mols, topol, sys_name):
        # ALBERT: creating the membrane + ligand topology
        
        simDir = os.getcwd()        

        with open(topol, 'r') as ftop:
            lines = ftop.readlines()
        
        with open(fname, 'w') as fout:
            for line in lines:
                line = line.replace("toppar", f"{self.membranePath}/toppar")
                line = line.replace("Title", sys_name)
                if 'forcefield.itp' in line:
                    fout.write(line)
                    for i in lig_itps:
                        fout.write(f'#include "{i}"\n')
                else:
                    fout.write(line)
            
            for mol in mols:
                fout.write('%s %s\n' %(mol[0],mol[1]))
            
            
    def _create_top( self, edge, fname='topol.top',  
                   itp=['merged.itp'], mols=[['MOL',1]],
                   systemName='simulation system',
                   destination='',toppaths=[]):
        """
        Creates a new topology file with the specified forcefield, additional itp, water, ions, and system.
        """

        fp = open(fname,'w')
        # ff itp
        fp.write('#include "%s/forcefield.itp"\n' % self.ff)
        
        # Add ligand parameters
        for lig in self.edges[edge]: #
            print(edge)
            ligpath = '{0}/{1}'.format(self.ligandPath,lig) #
            # Check if file exists
            paramFile = os.path.join(ligpath,"ligFFParams.prm")
            if not os.path.isfile(paramFile):
                print(f"Ligand parameter file {paramFile} not found. Not including it in topology.")
                continue
            else:
                fp.write(f'#include "{paramFile}"\n') 

        # additional itp
        for i in itp:
            fp.write('#include "%s"\n' % i) 
        # water itp
        fp.write('#include "%s/%s.itp"\n' % (self.ff,self.water)) 
        # ions
        fp.write('#include "%s/ions.itp"\n\n' % self.ff)
        # system
        fp.write('[ system ]\n')
        fp.write('{0}\n\n'.format(systemName))
        # molecules
        fp.write('[ molecules ]\n')
        for mol in mols:
            fp.write('%s %s\n' %(mol[0],mol[1]))
        fp.close()

        
    def _clean_backup_files( self, path ):
        """
        Remove gromacs backup files
        """
        toclean = glob.glob('{0}/*#'.format(path)) 
        for clean in toclean:
            os.remove(clean)        
    
    def boxWaterIons( self, edges=None, bBoxLig=True, bWatLig=True, bIonLig=True):
        """
        Add box, water, and ions to prot-Lig and Lig systems.
        """
        print('----------------')
        print('Box, water, ions')
        print('----------------')
        
        if edges==None:
            edges = self.edges
        print(edges,"--------------------")
        for edge in edges:
            print(edge)            
            outLigPath = self._get_specific_path(edge=edge,wp='water')
            outProtPath = self._get_specific_path(edge=edge,wp='protein')
            print(outLigPath,"--------------------")
            print(outProtPath,"--------------------")
            
            # box ligand
            if bBoxLig==True:
                inStr = '{0}/init.pdb'.format(outLigPath)
                outStr = '{0}/box.pdb'.format(outLigPath)
                gmx.editconf(inStr, o=outStr, bt=self.boxshape, d=self.boxd, other_flags='')                
            
                
            # water ligand
            if bWatLig==True:            
                inStr = '{0}/box.pdb'.format(outLigPath)
                outStr = '{0}/water.pdb'.format(outLigPath)
                top = '{0}/topol.top'.format(outLigPath)
                gmx.solvate(inStr, cs='spc216.gro', p=top, o=outStr)
           
            
            # ions ligand
            if bIonLig:
                inStr = '{0}/water.pdb'.format(outLigPath)
                outStr = '{0}/ions.pdb'.format(outLigPath)
                mdp = '{0}/lig_em_l0.mdp'.format(self.mdpPath)
                tpr = '{0}/tpr.tpr'.format(outLigPath)
                top = '{0}/topol.top'.format(outLigPath)
                mdout = '{0}/mdout.mdp'.format(outLigPath)
                gmx.grompp(f=mdp, c=inStr, p=top, o=tpr, maxwarn=1, other_flags=' -po {0}'.format(mdout))  # warning of sc-alpha != 0      
                gmx.genion(s=tpr, p=top, o=outStr, conc=self.conc, neutral=True, 
                      other_flags=' -pname {0} -nname {1}'.format(self.pname, self.nname))
            
            # clean backed files
            self._clean_backup_files( outLigPath )

        print('DONE')

    def _prepare_prot_tpr(self, simpath, toppath, state, simType, empath=None, eqpath=None, frameNum=0, extra_flag=None):
        # ALBERT: protein tpr file generation.
        mdpPrefix = ''
        if simType=='em':
            mdpPrefix = 'em'
        elif simType=='eq':
            mdpPrefix = 'eq'
        elif simType=='md':
            mdpPrefix = 'md'
        elif simType=='transitions':
            mdpPrefix = 'ti'

        if extra_flag is not None:
            mdpPrefix = "_".join([mdpPrefix,extra_flag])

        top = '{0}/topol.top'.format(toppath)
        tpr = '{0}/{1}.tpr'.format(simpath, simType)
        
        # mdp
        if state=='stateA':
            if mdpPrefix=='eq':
                
                mdp = f'{self.mdpPath}/prot_eq1_l0.mdp'
                tpr = f'{simpath}/{mdpPrefix}1.tpr'
                ingro = f'{empath}/em.gro'
                
                subprocess.run(f"printf '1 | 19\n name 20 SOLU\n 13 | 14 | 15\n name 21 MEMB\n 16 | 17 | 18\n name 22 SOLV\n 20 | 21\n name 23 SOLU_MEMB\n q\n' | gmx make_ndx -f {ingro} -o {simpath}/index.ndx", shell=True)
                gmx.grompp(f=mdp, c=ingro, p=top, o=tpr, maxwarn=1, other_flags=f' -n {simpath}/index.ndx') # warning of sc-alpha != 0
            
            else:
                mdp = f'{self.mdpPath}/prot_{mdpPrefix}_l0.mdp'
                # str
                if simType=='em':
                    ingro = '{0}/system.gro'.format(toppath)
                elif simType=='md':
                    ingro = '{0}/eq6.gro'.format(eqpath)
                elif simType=='transitions':
                    ingro = '{0}/frame{1}.gro'.format(simpath,frameNum)
                    tpr = '{0}/ti{1}.tpr'.format(simpath,frameNum)
                
                subprocess.run(f"printf '1 | 19\n name 20 SOLU\n 13 | 14 | 15\n name 21 MEMB\n 16 | 17 | 18\n name 22 SOLV\n 20 | 21\n name 23 SOLU_MEMB\n q\n' | gmx make_ndx -f {ingro} -o {simpath}/index.ndx", shell=True)
                gmx.grompp(f=mdp, c=ingro, p=top, o=tpr, maxwarn=1, other_flags=f' -n {simpath}/index.ndx') # warning of sc-alpha != 0

        else:
            if mdpPrefix=='eq':

                mdp = f'{self.mdpPath}/prot_eq1_l1.mdp'
                tpr = f'{simpath}/{mdpPrefix}1.tpr'
                ingro = f'{empath}/em.gro'
                subprocess.run(f"printf '1 | 19\n name 20 SOLU\n 13 | 14 | 15\n name 21 MEMB\n 16 | 17 | 18\n name 22 SOLV\n 20 | 21\n name 23 SOLU_MEMB\n q\n' | gmx make_ndx -f {ingro} -o {simpath}/index.ndx", shell=True)
                gmx.grompp(f=mdp, c=ingro, p=top, o=tpr, maxwarn=1, other_flags=f' -n {simpath}/index.ndx') # warning of sc-alpha != 0
        
            else:
                mdp = f'{self.mdpPath}/prot_{mdpPrefix}_l1.mdp'
                # str
                if simType=='em':
                    ingro = '{0}/system.gro'.format(toppath)
                elif simType=='md':
                    ingro = '{0}/eq6.gro'.format(eqpath)
                elif simType=='transitions':
                    ingro = '{0}/frame{1}.gro'.format(simpath,frameNum)
                    tpr = '{0}/ti{1}.tpr'.format(simpath,frameNum)
                subprocess.run(f"printf '1 | 19\n name 20 SOLU\n 13 | 14 | 15\n name 21 MEMB\n 16 | 17 | 18\n name 22 SOLV\n 20 | 21\n name 23 SOLU_MEMB\n q\n' | gmx make_ndx -f {ingro} -o {simpath}/index.ndx", shell=True)
                gmx.grompp(f=mdp, c=ingro, p=top, o=tpr, maxwarn=1, other_flags=f' -n {simpath}/index.ndx') # warning of sc-alpha != 0
        
        self._clean_backup_files( simpath )
            

    def _prepare_memb_tpr(self, simpath, toppath, state, simType, empath=None, eqpath=None, frameNum=0, extra_flag=None):
        # ALBERT: membrane tpr file generation.
        mdpPrefix = ''
        if simType=='em':
            mdpPrefix = 'em'
        elif simType=='eq':
            mdpPrefix = 'eq'
        elif simType=='md':
            mdpPrefix = 'md'
        elif simType=='transitions':
            mdpPrefix = 'ti'

        if extra_flag is not None:
            mdpPrefix = "_".join([mdpPrefix,extra_flag])

        top = '{0}/topol.top'.format(toppath)
        tpr = '{0}/{1}.tpr'.format(simpath, simType)
        
        # mdp
        if state=='stateA':
            if mdpPrefix=='eq':
                
                mdp = f'{self.mdpPath}/memb_eq1_l0.mdp'
                tpr = f'{simpath}/{mdpPrefix}1.tpr'
                ingro = f'{empath}/em.gro'
                
                subprocess.run(f"printf 'name 8 LIG\n 2 | 3 | 4\n name 9 MEMB\n 5 | 6 | 7\n name 10 SOLV\n 8 | 9\n name 11 SOLU_MEMB\n q\n' | gmx make_ndx -f {ingro} -o {simpath}/index.ndx", shell=True)
                gmx.grompp(f=mdp, c=ingro, p=top, o=tpr, maxwarn=1, other_flags=f' -n {simpath}/index.ndx') # warning of sc-alpha != 0
            
            else:
                mdp = f'{self.mdpPath}/memb_{mdpPrefix}_l0.mdp'
                # str
                if simType=='em':
                    ingro = '{0}/membrane.gro'.format(toppath)
                elif simType=='md':
                    ingro = '{0}/eq6.gro'.format(eqpath)
                elif simType=='transitions':
                    ingro = '{0}/frame{1}.gro'.format(simpath,frameNum)
                    tpr = '{0}/ti{1}.tpr'.format(simpath,frameNum)
                
                subprocess.run(f"printf 'name 8 LIG\n 2 | 3 | 4\n name 9 MEMB\n 5 | 6 | 7\n name 10 SOLV\n 8 | 9\n name 11 SOLU_MEMB\n q\n' | gmx make_ndx -f {ingro} -o {simpath}/index.ndx", shell=True)
                gmx.grompp(f=mdp, c=ingro, p=top, o=tpr, maxwarn=1, other_flags=f' -n {simpath}/index.ndx') # warning of sc-alpha != 0

        else:
            if mdpPrefix=='eq':

                mdp = f'{self.mdpPath}/memb_eq1_l1.mdp'
                tpr = f'{simpath}/{mdpPrefix}1.tpr'
                ingro = f'{empath}/em.gro'
                subprocess.run(f"printf 'name 8 LIG\n 2 | 3 | 4\n name 9 MEMB\n 5 | 6 | 7\n name 10 SOLV\n 8 | 9\n name 11 SOLU_MEMB\n q\n' | gmx make_ndx -f {ingro} -o {simpath}/index.ndx", shell=True)
                gmx.grompp(f=mdp, c=ingro, p=top, o=tpr, maxwarn=1, other_flags=f' -n {simpath}/index.ndx') # warning of sc-alpha != 0
        
            else:
                mdp = f'{self.mdpPath}/memb_{mdpPrefix}_l1.mdp'
                # str
                if simType=='em':
                    ingro = '{0}/membrane.gro'.format(toppath)
                elif simType=='md':
                    ingro = '{0}/eq6.gro'.format(eqpath)
                elif simType=='transitions':
                    ingro = '{0}/frame{1}.gro'.format(simpath,frameNum)
                    tpr = '{0}/ti{1}.tpr'.format(simpath,frameNum)
                subprocess.run(f"printf 'name 8 LIG\n 2 | 3 | 4\n name 9 MEMB\n 5 | 6 | 7\n name 10 SOLV\n 8 | 9\n name 11 SOLU_MEMB\n q\n' | gmx make_ndx -f {ingro} -o {simpath}/index.ndx", shell=True)
                gmx.grompp(f=mdp, c=ingro, p=top, o=tpr, maxwarn=1, other_flags=f' -n {simpath}/index.ndx') # warning of sc-alpha != 0
        
        self._clean_backup_files( simpath )
            

    def _prepare_single_tpr( self, simpath, toppath, state, simType, empath=None, nvtpath=None, frameNum=0,extra_flag=None):
        """
        Generate .tpr files for different simulations types
        """
        mdpPrefix = ''
        if simType=='em':
            mdpPrefix = 'em'
        elif simType=='eq': # added
            mdpPrefix = 'eq'
        elif simType=='md':
            mdpPrefix = 'md'
        elif simType=='transitions':
            mdpPrefix = 'ti'

        if extra_flag is not None:
            mdpPrefix = "_".join([mdpPrefix,extra_flag])

        top = '{0}/topol.top'.format(toppath)
        tpr = '{0}/tpr.tpr'.format(simpath)
        mdout = '{0}/mdout.mdp'.format(simpath)
        # mdp
        if state=='stateA':
            mdp = '{0}/lig_{1}_l0.mdp'.format(self.mdpPath,mdpPrefix)
        else:
            mdp = '{0}/lig_{1}_l1.mdp'.format(self.mdpPath,mdpPrefix)
        # str
        if simType=='em':
            inStr = '{0}/ions.pdb'.format(toppath)
        elif simType=='eq':
            inStr = '{0}/confout.gro'.format(empath)
        elif simType=='md':
            inStr = '{0}/confout.gro'.format(nvtpath)
        elif simType=='transitions':
            inStr = '{0}/frame{1}.gro'.format(simpath,frameNum)
            tpr = '{0}/ti{1}.tpr'.format(simpath,frameNum)

        gmx.grompp(f=mdp, c=inStr, p=top, o=tpr, maxwarn=1, other_flags=' -po {0}'.format(mdout))
        self._clean_backup_files( simpath )

    def prepare_simulation( self, edges=None, simType='em', bLig=True, bProt=True, bMemb=True, extra_flag=None):
        # ALBERT: changing the tpr creation for the protein and ligand separately.

        """
        Prepare tpr files for simulation. 
        """

        red = "\033[31m"
        green = "\033[92m"
        end = "\033[0m"
        blink = '\033[5m'
        blue = '\033[34m'

        print('-----------------------------------------')
        print('Preparing simulation: {0}'.format(simType))
        print('-----------------------------------------')
        
        if edges==None:
            edges = self.edges

        for edge in edges:
            print(f'\n\t ---> {blue}{edge}{end}  <---\n')
            ligTopPath = self._get_specific_path(edge=edge,wp='water')
            protTopPath = self._get_specific_path(edge=edge,wp='protein')
            membTopPath = self._get_specific_path(edge=edge,wp='membrane')   

            for state in self.states:
                for r in range(1,self.replicas+1):
                    
                    # ligand
                    if bLig==True:
                        wp = 'water'
                        simpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim=simType)
                        eqpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='eq')
                        empath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='em')
                        toppath = ligTopPath
                        self._prepare_single_tpr( simpath, toppath, state, simType, empath, eqpath, extra_flag=extra_flag)
                    
                    # protein
                    if bProt==True:
                        wp = 'protein'
                        simpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim=simType)
                        eqpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='eq')
                        empath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='em')
                        toppath = protTopPath # Should be protTopPath (?)
                        self._prepare_prot_tpr(simpath, toppath, state, simType, empath, eqpath, extra_flag=extra_flag )

                    # membrane
                    if bMemb==True:
                        wp = 'membrane'
                        simpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim=simType)
                        eqpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='eq')
                        empath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='em')
                        toppath = membTopPath # Should be protTopPath (?)
                        self._prepare_memb_tpr(simpath, toppath, state, simType, empath, eqpath, extra_flag=extra_flag )
 
 
        print('DONE')
                    
        

    def _run_mdrun( self, tpr=None, ener=None, confout=None, mdlog=None, 
                    cpo=None, trr=None, xtc=None, dhdl=None, bVerbose=False):
        """
        Run gmx mdrun command locally
        """
        # EM
        if xtc==None:
            process = subprocess.Popen(['gmx','mdrun',
                                '-s',tpr,
                                '-e',ener,
                                '-c',confout,
                                '-o',trr,                                        
                                '-g',mdlog,
                                '-dhdl',dhdl],
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
            self._be_verbose( process, bVerbose=bVerbose )                    
            process.wait()           
        # other FE runs
        else:
            process = subprocess.Popen(['gmx','mdrun',
                                '-s',tpr,
                                '-e',ener,
                                '-c',confout,
                                '-x',xtc,
                                '-o',trr,
                                '-cpo',cpo,                                        
                                '-g',mdlog,
                                '-dhdl',dhdl],
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
            self._be_verbose( process, bVerbose=bVerbose )                    
            process.wait()           
    

    def prepare_jobscripts( self, edges=None, simType='em', bLig=True, bProt=True, bMemb=True):
        # ALBERT: change for the protein job preparation while ligand stays the same.
        print('---------------------------------------------')
        print('Preparing jobscripts for: {0}'.format(simType))
        print('---------------------------------------------')
        
        jobfolder = '{0}/{1}_jobscripts'.format(self.workPath,simType)
        try:
            os.mkdir('{0}'.format(jobfolder))
        except FileExistsError:
            print('Directory {0} already exists'.format(jobfolder))
            pass
        
        if edges==None:
            edges = self.edges
            
        counter = 0
        for edge in edges:
            
            for state in self.states:
                for r in range(1,self.replicas+1):            
                    
                    # ligand
                    if bLig==True:
                        wp = 'water'
                        simpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim=simType)
                        jobfile = '{0}/jobscript{1}'.format(jobfolder,counter)
                        jobname = 'lig_{0}_{1}_{2}_{3}'.format(edge,state,r,simType)
                        job = pmx.jobscript.Jobscript(fname=jobfile,
                                        queue=self.JOBqueue,simcpu=self.JOBsimcpu,
                                        jobname=jobname,modules=self.JOBmodules,source=self.JOBsource,
                                        gmx=self.JOBgmx,partition=self.JOBpartition, mem=self.JOBmem)
                        
                        job.cmds = ['rm -f *tpr *trr *xtc *edr *log *xvg \#*']
                        if len(self.JOBexport) > 0:
                            for exp in self.JOBexport:
                                job.cmds.append(f'export {exp}\n')
                        if len(self.JOBsource) > 0:
                            for s in self.JOBsource:
                                job.cmds.append(f'source {s}\n')
                                            
                        if simType=='transitions':
                            self._commands_for_transitions( simpath, job )
                            print(f"NOTE: SimType is transition, cleaning backup files in {simpath}") #
                            self._clean_backup_files(simpath) #: clean backup files, just in case
                        else:
                            cmd1 = 'cd {0}'.format(simpath)
                            cmd2 = '$GMXRUN -s tpr.tpr'
                            job.cmds += [cmd1,cmd2]  
                        
                        job.create_jobscript()                        
                        counter+=1

                    # protein
                    if bProt==True:
                        wp = 'protein'
                        self.jobscripts_membrane(wp, edge, jobfolder, state, r, counter, simType)
                        self.jobscripts_cpt(wp, edge, jobfolder, state, r, counter)
                        counter += 1
                    # membrane
                    if bMemb==True:
                        wp = 'membrane'
                        self.jobscripts_membrane(wp, edge, jobfolder, state, r, counter, simType)
                        counter += 1
                    
        #######
        self._submission_script( jobfolder, counter, simType )
        print('DONE')


    def jobscripts_membrane( self, wp, edge, jobfolder, state, r, counter, simType='em'):
        simpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim=simType)
        jobfile = '{0}/jobscript{1}'.format(jobfolder,counter)
        jobname = 'prot_{0}_{1}_{2}_{3}'.format(edge,state,r,simType)
        job = pmx.jobscript.Jobscript(fname=jobfile,
                        queue=self.JOBqueue,simcpu=self.JOBsimcpu,
                        jobname=jobname,modules=self.JOBmodules,source=self.JOBsource,
                        gmx=self.JOBgmx,partition=self.JOBpartition, mem=self.JOBmem)
        
        job.cmds = ['rm -f *tpr *trr *xtc *edr *log *xvg \#*']
        if len(self.JOBexport) > 0:
            for exp in self.JOBexport:
                job.cmds.append(f'export {exp}\n')
        if len(self.JOBsource) > 0:
            for s in self.JOBsource:
                job.cmds.append(f'source {s}\n')
        
        cmd1 = 'cd {0}'.format(simpath)
        if simType == 'em':
            cmd2 = '$GMXRUN -deffnm em'
            job.cmds += [cmd1,cmd2]

        elif simType == 'eq':
                job.cmds = [cmd1, '$GMXRUN -deffnm eq1']
                for i in range(2,7):
                    if wp == 'protein':
                        if state == 'stateA':
                            mdp = f'{self.mdpPath}/prot_eq{i}_l0.mdp'
                        else:
                            mdp = f'{self.mdpPath}/prot_eq{i}_l1.mdp'
                    else:
                        if state == 'stateA':
                            mdp = f'{self.mdpPath}/memb_eq{i}_l0.mdp'
                        else: 
                            mdp = f'{self.mdpPath}/memb_eq{i}_l1.mdp'
                
                    tpr = f'{simpath}/eq{i}.tpr'
                    ingro = f'{simpath}/eq{i-1}.gro'
                    top = f"{self._get_specific_path(edge=edge,wp=wp)}/topol.top"
                    job.cmds.append(f'gmx grompp -f {mdp} -c {ingro} -r {ingro} -p {top} -o {tpr} -maxwarn 2 -n {simpath}/index.ndx') # 2 warnings: sc-alpha != 0
                    job.cmds.append(f'$GMXRUN -deffnm eq{i}')
        elif simType == 'md':
            cmd2 = '$GMXRUN -deffnm md'
            job.cmds += [cmd1,cmd2]
            
        elif simType=='transitions':
            self._commands_for_transitions( simpath, job )
            print(f"NOTE: SimType is transition, cleaning backup files in {simpath}") #
            self._clean_backup_files(simpath) #: clean backup files, just in case                        
        job.create_jobscript()

    def jobscripts_cpt(self, wp, edge, jobfolder, state, r, counter):
        simpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='md')
        jobfile = '{0}/jobscript_cp{1}'.format(jobfolder,counter)
        jobname = 'prot_{0}_{1}_{2}_{3}'.format(edge,state,r,'md')
        job = pmx.jobscript.Jobscript(fname=jobfile,
                        queue=self.JOBqueue,simcpu=self.JOBsimcpu,
                        jobname=jobname,modules=self.JOBmodules,source=self.JOBsource,
                        gmx=self.JOBgmx,partition=self.JOBpartition, mem=self.JOBmem)
        
        job.cmds = []
        if len(self.JOBexport) > 0:
            for exp in self.JOBexport:
                job.cmds.append(f'export {exp}\n')
        if len(self.JOBsource) > 0:
            for s in self.JOBsource:
                job.cmds.append(f'source {s}\n')
        
        cmd1 = 'cd {0}'.format(simpath)
        cmd2 = '$GMXRUN -deffnm md -cpi md.cpt'
        job.cmds += [cmd1,cmd2]

        job.create_jobscript()
        
    def _commands_for_transitions( self, simpath, job ):
        """
        Define commands for scripts fortransitions simulations
        """
        if self.JOBqueue=='SGE':
            for i in range(1,self.frameNum+1):
                if self.JOBbackup:
                    cmd0 = f'export GMX_MAXBACKUP={self.frameNum + 10}' # add 10 just in case
                else:
                    cmd0 = 'export GMX_MAXBACKUP=-1'
                cmd1 = 'cd $TMPDIR'
                cmd2 = 'cp {0}/ti$SGE_TASK_ID.tpr tpr.tpr'.format(simpath)
                cmd3 = '$GMXRUN -s tpr.tpr -dhdl dhdl$SGE_TASK_ID.xvg'.format(simpath)
                cmd4 = 'cp dhdl$SGE_TASK_ID.xvg {0}/.'.format(simpath)
                job.cmds += [cmd0,cmd1,cmd2,cmd3,cmd4]
        elif self.JOBqueue=='SLURM':
            if self.JOBbackup:
                cmd0 = f'export GMX_MAXBACKUP={self.frameNum + 10}' # add 10 just in case
            else:
                cmd0 = 'export GMX_MAXBACKUP=-1'
            cmd1 = 'cd {0}'.format(simpath)
            cmd2 = f'for i in {{1..{self.frameNum}}};do' 
            cmd3 = '$GMXRUN -s ti$i.tpr -dhdl dhdl$i'
            cmd4 = 'done'
            # cmd5 = '\ntar -czvf frames.tar.gz *.gro' # compress all .gro files
            # cmd6 = 'rm -f \#*'
            job.cmds += [cmd0,cmd1,cmd2,cmd3,cmd4]
   
   
        
    def _submission_script( self, jobfolder, counter, simType='eq' ):
        # ALBERT; efficient job submission if you only want to use slotsToUse gpus.
        """
        Submission script

        slotsToUse :: number of nodes to have running at once
        """
        if self.slotsToUse is not None:
            print(f"Will run {self.slotsToUse} jobs max at the same time") 
        
        fname = '{0}/submit_jobs.sh'.format(jobfolder)
        fp = open(fname,'w')
        fp.write('#!/bin/bash\n')
        fp.write(f'#SBATCH --job-name=NEMAT_{simType}\n')
        fp.write(f'#SBATCH --output=job_%A_%a.out\n')
        fp.write(f'#SBATCH --partition={self.JOBpartition}\n')
        fp.write(f'#SBATCH --gres=gpu:1\n')
        fp.write(f'#SBATCH -N 1\n')
        fp.write(f'#SBATCH -n {self.JOBsimcpu}\n')
        fp.write(f'#SBATCH -c 1\n')
        if self.JOBmem != '':
            fp.write(f'#SBATCH --mem={self.JOBmem}\n')
        if self.JOBsimtime != '':
            fp.write(f'#SBATCH -t {self.JOBsimtime}\n')
        if self.slotsToUse is not None:
            fp.write(f'#SBATCH --array=1-{counter}%{self.slotsToUse}\n\n')
        else:
            fp.write(f'#SBATCH --array=1-{counter}\n\n')
        
        if len(self.JOBexport) > 0:
            for exp in self.JOBexport:
                fp.write(f'export {exp}\n')
            fp.write('\n')
        if len(self.JOBsource) > 0:
            for s in self.JOBsource:
                fp.write(f'source {s}\n')
            fp.write('\n')

        fp.write('case $SLURM_ARRAY_TASK_ID in\n')

        job_type = 0
        cp_files = []
        for i in range(0,counter):
            if job_type == 0:
                comm = '# Water'
                job_type = 1
            elif job_type == 1:
                comm = '# Protein'
                cp_files.append(i)
                job_type = 2
            elif job_type == 2:
                comm = '# Membrane'
                job_type = 0

            fp.write(f'  {i+1}) ./jobscript{i} ;; {comm}\n') 
        
        fp.write('esac\n')
        fp.close()

        subprocess.run(f'chmod 777 {jobfolder}/jobscript*', shell=True)


        # cpt submiting script to the job folder
        fname = '{0}/submit_jobs_cpt.sh'.format(jobfolder)
        fp = open(fname,'w')
        fp.write('#!/bin/bash\n')
        fp.write(f'#SBATCH --job-name=NEMAT_md_cpt\n')
        fp.write(f'#SBATCH --output=job_%A_%a.out\n')
        fp.write(f'#SBATCH --partition={self.JOBpartition}\n')
        fp.write(f'#SBATCH --gres=gpu:1\n')
        fp.write(f'#SBATCH -N 1\n')
        fp.write(f'#SBATCH -n {self.JOBsimcpu}\n')
        fp.write(f'#SBATCH -c 1\n')
        if self.JOBmem != '':
            fp.write(f'#SBATCH --mem={self.JOBmem}\n')
        if self.JOBsimtime != '':
            fp.write(f'#SBATCH -t {self.JOBsimtime}\n')
        if self.slotsToUse is not None:
            fp.write(f'#SBATCH --array=1-{len(cp_files)}%{self.slotsToUse}\n\n')
        else:
            fp.write(f'#SBATCH --array=1-{len(cp_files)}\n\n')
        
        if len(self.JOBexport) > 0:
            for exp in self.JOBexport:
                fp.write(f'export {exp}\n')
            fp.write('\n')
        if len(self.JOBsource) > 0:
            for s in self.JOBsource:
                fp.write(f'source {s}\n')
            fp.write('\n')

        fp.write('case $SLURM_ARRAY_TASK_ID in\n')
        for i in range(len(cp_files)):
            fp.write(f'  {i+1}) ./jobscript_cp{cp_files[i]} ;; # Protein cpt\n')
        
        fp.write('esac\n')
        fp.close()

        if not self.JOBmpi:
            subprocess.run(f"""for file in {jobfolder}/jobscript*; do sed -i 's/-ntmpi 1//g' "$file"; done""", shell=True)


    def _extract_snapshots_prot(self, mdpath, tipath):
        """
        Extract snapshots from trajectory files. Necessary for alchemical transitions
        """
        tpr = '{0}/md.tpr'.format(mdpath)
        xtc = '{0}/md.xtc'.format(mdpath)
        frame = '{0}/frame.gro'.format(tipath)
        start_time_flag = f" -b {self.tstart}" # avoids the first frame which is the closest to the equilibration

        if not os.path.exists(f'{tipath}/frame{self.frameNum}.gro'):
            gmx.trjconv(s=tpr,f=xtc,o=frame, sep=True, ur='compact', pbc='mol', other_flags=start_time_flag)
            cmd = f'mv {tipath}/frame0.gro {tipath}/frame{self.frameNum}.gro'
            os.system(cmd)
        else:
            print('Frames already extracted')
        
        self._clean_backup_files( tipath )

    def _extract_snapshots( self, eqpath, tipath ):
        """
        Extract snapshots from trajectory files. Necessary for alchemical transitions
        """
        tpr = '{0}/tpr.tpr'.format(eqpath)
        xtc = '{0}/traj_comp.xtc'.format(eqpath)
        frame = '{0}/frame.gro'.format(tipath)
        start_time_flag = f" -b {self.tstart}"
        
        if not os.path.exists(f'{tipath}/frame{self.frameNum}.gro'):
            gmx.trjconv(s=tpr,f=xtc,o=frame, sep=True, ur='compact', pbc='mol', other_flags=start_time_flag)
            cmd = f'mv {tipath}/frame0.gro {tipath}/frame{self.frameNum}.gro'
            os.system(cmd)
        else:
            print('Frames already extracted')
        
        self._clean_backup_files( tipath )

    def _prepareExtractionTime(self,extra_flag=None): 
        #ALBERT: changes to work with xtc 
        """
        Reads eq simulation mdp file to determine the time from which to start extracting
        frames to obtain the desired number of frames (self.frameNum)
        """

        if extra_flag is not None:
            mdp = f'{self.mdpPath}/lig_md_{extra_flag}_l0.mdp'
        else:
            mdp = f'{self.mdpPath}/lig_md_l0.mdp'

        with open(mdp, 'r') as f:
            lines = f.readlines()

        # Extract 3 thing: i) total step number ii) dt (in ps) iii) nstxout
        for line in lines:
            if "nsteps" in line: 
                nsteps = int(line.split("=")[-1].split(";")[0])
            
            elif "dt" in line:
                dt = float(line.split("=")[-1].split(";")[0])
                
            elif 'nstxout-compressed ' in line:
                nstxout = int(line.split("=")[-1].split(";")[0])
        
        self.totalSimTime = dt*nsteps
        self.timePerStep = dt*nstxout
        self.tstart = self.totalSimTime - self.timePerStep * self.frameNum
        print(f"Total simulation time: {self.totalSimTime} ps")
        print(f"Time per step: {self.timePerStep} ps")
        print(f"Initial extraction time: {self.tstart} ps")


        if self.tstart < 0:
            print("WARNING: too many steps to extract from simulation. Modify the mdp and redo the production")

            self.tstart = 0 # To remove equilibration 
            self.frameNum = floor((self.totalSimTime - self.tstart)/self.timePerStep)
            print(f"WARNING: defaulting to tstart = 0 --> New frame number = {self.frameNum}")
        
        
    def prepare_transitions(self, edges=None, bLig=True, bProt=True, bMemb=True, bGenTpr=True,extra_flag_extractTime=None, extra_flag_sim=None ):
        """
        Prepare transitions tprs. Since it is long, use sbatch if possible.
        """
        print('---------------------')
        print('Preparing transitions')
        print('---------------------')

        self._prepareExtractionTime(extra_flag=extra_flag_extractTime)
        self.tstart = 0
        if edges==None:
            edges = self.edges
        for edge in edges:
            ligTopPath = self._get_specific_path(edge=edge,wp='water')
            protTopPath = self._get_specific_path(edge=edge,wp='protein')
            membTopPath = self._get_specific_path(edge=edge,wp='membrane')            
            
            for state in self.states:
                for r in range(1,self.replicas+1):
                    
                    # ligand
                    if bLig==True:
                        print('Preparing: LIG {0} {1} run{2}'.format(edge,state,r))
                        wp = 'water'
                        mdpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='md')
                        tipath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='transitions')
                        toppath = ligTopPath
                        self._extract_snapshots( mdpath, tipath )
                        if bGenTpr==True:
                            for i in range(1,self.frameNum+1):
                                self._prepare_single_tpr( tipath, toppath, state, simType='transitions',frameNum=i,extra_flag=extra_flag_sim )
                    
                    # protein
                    if bProt==True:
                        print('Preparing: PROT {0} {1} run{2}'.format(edge,state,r))
                        wp = 'protein'
                        mdpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='md')
                        tipath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='transitions')                        
                        toppath = protTopPath
                        self._extract_snapshots_prot( mdpath, tipath )
                        if bGenTpr==True:
                            for i in range(1,self.frameNum+1):
                                self._prepare_prot_tpr( tipath, toppath, state, simType='transitions',frameNum=i,extra_flag=extra_flag_sim )

                    if bProt==True:
                        print('Preparing: MEMB {0} {1} run{2}'.format(edge,state,r))
                        wp = 'membrane'
                        mdpath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='md')
                        tipath = self._get_specific_path(edge=edge,wp=wp,state=state,r=r,sim='transitions')                        
                        toppath = membTopPath
                        self._extract_snapshots_prot( mdpath, tipath )
                        if bGenTpr==True:
                            for i in range(1,self.frameNum+1):
                                self._prepare_memb_tpr( tipath, toppath, state, simType='transitions',frameNum=i,extra_flag=extra_flag_sim )
        
        
        print('DONE')  
      
    
    def _run_analysis_script( self, analysispath, stateApath, stateBpath, bVerbose=False ):
        """
        Call pmx analyse to analyse results 
        """
        fA = ' '.join( glob.glob('{0}/dhdl*xvg'.format(stateApath)) )
        fB = ' '.join( glob.glob('{0}/dhdl*xvg'.format(stateBpath)) )
        oA = '{0}/integ0.dat'.format(analysispath)
        oB = '{0}/integ1.dat'.format(analysispath)
        wplot = '{0}/wplot.png'.format(analysispath)
        o = '{0}/results.txt'.format(analysispath)

        cmd = 'pmx analyse -fA {0} -fB {1} -o {2} -oA {3} -oB {4} -w {5} -t {6} -b {7}'.format(\
                                                                            fA,fB,o,oA,oB,wplot,self.temp,self.bootstrap) 
        os.system(cmd)
        
        if bVerbose==True:
            fp = open(o,'r')
            lines = fp.readlines()
            fp.close()
            bPrint = False
            for l in lines:
                if 'ANALYSIS' in l:
                    bPrint=True
                if bPrint==True:
                    print(l,end='')
        
    def run_analysis( self, edges=None, bLig=True, bProt=True, bMemb=True, bParseOnly=False, bVerbose=False ):
        """
        Perform analysis on the system's results
        """
        print('----------------')
        print('Running analysis')
        print('----------------')
        
        if edges==None:
            edges = self.edges
        for edge in edges:
            print(f'--> {edge}')
            
            for r in range(1,self.replicas+1):
                
                # ligand
                if bLig==True:
                    wp = 'water'
                    analysispath = '{0}/analyse{1}'.format(self._get_specific_path(edge=edge,wp=wp),r)
                    create_folder(analysispath)
                    stateApath = self._get_specific_path(edge=edge,wp=wp,state='stateA',r=r,sim='transitions')
                    stateBpath = self._get_specific_path(edge=edge,wp=wp,state='stateB',r=r,sim='transitions')
                    self._run_analysis_script( analysispath, stateApath, stateBpath, bVerbose=bVerbose )
                    
                # protein
                if bProt==True:
                    wp = 'protein'
                    analysispath = '{0}/analyse{1}'.format(self._get_specific_path(edge=edge,wp=wp),r)
                    create_folder(analysispath)
                    stateApath = self._get_specific_path(edge=edge,wp=wp,state='stateA',r=r,sim='transitions')
                    stateBpath = self._get_specific_path(edge=edge,wp=wp,state='stateB',r=r,sim='transitions')
                    self._run_analysis_script( analysispath, stateApath, stateBpath, bVerbose=bVerbose )

                # membrane
                if bMemb==True:
                    wp = 'membrane'
                    analysispath = '{0}/analyse{1}'.format(self._get_specific_path(edge=edge,wp=wp),r)
                    create_folder(analysispath)
                    stateApath = self._get_specific_path(edge=edge,wp=wp,state='stateA',r=r,sim='transitions')
                    stateBpath = self._get_specific_path(edge=edge,wp=wp,state='stateB',r=r,sim='transitions')
                    self._run_analysis_script( analysispath, stateApath, stateBpath, bVerbose=bVerbose )
        print('DONE')
        
        

    def _fill_resultsAll( self, res, edge, wp, r ):
        """
        Fill resultsAll DataFrame with relevant results information
        """
        rowName = '{0}_{1}_{2}'.format(edge,wp,r)
        self.resultsAll.loc[rowName,'val'] = res[2]
        self.resultsAll.loc[rowName,'err_analyt'] = res[3]
        self.resultsAll.loc[rowName,'err_boot'] = res[4]
        self.resultsAll.loc[rowName,'framesA'] = res[0]
        self.resultsAll.loc[rowName,'framesB'] = res[1]
        
    def _summarize_results( self, edges ):
        """
        Generate summary for results
        """

        red = "\033[31m"
        green = "\033[92m"
        end = "\033[0m"
        blue = '\033[34m'

        bootnum = 1000
        for edge in edges:
            for wp in ['water','protein', 'membrane']:
                dg = []
                erra = []
                errb = []
                distra = []
                distrb = []
                for r in range(1,self.replicas+1):
                    
                    rowName = '{0}_{1}_{2}'.format(edge,wp,r)
                    dg.append( self.resultsAll.loc[rowName,'val'] )
                    erra.append( self.resultsAll.loc[rowName,'err_analyt'] )
                    errb.append( self.resultsAll.loc[rowName,'err_boot'] )
                    distra.append(np.random.normal(self.resultsAll.loc[rowName,'val'],self.resultsAll.loc[rowName,'err_analyt'] ,size=bootnum))
                    distrb.append(np.random.normal(self.resultsAll.loc[rowName,'val'],self.resultsAll.loc[rowName,'err_boot'] ,size=bootnum))
                    


                rowName = '{0}_{1}'.format(edge,wp)
                distra = np.array(distra).flatten()
                distrb = np.array(distrb).flatten()

                if self.replicas==1:
                    self.resultsAll.loc[rowName,'val'] = dg[0]                              
                    self.resultsAll.loc[rowName,'err_analyt'] = erra[0]
                    self.resultsAll.loc[rowName,'err_boot'] = errb[0]
                else:

                    if self.maxDiff is None:
                        self.resultsAll.loc[rowName,'val'] = np.mean(dg)
                        self.resultsAll.loc[rowName,'err_analyt'] = np.sqrt(np.var(distra)/float(self.replicas))
                        self.resultsAll.loc[rowName,'err_boot'] = np.sqrt(np.var(distrb)/float(self.replicas))
                    else:
                        best_group = []

                        # Try all subsets where max difference ≤ max_diff
                        for i in range(len(dg)):
                            group = [dg[i]]
                            ind = [i]
                            for j in range(i+1, len(dg)):
                                if abs(dg[j] - dg[i]) <= self.maxDiff:
                                    group.append(dg[j])
                            if len(group) > len(best_group):
                                best_group = group

                        print(f'--> Using results from replicas {[i+1 for i in ind]} (from {dg}) for the mean since maxDiff is {self.maxDiff}.')
                        print(distra)

                        self.resultsAll.loc[rowName,'val'] = np.mean(best_group)
                        erra = [distra[i] for i in ind]
                        errb = [distrb[i] for i in ind]
                        self.resultsAll.loc[rowName,'err_analyt'] = np.sqrt(np.var(distra)/float(len(best_group)))
                        self.resultsAll.loc[rowName,'err_boot'] = np.sqrt(np.var(distrb)/float(len(best_group)))
                    
            #### also collect resultsSummary
            rowNameWater = '{0}_{1}'.format(edge,'water')
            rowNameProtein = '{0}_{1}'.format(edge,'protein')
            rowNameMembrane = '{0}_{1}'.format(edge,'membrane')

            dg_pw = self.resultsAll.loc[rowNameProtein,'val'] - self.resultsAll.loc[rowNameWater,'val']
            dg_pm = self.resultsAll.loc[rowNameProtein,'val'] - self.resultsAll.loc[rowNameMembrane,'val']
            dg_mw = self.resultsAll.loc[rowNameMembrane,'val'] - self.resultsAll.loc[rowNameWater,'val']


            erra_pw = np.sqrt( np.power(self.resultsAll.loc[rowNameProtein,'err_analyt'],2.0) \
                            + np.power(self.resultsAll.loc[rowNameWater,'err_analyt'],2.0) )
            errb_pw = np.sqrt( np.power(self.resultsAll.loc[rowNameProtein,'err_boot'],2.0) \
                            + np.power(self.resultsAll.loc[rowNameWater,'err_boot'],2.0) )
            
            erra_pm = np.sqrt( np.power(self.resultsAll.loc[rowNameProtein,'err_analyt'],2.0) \
                            + np.power(self.resultsAll.loc[rowNameMembrane,'err_analyt'],2.0) )
            errb_pm = np.sqrt( np.power(self.resultsAll.loc[rowNameProtein,'err_boot'],2.0) \
                            + np.power(self.resultsAll.loc[rowNameMembrane,'err_boot'],2.0) )
            
            erra_mw = np.sqrt( np.power(self.resultsAll.loc[rowNameMembrane,'err_analyt'],2.0) \
                            + np.power(self.resultsAll.loc[rowNameWater,'err_analyt'],2.0) )
            errb_mw = np.sqrt( np.power(self.resultsAll.loc[rowNameMembrane,'err_boot'],2.0) \
                            + np.power(self.resultsAll.loc[rowNameWater,'err_boot'],2.0) )
            rowName = edge
            self.resultsSummary.loc[rowName,'dG_wp'] = dg_pw
            self.resultsSummary.loc[rowName,'dG_mp'] = dg_pm
            self.resultsSummary.loc[rowName,'dG_wm'] = dg_mw

            self.resultsSummary.loc[rowName,'err_analyt_wp'] = erra_pw
            self.resultsSummary.loc[rowName,'err_boot_wp'] = errb_pw
            self.resultsSummary.loc[rowName,'err_analyt_mp'] = erra_pm
            self.resultsSummary.loc[rowName,'err_boot_mp'] = errb_pm
            self.resultsSummary.loc[rowName,'err_analyt_wm'] = erra_mw
            self.resultsSummary.loc[rowName,'err_boot_wm'] = errb_mw

            valid = dg_mw - dg_pm
            valid_erra = np.sqrt( np.power(self.resultsSummary.loc[rowName,'err_analyt_mp'],2.0) \
                            + np.power(self.resultsSummary.loc[rowName,'err_analyt_wm'],2.0) )
            valid_errb = np.sqrt( np.power(self.resultsSummary.loc[rowName,'err_boot_mp'],2.0) \
                            + np.power(self.resultsSummary.loc[rowName,'err_boot_wm'],2.0) )
            


            print('\n-----------------------VALIDATION------------------------')
            print(f'\t--> {blue} dG_wp +- 2d(wp) =? dg_wm - dg_mp +- 2d(wm-mp){end}\n')
            print(f'\t--> A: {dg_pw:.3f} +- {2*erra_pw:.3f} =? {valid:.3f} +- {valid_erra:.3f}')
            print(f'\t--> B: {dg_pw:.3f} +- {2*errb_pw:.3f} =? {valid:.3f} +- {valid_errb:.3f}\n')
            if dg_pw - 2*erra_pw < valid + valid_erra and dg_pw + 2*erra_pw > valid - valid_erra:
                print(f'\t--> {green}VALIDATION PASSED{end}')
            else:
                print(f'\t--> {red}VALIDATION FAILED{end}')
            print('---------------------------------------------------------\n')

        self.resultsSummary.to_csv(f'results_summary.csv')

        self._results_image()

    
    def _results_image(self):

        decimals = self.precision
        
        for edge in self.edges:
            edgepath = '{0}'.format(self._get_specific_path(edge=edge))

            self.resultsSummary = pd.read_csv(f'results_summary.csv', index_col=0)
        
            img = mpimg.imread('utils/results.png')
            
            plt.figure()
            plt.imshow(img)
            plt.title(edge)
            dg_pw = self.resultsSummary.loc[edge,'dG_wp']
            dg_pm = self.resultsSummary.loc[edge,'dG_mp']
            dg_mw = self.resultsSummary.loc[edge,'dG_wm']

            e_pw = self.resultsSummary.loc[edge,'err_boot_wp']
            e_pm = self.resultsSummary.loc[edge,'err_boot_mp']
            e_mw = self.resultsSummary.loc[edge,'err_boot_wm']

            plt.text(670, 141, f'{dg_pw:.{decimals}f} $\pm$ {e_pw:.{decimals}f} kJ/mol', fontsize=8, color='black')
            plt.text(1010, 359, f'{dg_pm:.{decimals}f} $\pm$ {e_pm:.{decimals}f} kJ/mol', fontsize=8, color='black')
            plt.text(142, 348, f'{dg_mw:.{decimals}f} $\pm$ {e_mw:.{decimals}f} kJ/mol', fontsize=8, color='black')
    
            plt.axis('off')               # Hides ticks and axes
            # plt.gca().spines[:].clear()   # Hides axis lines (spines)
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove padding
            
            plt.savefig(f'{edgepath}/results.png', dpi=300)
            print(f'\nResults image saved to {edgepath}/results.png')


    def _read_neq_results( self, fname ):
        """
        Read NEQ results and return relevant data
        """
        fp = open(fname,'r')
        lines = fp.readlines()
        fp.close()
        out = []
        for l in lines:
            l = l.rstrip()
            foo = l.split()
            if 'BAR: dG' in l:
                out.append(float(foo[-2]))
            elif 'BAR: Std Err (bootstrap)' in l:
                out.append(float(foo[-2]))
            elif 'BAR: Std Err (analytical)' in l:
                out.append(float(foo[-2]))      
            elif '0->1' in l:
                out.append(int(foo[-1]))      
            elif '1->0' in l:
                out.append(int(foo[-1]))
        return(out)
            
                    
    def analysis_summary( self, edges=None ):
        """
        Perform analysis for all systems
        """
        if edges==None:
            edges = self.edges
            
        for edge in edges:
            for r in range(1,self.replicas+1):
                for wp in ['water','protein', 'membrane']:
                    analysispath = '{0}/analyse{1}'.format(self._get_specific_path(edge=edge,wp=wp),r)
                    resultsfile = '{0}/results.txt'.format(analysispath)
                    res = self._read_neq_results( resultsfile )
                    self._fill_resultsAll( res, edge, wp, r )
        
        # the values have been collected now
        # let's calculate ddGs
        self._summarize_results( edges )

