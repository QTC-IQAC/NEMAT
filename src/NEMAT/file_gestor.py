from nemat import *
import yaml
from argparse import ArgumentParser
import warnings



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

    parser.add_argument(
        "--NMT_HOME",
        type=str,
        help="Path to the NMT_HOME directory",
        default=None,
        required=False
    )

    args = parser.parse_args()
    return args

def custom_formatwarning(message, category, filename, lineno, line=None):
    # Keep the warning type, but drop filename/line info
    return f"{category.__name__}: {message}\n"

def read_input(f='input.yaml'):
    with open(f) as f:
        config = yaml.safe_load(f)


    # initialize the free energy environment object: it will store the main parameters for the calculations
    nmt = NEMAT(**config)

    # print(nmt.edges,"From main program")

    nmt.prepareAttributes() # don't comment

    return nmt


def check_files(nmt, nmt_home=None):
    """
    CHECK MDP FILES
    """
    mdp_files = os.listdir(f'{nmt.inputDirName}/mdppath')

    time_eq_l0m = []
    time_eq_l1m = []
    time_eq_l0p = []
    time_eq_l1p = []

    protein = {'eq':[], 'md':[], 'ti':[]}
    membrane = {'eq':[], 'md':[], 'ti':[]}
    water = {'eq':[], 'md':[], 'ti':[]}

    # check delta-lambda
    prev_framenum = nmt.frameNum
    for file in mdp_files:
        wp = file.split('_')[0]
        with open(f'{nmt.inputDirName}/mdppath/{file}', 'r') as f:
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
                    elif key == 'nstxout-compressed':
                        nstxout_compressed = int(value)
                    elif key == 'dt':
                        dt = float(value)
            

        if file.endswith('ti_l0.mdp') or file.endswith('ti_l1.mdp'):
            # Ensure both values were found
            if nsteps is None or delta_lambda is None:
                raise ValueError(f"Missing 'nsteps' or 'delta-lambda' in {file} file")


            if file.endswith('l0.mdp'):
                time_ti0 = dt*nsteps/1000 # in ns
                if nmt.titime is not None:
                    if nmt.titime != time_ti0:
                        warnings.warn(f'[{file}]; Transition time in mdp file ({time_ti0} ns) is different from the one specified in input.yaml ({nmt.titime} ns). The one in input.yaml will be used.')
                        # change nsteps in mdp file
                        os.system(f'{nmt_home}/src/NEMAT/change_time.sh {nmt.inputDirName}/mdppath/{file} {nmt.titime} 10')
                        time_ti0 = nmt.titime
            else:
                time_ti1 = dt*nsteps/1000

                if nmt.titime is not None:
                    if nmt.titime != time_ti1:
                        warnings.warn(f'[{file}]; Transition time in mdp file ({time_ti1} ns) is different from the one specified in input.yaml ({nmt.titime} ns). The one in input.yaml will be used.')
                        # change nsteps in mdp file
                        os.system(f'{nmt_home}/src/NEMAT/change_time.sh {nmt.inputDirName}/mdppath/{file} {nmt.titime} 10')
                        time_ti1 = nmt.titime

            # # Assert with a tolerance for floating point comparison
            # assert abs(delta_lambda - expected) < 1e-8, \
            #     f"file {file}: delta-lambda ({delta_lambda}) is not equal to 1/nsteps ({expected}) this would raise a GROMACS error"
            
            try:
                if wp == 'prot':
                    protein['ti'].append(time_ti0)
                elif wp == 'memb':
                    membrane['ti'].append(time_ti0)
                elif wp == 'lig':
                    water['ti'].append(time_ti0)
            except:
                if wp == 'prot':
                    protein['ti'].append(time_ti1)
                elif wp == 'memb':
                    membrane['ti'].append(time_ti1)
                elif wp == 'lig':
                    water['ti'].append(time_ti1)

        elif file.endswith('md_l0.mdp') or file.endswith('md_l1.mdp'):

            if nsteps is None or delta_lambda is None:
                raise ValueError(f"Missing 'nsteps' in {file} file")

            # compute how many frames will be saved
            # total_frames = floor(nsteps / nstxout_compressed)

            if nmt.saveFrames < nmt.frameNum:
                raise ValueError(f"Total frames that will be saved ({nmt.saveFrames}) is less than required frames for transitions ({nmt.frameNum}).\n\t--> Modify {file}.")
            
            possible_frames = nmt.saveFrames
            if file.endswith('l0.mdp'):
                time_md0 = dt*nsteps/1000 # in ns

                if nmt.mdtime is not None:
                    if nmt.mdtime != time_md0:
                        warnings.warn(f'[{file}]; Production time in mdp file ({time_md0} ns) is different from the one specified in input.yaml ({nmt.mdtime} ns). The one in input.yaml will be used.')
                    # change nsteps in mdp file
                    os.system(f'{nmt_home}/src/NEMAT/change_time.sh {nmt.inputDirName}/mdppath/{file} {nmt.mdtime} {nmt.saveFrames}')
                    time_md0 = nmt.mdtime

                if nmt.tstart is None:
                    time_per_frame = time_md0 / nmt.saveFrames
                    if time_per_frame < 0.1:
                        warnings.warn(f'[{file}]; A frame will be extracted every {time_per_frame:.2f} ns which is less than 0.1 ns. This may lead to poor overlap between states due to correlation between frames. Consider increasing nstxout-compressed.')
                else:
                    time_per_frame = (time_md0 - nmt.tstart/1000) / nmt.frameNum
                    possible_frames = int(nmt.saveFrames - nmt.tstart/1000/time_per_frame) 
                    if time_per_frame < 0.1:
                        warnings.warn(f'[{file}]; A frame will be extracted every {time_per_frame:.2f} ns which is less than 0.1 ns. This may lead to poor overlap between states due to correlation between frames. Consider increasing nstxout-compressed.')

            else:
                time_md1 = dt*nsteps/1000 # in ns
                if nmt.mdtime is not None:
                    if nmt.mdtime != time_md1:
                        warnings.warn(f'[{file}]; Production time in mdp file ({time_md1} ns) is different from the one specified in input.yaml ({nmt.mdtime} ns). The one in input.yaml will be used.')
                    # change nsteps in mdp file
                    os.system(f'{nmt_home}/src/NEMAT/change_time.sh {nmt.inputDirName}/mdppath/{file} {nmt.mdtime} {nmt.saveFrames}')
                    time_md1 = nmt.mdtime
                
                if nmt.tstart is None:
                    time_per_frame = time_md1 / nmt.saveFrames
                    if time_per_frame < 0.1:
                        warnings.warn(f'[{file}]; A frame will be extracted every {time_per_frame:.2f} ns which is less than 0.1 ns. This may lead to poor overlap between states due to correlation between frames. Consider increasing nstxout-compressed.')
                else:
                    time_per_frame = (time_md1 - nmt.tstart/1000) / nmt.frameNum
                    possible_frames = int(nmt.saveFrames - nmt.tstart/1000/time_per_frame) 
                    if time_per_frame < 0.1:
                        warnings.warn(f'[{file}]; A frame will be extracted every {time_per_frame:.2f} ns which is less than 0.1 ns. This may lead to poor overlap between states due to correlation between frames. Consider increasing nstxout-compressed.')
            try:
                if wp == 'prot':
                    protein['md'].append(time_md0)
                elif wp == 'memb':
                    membrane['md'].append(time_md0)
                elif wp == 'lig':
                    water['md'].append(time_md0)
            except:
                if wp == 'prot':
                    protein['md'].append(time_md1)
                elif wp == 'memb':
                    membrane['md'].append(time_md1)
                elif wp == 'lig':
                    water['md'].append(time_md1)

        elif file.endswith('em_l0.mdp') or file.endswith('em_l1.mdp'):
            pass
            
        else:
            if wp == 'prot':
                if file.endswith('l0.mdp'):
                    time_eq_l0p.append(round(dt*nsteps/1000, 3)) # in ns
                else:
                    time_eq_l1p.append(round(dt*nsteps/1000, 3)) # in ns
            elif wp == 'memb':
                if file.endswith('l0.mdp'):
                    time_eq_l0m.append(round(dt*nsteps/1000, 3)) # in ns
                else:
                    time_eq_l1m.append(round(dt*nsteps/1000, 3)) # in ns
            else:
                if file.endswith('l0.mdp'):
                    time_eq0 = round(dt*nsteps/1000, 3) # in ns
                else:
                    time_eq1 = round(dt*nsteps/1000, 3) # in ns

    water['eq'] = [time_eq0, time_eq1]

    time_eq0 = np.round(np.sum(np.array(time_eq_l0p)), 3)
    time_eq1 = np.round(np.sum(np.array(time_eq_l1p)), 3)

    protein['eq'] = [time_eq0, time_eq1]

    time_eq0 = np.round(np.sum(np.array(time_eq_l0m)), 3)
    time_eq1 = np.round(np.sum(np.array(time_eq_l1m)), 3)

    membrane['eq'] = [time_eq0, time_eq1]

    assert protein['eq'][0] == protein['eq'][1], f"Total equilibration times for protein are not equal for the protein system!: {protein['eq'][0]}, {protein['eq'][1]}"
    assert membrane['eq'][0] == membrane['eq'][1], f"Total equilibration times for membrane are not equal for the membrane system!: {membrane['eq'][0]}, {membrane['eq'][1]}"
    assert water['eq'][0] == water['eq'][1], f"Equilibration time for water is not equal for the water system!: {water['eq'][0]}, {water['eq'][1]}"

    assert protein['md'][0] == protein['md'][1], f"Total production times for protein are not equal for the protein system!: {protein['md'][0]}, {protein['md'][1]}"
    assert membrane['md'][0] == membrane['md'][1], f"Total production times for membrane are not equal for the membrane system!: {membrane['md'][0]}, {membrane['md'][1]}"
    assert water['md'][0] == water['md'][1], f"Production time for water is not equal for the water system!: {water['md'][0]}, {water['md'][1]}"

    def draw_table(values):
        # Define column and row names
        columns = ["eq", "md", "ti"]
        rows = ["water", "membrane", "protein"]

        # Define cell width
        cell_width = max(
            max(len(c) for c in columns),
            max(len(r) for r in rows),
            max(len(str(v)) for row in values.values() for v in row.values())
        )

        # Header and separator
        header = "| {:<{w}} ".format("", w=cell_width) + "".join(
            "| {:<{w}} ".format(col, w=cell_width) for col in columns
        ) + "|\n"
        separator = "+" + "+".join(["-" * (cell_width + 2) for _ in range(len(columns) + 1)]) + "+\n"

        # Rows
        rows_str = ""
        for row in rows:
            rows_str += "| {:<{w}} ".format(row, w=cell_width)
            for col in columns:
                val = values.get(row, {}).get(col, "")
                # print(val)
                rows_str += "| {:<{w}} ".format(val[0], w=cell_width)
            rows_str += "|\n"

        # Combine and save
        table = separator + header + separator + rows_str + separator
        return table


    end = "\033[0m"
    blue = '\033[1;35m'
    yellow = '\033[1;33m'
    red = "\033[31m"
    blink = '\033[5m'
    green = "\033[92m"
 

    table = draw_table(dict(water=water, membrane=membrane, protein=protein))

    with open('logs/checklist.txt', 'w') as f:
        
        f.write(f"\n-->-->--> System check <--<--<--\n")
        f.write(f"\n{blue}-- SIMULATION TIMES (ns) --{end}\n")
        f.write(table)
        f.write(f"\n{blue}-- INFO --{end}\n")
        f.write(f"\n{green}|{end}\t--> Frames saved in md          : {yellow}{nmt.saveFrames}{end}\n")
        if possible_frames < nmt.frameNum:
            f.write(f"|\n{red}{blink}WARNING:{end}{end}  With the current settings, only {red}{possible_frames}{end} frames are available for transitions instead of {yellow}{prev_framenum}{end}.\n|\t  If you still want {yellow}{prev_framenum}{end} transitions, consider decreasing {yellow}tstart{end} or\n|\t  increasing {yellow}saveFrames{end}. Current values: [tstart: {nmt.tstart/1000} ns; SaveFrames: {nmt.saveFrames}] \n{green}|{end}\n")
            f.write(f"{green}|{end}\t--> Number of transitions       : {yellow}{possible_frames}{end}\n")
        else:
            f.write(f"{green}|{end}\t--> Number of transitions       : {yellow}{nmt.frameNum}{end}\n")
        
        f.write(f"{green}|{end}\t--> dt transitions              : {yellow}{time_per_frame:.2f} ns{end}\n")
        if time_per_frame < 0.1:
            f.write(f"{red}WARNING:{end}  A frame will be extracted every {time_per_frame:.2f} ns which is less than 0.1 ns.\n|\t  This may lead to poor overlap between states due to correlation between frames.\n|\t  Consider increasing nstxout-compressed.\n{green}|{end}\n")
        if nmt.tstart is None:
            f.write(f"{green}|{end}\t\t--> This means that the first transition frame would be {yellow}{nmt.saveFrames-nmt.frameNum} (at {(nmt.saveFrames-nmt.frameNum)*time_per_frame} ns){end}.\n")
        else:
            f.write(f"{green}|{end}\t\t--> This means that the first transition frame would be {yellow}{int(nmt.tstart/1000*nmt.saveFrames/time_md0)} (at {nmt.tstart/1000} ns){end}.\n")
        f.write(f"{green}|{end}\n")
        f.write(f"{green}|{end}\t--> Transitions for analysis    : {yellow}{nmt.nframesAnalysis}{end}\n")
        f.write(f"{green}|{end}\t--> Spaced frames for analysis  : {yellow}{nmt.spacedFrames}{end}\n")
        if nmt.spacedFrames:
            if nmt.frameNum // nmt.nframesAnalysis > 1:
                f.write(f"{green}|{end}\t\t--> This means the analysis will use one frame every {yellow}{nmt.frameNum // nmt.nframesAnalysis}{end} transitions\n")
        
        f.write(f"{green}|{end}\n")
        f.write(f"{green}|{end}\t--> Replicas per system         : {yellow}{nmt.replicas}{end}\n")
        f.write(f"{green}|{end}\t--> Simulations will run for {yellow}{len(nmt.edges)} edges{end}.\n{green}|{end}\t\t--> This means {yellow}{len(nmt.edges)*nmt.replicas*6} jobs{end} per step.\n{green}|{end}\n")
        f.write(f"{green}|{end}\t--> Edges:\n")

        for i in nmt.edges:
            f.write(f"\t\t  * {yellow}{i}{end}\n")
        f.write(f"{green}|{end}\n{green}|{end}\t--> Temperature                 : {yellow}{nmt.temp}{end} K\n")
        f.write(f"{green}|{end}\t--> Charge type                 : {yellow}{nmt.chargeType}{end}\n")
        f.write(f"{green}|{end}\t--> Results will be in          : {yellow}{nmt.units}{end}\n") 
        f.write(f"{green}|{end}\n")
        f.write(f"{green}|{end}\t--> CPUs per job                : {yellow}{nmt.JOBsimcpu}{end} \n")
        if nmt.JOBbGPU:
            f.write(f"{green}|{end}\t--> GPU enabled                 : {yellow}{nmt.JOBbGPU}{end}.\n")
        else:
            f.write(f"{green}|{end}\t--> GPU enabled                 : {red}{nmt.JOBbGPU}{end}.\n")
            f.write(f"{red}|{blink}WARNING:{end}{end} GPU is disabled. This is not recommended.\n")
        f.write("\n\n")



    """
    CHECK IMPORTANT FILE NAMES
    """

    # check if the membrane files are present
    if 'membrane' in nmt.thermCycleBranches:
        
        memb_files = os.listdir(f'{nmt.inputDirName}/membrane')
        assert 'membrane.gro' in memb_files, \
            "membrane.gro file not found in membrane directory. Add it or rename the gro file"
        assert 'membrane.top' in memb_files, \
            "membrane.top file not found in membrane directory. Add it or rename the top file"   

    # check if the protein files are present
    if 'protein' in nmt.thermCycleBranches:
        prot = os.listdir(f'{nmt.inputDirName}/proteins')
        prot_files = os.listdir(f'{nmt.inputDirName}/proteins/{prot[0]}')
        assert 'system.gro' in prot_files, \
            "system.gro file not found in proteins directory. Add it or rename the gro file"
        assert 'system.top' in prot_files, \
            "system.top file not found in proteins directory. Add it or rename the top file"
    

        
