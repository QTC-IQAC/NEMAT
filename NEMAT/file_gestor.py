from nemat import *
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
    fe = NEMAT(**config)

    print(fe.edges,"From main program")

    fe.prepareAttributes() # don't comment

    check_files(fe) # check if the files are present and correct

    return fe


def check_files(fe):
    """
    CHECK MDP FILES
    """

    mdp_files = os.listdir(f'{fe.inputDirName}/mdppath')
    trans_files = [f for f in mdp_files if f.endswith('ti_l0.mdp') or f.endswith('ti_l1.mdp')]

    # check delta-lambda
    for tfile in trans_files: 
        with open(f'{fe.inputDirName}/mdppath/{tfile}', 'r') as f:
            for line in f:
                # Ignore comments and empty lines
                line = line.strip()
                if not line or line.startswith(';'):
                    continue

                # Split key-value pairs
                if '=' in line:
                    key, value = line.split('=')[0], line.split('=')[-1].split(';')[0]
                    key = key.strip()
                    value = value.strip()

                    if key == 'nsteps':
                        nsteps = int(value)
                    elif key == 'delta-lambda':
                        delta_lambda = abs(float(value))

        # Ensure both values were found
        if nsteps is None or delta_lambda is None:
            raise ValueError("Missing 'nsteps' or 'delta-lambda' in MDP file")

        # Compute expected delta-lambda
        expected = 1.0 / nsteps

        # Assert with a tolerance for floating point comparison
        assert abs(delta_lambda - expected) < 1e-8, \
            f"delta-lambda ({delta_lambda}) is not equal to 1/nsteps ({expected}) this would raise a GROMACS error"
        
    
    run_files = os.listdir(f'NEMAT/run_files')
    for f in run_files:
        new_file = []
        with open(f'NEMAT/run_files/{f}', 'r') as file:
            lines = file.readlines()
            for line in lines:
                
                    if line.startswith('#SBATCH -n'):
                        # Replace the line with the new one
                        new_line = f'#SBATCH -n {fe.JOBsimcpu}\n'
                        new_file.append(new_line)
                    elif line.startswith('#SBATCH -p'):
                        # Replace the line with the new one
                        new_line = f'#SBATCH -p {fe.JOBpartition}\n'
                        new_file.append(new_line)
                    elif line.startswith('#SBATCH --gres'):
                        new_file.append(line)
                        if fe.JOBsimtime != '':
                            if f == 'prep_min.sh':
                                # Replace the line with the new one
                                new_line = f'#SBATCH -t 00-01:00\n'
                            elif f == 'prep_eq.sh':
                                new_line = f'#SBATCH -t 00-01:00\n'
                            elif f == 'prep_md.sh':
                                new_line = f'#SBATCH -t 00-04:00\n'
                            elif f == 'prep_ti.sh':
                                new_line = f'#SBATCH -t 01-00:00\n'
                            elif f == 'prep.sh':
                                new_line = f'#SBATCH -t 00-01:00\n'
                            elif f == 'analyze.sh':
                                new_line = f'#SBATCH -t 00-12:00\n'
                            
                            new_file.append(new_line)
                            
                        if len(fe.JOBmodules) > 0:
                            new_file.append('\n')
                            for module in fe.JOBmodules: 
                                new_file.append(f'module load {module}\n')

                    elif line.startswith('#SBATCH -t'):
                        pass

                    elif line.startswith('module'):
                        pass
                    else:
                        new_file.append(line)

        
        with open(f'NEMAT/run_files/{f}', 'w') as file:
            file.writelines(new_file)


    # check if the membrane files are present
    memb_files = os.listdir(f'{fe.inputDirName}/membrane')
    assert 'membrane.gro' in memb_files, \
        "membrane.gro file not found in membrane directory. Add it or rename the gro file"
    assert 'membrane.top' in memb_files, \
        "membrane.top file not found in membrane directory. Add it or rename the top file"   

    # check if the protein files are present
    prot = os.listdir(f'{fe.inputDirName}/proteins')
    prot_files = os.listdir(f'{fe.inputDirName}/proteins/{prot[0]}')
    assert 'system.gro' in prot_files, \
        "system.gro file not found in proteins directory. Add it or rename the gro file"
    assert 'system.top' in prot_files, \
        "system.top file not found in proteins directory. Add it or rename the top file"

    
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
    
    fe.boxWaterIons(bBoxLig=True,bWatLig=True,bIonLig=True)

