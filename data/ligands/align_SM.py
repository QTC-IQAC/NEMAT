import os

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.rdFMCS import FindMCS
from argparse import ArgumentParser

def args_parser():
    """
    This function parses command-line arguments for the script.

    Parameters:
    -----------
    None

    Returns:
    --------
    args : argparse.Namespace
        An object containing the parsed command-line arguments.
        The object has attributes corresponding to the command-line arguments,
        e.g., args.ft
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--ft",
        type=str,
        help="File type of the ligand.",
        required=False,
        default='pdb'
    )

    args = parser.parse_args()
    return args

def align_molecules(ref_file, query_file, output_file, ft="sdf"):

    # Load molecules
    if ft == "sdf":
        ref = Chem.SDMolSupplier(ref_file, removeHs=False)[0]
        mol = Chem.SDMolSupplier(query_file, removeHs=False)[0]
    elif ft == "pdb":
        ref = Chem.MolFromPDBFile(ref_file, removeHs=False)
        mol = Chem.MolFromPDBFile(query_file, removeHs=False)
        print('\t--> WARNING: PDB files may not contain proper bond information!!!!!')
    elif ft == "mol2":
        ref = Chem.MolFromMol2File(ref_file, removeHs=False)
        mol = Chem.MolFromMol2File(query_file, removeHs=False)
    elif ft == "mol":
        ref = Chem.MolFromMolFile(ref_file, removeHs=False)
        mol = Chem.MolFromMolFile(query_file, removeHs=False)
    else:
        raise ValueError(f"Unsupported file type: {ft}")

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
    Chem.MolToMolFile(mol, output_file)



# Example usage:
if __name__ == "__main__":
    args = args_parser()
    ft = args.ft.lstrip(".").lower()
    ligs = os.listdir("ligands")
    ligs = [lig for lig in ligs if lig.endswith(f".{ft}")]
    for lig in ligs:
        print(f"--> {lig}")
        name = lig.split(".")[0].split("/")[-1]
        align_molecules(f"ref_lig.{ft}", f"ligands/{lig}", f"aligned/{name}.sdf", ft=ft)