def check_run_files(nmt, nmt_home):
    """
    CHECK RUN FILES
    """

    run_files = os.listdir(f'{nmt_home}/src/NEMAT/run_files')
    for f in run_files:
        new_file = []
        with open(f'{nmt_home}/src/NEMAT/run_files/{f}', 'r') as file:
            lines = file.readlines()
            for line in lines:
                
                if line.startswith('#SBATCH -n'):
                    # Replace the line with the new one
                    new_line = f'#SBATCH -n {nmt.JOBsimcpu}\n'
                    new_file.append(new_line)
                elif line.startswith('#SBATCH -p'):
                    # Replace the line with the new one
                    new_line = f'#SBATCH -p {nmt.JOBpartition}\n'
                    new_file.append(new_line)
                elif line.startswith('#SBATCH --gres'):
                    new_file.append(line)
                    if nmt.JOBsimtime != '':
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
                        new_file.append('\n')
                        
                    if len(nmt.JOBmodules) > 0:
                        for module in nmt.JOBmodules: 
                            new_file.append(f'module load {module}\n')
                        new_file.append('\n')

                    if len(nmt.JOBexport) > 0:
                        for export in nmt.JOBexport:
                            export = f'export {export}\n'
                            new_file.append(export)
                        new_file.append('\n')


                    if len(nmt.JOBsource) > 0:
                        for s in nmt.JOBsource:
                            source = f'source {s}\n'
                            new_file.append(source)
                        new_file.append('\n')

                    if len(nmt.JOBcommands) > 0:
                        new_comm = False
                        for command in nmt.JOBcommands:
                            if f'{command}\n' not in lines:
                                new_file.append(f'{command}\n')
                                new_comm = True
                        if new_comm:
                            new_file.append('\n')
   

                elif line.startswith('#SBATCH -t'):
                    pass

                elif line.startswith('module'):
                    pass

                elif line.startswith('source'):
                    pass

                elif line.startswith('export'):
                    pass

                else:
                    non = False
                    if not non:
                        if not line.startswith('\n'):
                            if line.startswith('#!/bin'):
                                new_file.append(line)
                            else:
                                new_file.append(line)
                                non = True

                    else:
                        new_file.append(line)


        with open(f'{nmt_home}/src/NEMAT/run_files/{f}', 'w') as file:
            file.writelines(new_file)

    