def minimization():
    
    """
    ENERGY MINIMIZATION
    """
    fe = read_input() # Initialize the class with the input parameters

    fe.prepare_simulation( simType='em', bProt=True, bLig=True, bMemb=True)
    fe.prepare_jobscripts(simType='em', bProt=True, bLig=True, bMemb=True)

def equilibration():
    
    """
    EQUILIBRATION
    """
    fe = read_input() # Initialize the class with the input parameters

    fe.prepare_simulation( simType='eq', bProt=True)
    fe.prepare_jobscripts(simType='eq', bProt=True, bLig=True, bMemb=True)


def production():
   
    """
    PRODUCTION
    """
    fe = read_input() # Initialize the class with the input parameters

    # create the jobscripts
    fe.prepare_simulation(simType='md', bProt=True, bLig=True, bMemb=True)
    fe.prepare_jobscripts(simType='md', bProt=True, bLig=True, bMemb=True)


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
    fe.analysis_summary()
    fe.resultsAll.to_csv('results_all.csv')
    print(fe.resultsSummary)


def track_errors(file):
    """
    TRACK ERRORS
    """

    red = "\033[31m"
    green = "\033[92m"
    end = "\033[0m"

    with open(file, 'r') as f:
        lines = f.readlines()
        errors = {}
        warnings = {}
        e = False
        w = False
        aux = []
        aux2 = []
        for i, line in enumerate(lines):
            if line.startswith('Error') or line.startswith('Fatal'):
                e = True
                eline = i   
            if e:
                aux.append(line)
                if line == '\n':
                    e = False
                    errors[f'Error_{eline}'] = aux
                    aux = []
                    
            if line.startswith('WARNING'):
                w = True
                wline = i   
            if w:
                aux2.append(line)
                if line == '\n':
                    w = False
                    warnings[f'Warning_{wline}'] = aux2
                    aux2 = []
    
    with open(f"logs/errors_{file.lstrip('logs/').rstrip('.err')}.log", 'w') as f:

        if len(errors) == 0:
            f.write(f'{green}No errors found!!{end}\n')
        
        for err in errors:
            f.write(f'{red}{err}{end}:\n')
            for line in errors[err]:
                f.write(line)
            f.write('\n')
    
    with open(f"logs/warnings_{file.lstrip('logs/').rstrip('.err')}.log", 'w') as f:
        if len(warnings) == 0:
            f.write(f'{green}No warnings found!!{end}\n')
        
        for w in warnings:
            f.write(f'{red}{w}{end}:\n')
            for line in warnings[w]:
                f.write(line)
            f.write('\n')

                
    


if __name__ == '__main__':
    args = args_parser()
    if args.step == 'prep':
        print("Assembling system...")
        asssemble_system()
        prepare_ligands()
        print("Tracking errors...")
        track_errors('logs/prep.err')
    
    elif args.step == 'min':
        print("Minimization...")
        minimization()
        print("Tracking errors...")
        track_errors('logs/min.err')
    
    elif args.step == 'eq':
        print("Equilibration...")
        equilibration()
        print("Tracking errors...")
        track_errors('logs/eq.err')
    
    elif args.step == 'md':
        print("Production...")
        production()
        print("Tracking errors...")
        track_errors('logs/md.err')
    
    elif args.step == 'ti':
        print("Transitions...")
        transitions()
        print("Tracking errors...")
        track_errors('logs/ti.err')
    
    elif args.step == 'analysis':
        print("Analysis...")
        analyse()
        print("Tracking errors...")
        track_errors('logs/analysis.err')

    elif args.step == 'img':
        print("Generating results image from results_summary.csv...")
        fe = read_input()
        fe._results_image()

    elif args.step == 'test':
        read_input(f='input.yaml')