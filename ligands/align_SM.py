import os

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.rdFMCS import FindMCS

def align_molecules(ref_file, query_file, output_file):

    # Load molecules
    ref = Chem.MolFromPDBFile(ref_file, removeHs=False)
    mol = Chem.MolFromPDBFile(query_file, removeHs=False)

    # Generate 3D coordinates if not present
    # AllChem.EmbedMolecule(ref)
    # AllChem.EmbedMolecule(mol)

    # Find Maximum Common Substructure (MCS)
    mcs_result = FindMCS([ref, mol], ringMatchesRingOnly=True, completeRingsOnly=True)
    mcs_mol = Chem.MolFromSmarts(mcs_result.smartsString)

    # Get atom indices for alignment
    match1 = ref.GetSubstructMatch(mcs_mol)
    match2 = mol.GetSubstructMatch(mcs_mol)

    # Align mol onto ref using MCS
    rmsd = AllChem.AlignMol(mol, ref, atomMap=list(zip(match2, match1)))

    # Save aligned mol
    Chem.MolToPDBFile(mol, output_file)


# Example usage:
if __name__ == "__main__":
    ligs = os.listdir("ligands")
    for lig in ligs:
        print(f"--> {lig}")
        name = lig.split(".")[0].split("/")[-1]
        align_molecules("ref_lig.pdb", f"ligands/{lig}", f"aligned/{name}_a.pdb")