def assemble_system(nmt_home):
    nmt = read_input() # Initialize the class with the input parameters
    check_files(nmt, nmt_home) # check if the files are present and correct

    # finally, let's prepare the overall free energy calculation directory structure
    nmt.prepareFreeEnergyDir( )

    """
    ASSEMBLE SYSTEM FOR FEP
    """
    # this command will map the atoms of all edges found in the 'nmt' object
    # bVerbose flag prints the output of the command
    nmt.atom_mapping(bVerbose=True)
    nmt.hybrid_structure_topology(bVerbose=False)
    nmt.assemble_systems( )

def prepare_ligands():
    
    """
    ADD SOLVENT TO LIG
    """
    nmt = read_input() # Initialize the class with the input parameters

    if 'water' in nmt.thermCycleBranches:
        nmt.boxWaterIons(bBoxLig=True,bWatLig=True,bIonLig=True)

def minimization():
    
    """
    ENERGY MINIMIZATION
    """
    nmt = read_input() # Initialize the class with the input parameters

    if 'water' in nmt.thermCycleBranches:
        bLig = True
    else:
        bLig = False
    
    if 'membrane' in nmt.thermCycleBranches:
        bMemb = True
    else:
        bMemb = False

    if 'protein' in nmt.thermCycleBranches:
        bProt = True
    else:
        bProt = False

    nmt.prepare_simulation( simType='em', bProt=bProt, bLig=bLig, bMemb=bMemb)
    nmt.prepare_jobscripts(simType='em', bProt=bProt, bLig=bLig, bMemb=bMemb)

