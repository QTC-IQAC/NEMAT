from AZtutorial import *
import yaml
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
        e.g., args.p
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--step",
        type=str,
        help="Step of the FEP calculation you are at: [prep, min, eq, md, ti, analysis] which are preparation (assemble of the system and ligand solvation)\
        minimization, equilibration, production, transitions and analysis",
        required=True,
    )

    args = parser.parse_args()
    return args

def read_input(f='input.yaml'):
    

    with open("input.yaml") as f:
        config = yaml.safe_load(f)


    # initialize the free energy environment object: it will store the main parameters for the calculations
    fe = AZtutorial(**config)

    print(fe.edges,"From main program")

    fe.prepareAttributes() # don't comment

    return fe

def asssemble_system():
    fe = read_input() # Initialize the class with the input parameters

    # finally, let's prepare the overall free energy calculation directory structure
    fe.prepareFreeEnergyDir( )

    """
    ASSEMBLE SYSTEM FOR FEP
    """
    # this command will map the atoms of all edges found in the 'fe' object
    # bVerbose flag prints the output of the command
    fe.atom_mapping(bVerbose=False)
    fe.hybrid_structure_topology(bVerbose=False)
    fe.assemble_systems( )

def prepare_ligands():
    
    """
    ADD SOLVENT TO LIG
    """
    fe = read_input() # Initialize the class with the input parameters
    
    fe.boxWaterIons(bBoxProt=False,bWatProt=False,bIonProt=False,bBoxLig=True,bWatLig=True,bIonLig=True)

def minimization():
    
    """
    ENERGY MINIMIZATION
    """
    fe = read_input() # Initialize the class with the input parameters

    fe.prepare_simulation( simType='em' )
    fe.prepare_jobscripts(simType='em', bProt=False, bLig=False, bMemb=True)

def equilibration():
    
    """
    EQUILIBRATION
    """
    fe = read_input() # Initialize the class with the input parameters

    fe.prepare_simulation( simType='eq', bProt=True)
    fe.prepare_jobscripts(simType='eq', bProt=False, bLig=False, bMemb=True)


def production():
   
    """
    PRODUCTION
    """
    fe = read_input() # Initialize the class with the input parameters

    # create the jobscripts
    fe.prepare_simulation(simType='md', bProt=False, bLig=False, bMemb=True)
    fe.prepare_jobscripts(simType='md', bProt=False, bLig=False, bMemb=True)


def transitions():

    """
    PREPARE NON EQUILIBRIUM TRANSITIONS
    """
    fe = read_input() # Initialize the class with the input parameters

    fe.prepare_transitions(bGenTpr=True, bProt=True, bLig=True, bMemb=True)
    fe.prepare_jobscripts(simType='transitions', bProt=True)


def analyse():
    """
    ANALYSIS
    """
    fe = read_input() # Initialize the class with the input parameters
    
    fe.run_analysis( bVerbose=True)
    fe.analysis_summary( )
    fe.resultsAll.to_csv('results_all.csv')
    print(fe.resultsSummary)


if __name__ == '__main__':
    args = args_parser()
    if args.step == 'prep':
        print("Assembling system...")
        asssemble_system()
    elif args.step == 'min':
        print("Minimization...")
        minimization()
    elif args.step == 'eq':
        print("Equilibration...")
        equilibration()
    elif args.step == 'md':
        print("Production...")
        production()
    elif args.step == 'ti':
        print("Transitions...")
        transitions()
    elif args.step == 'analysis':
        print("Analysis...")
        analyse()

        
    # asssemble_system()
    # prepare_ligands()
    # minimization()
    # equilibration()
    # production()
    # transitions()
    # analyse()