def equilibration():
    
    """
    EQUILIBRATION
    """
    nmt = read_input() # Initialize the class with the input parameters

    if 'water' in nmt.thermCycleBranches:
        bLig = True
    else:
        bLig = False
    
    if 'membrane' in nmt.thermCycleBranches:
        bMemb = True
    else:
        bMemb = False

    if 'protein' in nmt.thermCycleBranches:
        bProt = True
    else:
        bProt = False

    nmt.prepare_simulation( simType='eq', bProt=bProt, bLig=bLig, bMemb=bMemb)
    nmt.prepare_jobscripts(simType='eq', bProt=bProt, bLig=bLig, bMemb=bMemb)


def production():
   
    """
    PRODUCTION
    """
    nmt = read_input() # Initialize the class with the input parameters

    if 'water' in nmt.thermCycleBranches:
        bLig = True
    else:
        bLig = False
    
    if 'membrane' in nmt.thermCycleBranches:
        bMemb = True
    else:
        bMemb = False

    if 'protein' in nmt.thermCycleBranches:
        bProt = True
    else:
        bProt = False

    # create the jobscripts
    nmt.prepare_simulation(simType='md', bProt=bProt, bLig=bLig, bMemb=bMemb)
    nmt.prepare_jobscripts(simType='md', bProt=bProt, bLig=bLig, bMemb=bMemb)

def transitions():

    """
    PREPARE NON EQUILIBRIUM TRANSITIONS
    """
    nmt = read_input() # Initialize the class with the input parameters

    if 'water' in nmt.thermCycleBranches:
        bLig = True
    else:
        bLig = False
    
    if 'membrane' in nmt.thermCycleBranches:
        bMemb = True
    else:
        bMemb = False

    if 'protein' in nmt.thermCycleBranches:
        bProt = True
    else:
        bProt = False

    nmt.prepare_jobscripts(simType='transitions', bProt=bProt, bLig=bLig, bMemb=bMemb)
    nmt.prepare_transitions(bGenTpr=True, bProt=bProt, bLig=bLig, bMemb=bMemb)


def analyse():
    """
    ANALYSIS
    """
    nmt = read_input() # Initialize the class with the input parameters

    if 'water' in nmt.thermCycleBranches:
        bLig = True
    else:
        bLig = False
    
    if 'membrane' in nmt.thermCycleBranches:
        bMemb = True
    else:
        bMemb = False

    if 'protein' in nmt.thermCycleBranches:
        bProt = True
    else:
        bProt = False

    nmt.run_analysis( bVerbose=True, bProt=bProt, bLig=bLig, bMemb=bMemb)
    nmt.analysis_summary()
    nmt.resultsAll.to_csv('results_all.csv')
    print(nmt.resultsSummary)


def track_errors(file):
    """
    TRACK ERRORS
    """

    red = "\033[31m"
    green = "\033[92m"
    yellow = "\033[93m"
    end = "\033[0m"

    with open(file, 'r') as f:
        lines = f.readlines()
        errors = {}
        warnings = {}
        e = False
        w = False
        aux = []
        aux2 = []
        min_err = False
        for i, line in enumerate(lines):
            if line.startswith('Error') or line.startswith('Fatal'):
                e = True
                eline = i
            elif 'Energy minimization has stopped, but the forces have not converged to the requested precision' in line:
                e = True
                min_err = True
                eline = i   
            if e:
                aux.append(line)
                if line == '\n':
                    if min_err:
                        aux.append(f'Use {yellow}nemat atom{end} for a possible solution to this issue.\n\n')
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
            f.write(f'{green}No GROMACS errors found!!{end}\n')
        
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

    
    if len(errors) > 0:
        sys.exit(1)

                
    


if __name__ == '__main__':
    warnings.formatwarning = custom_formatwarning

    args = args_parser()
    if args.step == 'prep':
        print("Assembling system...")
        assemble_system(args.NMT_HOME)
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
        nmt = read_input()
        nmt._results_image()

    elif args.step == 'check':
        # print("Checking input files...")
        nmt = read_input() # Initialize the class with the input parameters
        check_run_files(nmt, args.NMT_HOME) # check if the files are present and correct

    elif args.step == 'update':
        print("Updating input files...")
        nmt = read_input() # Initialize the class with the input parameters
        check_files(nmt, args.NMT_HOME) # check if the files are present and correct
        check_run_files(nmt, args.NMT_HOME)

