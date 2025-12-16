[![DOI](https://img.shields.io/badge/DOI-10.1234%2Fabcd1234-blue)](https://www.biorxiv.org/content/10.64898/2025.12.09.692605v1) ![SLURM Compatible](https://img.shields.io/badge/HPC%20scheduler-SLURM-green) [![Documentation Status](https://readthedocs.org/projects/NEMAT/badge/?version=latest)](https://nemat.readthedocs.io/en/latest/)



# NEMAT: An Automated Non-Equilibrium Free-Energy Framework for Predicting Ligand Affinity in Membrane Proteins

**NEMAT** (Non-Equilibrium Membrane Alchemical Transformations) is an open-source framework designed to make **non-equilibrium free-energy calculations for ligand binding in membrane proteins accessible, reproducible, and automated.**

Built around established molecular simulation workflows, NEMAT guides users through the full process—from system preparation and execution to analysis—enabling the estimation of ligand binding affinities directly from non-equilibrium molecular dynamics simulations. It is particularly tailored for membrane protein systems, where setup and analysis are often complex and error-prone.

By providing a structured, modular workflow, NEMAT reduces manual intervention, improves consistency across simulations, and allows researchers to focus on interpreting results rather than managing infrastructure.

For detailed instructions on **execution**, **configuration**, **available options**, and **tutorials**, please refer to the [project documentation].

[project documentation]: https://nemat.readthedocs.io/en/latest/

# 1. Install 

Download NEMAT from GitHub using:

```bash
git clone https://github.com/QTC-IQAC/NEMAT.git
```

First set up env:

```bash
cd NEMAT
bash bin/set_env.sh
```

Then give execute permissions to the NEMAT executable
```bash
chmod +x $NMT_HOME/bin/nemat
```

If using `nemat` is not available, try updating the `.bashrc` file:

```bash
source ~/.bashrc
```

# Prepare directory for a NEMAT run:  `nemat start`.

Create a new **empty** directory and, inside the directory, use:

```bash
nemat start 
```

This will copy into your directory the following elements:

1. A folder named `membrane`
2. A folder named `proteins`
3. A folder named `mdppath`
4. A folder named `ligands`
5. A folder named `logs`
6. A file named `input.yaml`

 Now you have the structure to start a NEMAT run. Create the inputs for ligands, membrane, and protein as explained in the [documentation].

 [documentation]: https://nemat.readthedocs.io/en/latest/prep/index.html#preparation 


# Set up of NEMAT: the `input.yaml` file

An example of an input for the FEP simulation can be found in `input.yaml`:

```yaml
##############################
#       PREPARE INPUTS       #
##############################

inputDirName: 'input_name'             # path to the directory where the input files will be located. 
proteinName: 'prot_name'               # name of the protein in inputDirName/proteins that will be used.


##############################
#      SIMULATION INPUTS     #
##############################


workPath: 'workpath_name'                # path to the directory where the simulations will run
replicas: 3                              # set the number of replicas (several repetitions of calculation are useful to obtain reliable statistics)
edges:                                   # List of lists containing the edges.  
  - ['small_molec_1', 'small_molec_2']   # without the .mol2 
  - ['small_molec_1', 'small_molec_3']
  - ['small_molec_2', 'small_molec_3']

pname: 'NA'                              # Which positive ions to use in the ligand simulations
nname: 'CL'                              # Which negative ions to use in the ligand simulations 
# slotsToUse: 6                          # Use if you want to limit the number of jobs running at the same time in the cluster.
saveFrames: 200                          # Number of frames to save in the production MD. The default is 400 frames.
frameNum: 100                            # Number of frames to extract to make transitions. The default upper limit is frameNum.
temp: 298                                # Temperature of the systems.
units: 'kcal'                            # Units for the free energy calculations ("kJ" for kJ/mol or "kcal" for kcal/mol)
mdtime: 20                               # Production MD time in ns. If you want to use the time in the mdp files, don't set this parameter or set it to None.
titime: 0.2                              # Transition MD time in ns. If you want to use the time in the mdp files, don't set this parameter or set it to None.
tstart: 5                                # Starting time (in ns) to extract frames from the production MD for transition simulations. If None, tstart will be determined by frameNum.


##############################
#    JOB SUBMISSION INPUTS   #
##############################

JOBsimcpu: 24                            # Number of CPUs to use for the simulation jobs
JOBmodules:                              # List of modules to load for the simulation jobs
  - 'gromacs-plumed/2024.2-2.9.2'  
JOBgmx: 'gmx mdrun -maxh 72'             # Command to run the simulation jobs
JOBpartition: 'gpu'                      # Partition to use for the simulation jobs
JOBsimtime: '3-00:00'                    # Time limit for the simulation jobs. Can be set to none.
JOBmpi: False                            # Set to True if you want to specifically display -ntmpi 1 (solves problem of rank division)
JOBexport:                               # List of environment variables to export for the simulation jobs (the jobs will include "export SET_SOME_VAR=1")
  - 'SET_SOME_VAR=1'

JOBsource:                               # List of source files to run before the simulation jobs (the jobs will include "source file.sh")
  - 'file.sh'                          
              
JOBcommands:                             # List of commands to run before the simulation jobs 
  - 'conda activate NEMAT'    
  
  
##############################
#          ANALYSIS          #
##############################

precision: 1                             # Number of decimal places to use in the analysis output (results.png)
framesAnalysis: [start_frame, end_frame] # List of frames to analyze. If you want to analyze all frames, ignore this field. 
nframesAnalysis: 80                      # Number of frames to use in the analysis (max frameNum, which is the number of transitions).
spacedFrames: False                      # if True, nframesAnalysis are evenly spaced. If False, all frames in nframesAnalysis are selected

```

Remember to load GROMACS using `JOBmodules` if it's a module or manually. More modules can be loaded, but only GROMACS is strictly necessary. 

On the other hand, it is important that the GROMACS executable `gmx` exists. If you only have `gmx_mpi` as an executable, the program will fail.

See all options [here].

[here]: https://nemat.readthedocs.io/en/latest/prep/setup_input.html#set-up-of-nemat-the-input-yaml-file

# Running NEMAT. 

Use `nemat` or `nemat help` to display all the options. You can use `nemat wf` to display a simplified workflow for a NEMAT run:

```
>>> submit this steps sequentially for a complete NEMAT run... ([ ]  <-- You are here!  marks the last completed step)

	 1. Prepare the system        : nemat prep

   [ 2. Prepare minimization      : nemat prep_min ] 	 <-- You are here!

	 3. Run minimization          : nemat run_min

	 4. Prepare equilibration     : nemat prep_eq
	 5. Run equilibration         : nemat run_eq

	 6. Prepare production        : nemat prep_md
	 7. Run production            : nemat run_md

	 8. Prepare transitions       : nemat prep_ti
	 9. Run transitions           : nemat run_ti

	10. Analyze results           : nemat analyze

```

This is the order to run from start to finish a complete run. For more details on every step, refer to the [executing documentation].

[executing documentation]: https://nemat.readthedocs.io/en/latest/run/run_nemat.html#running-nemat 


# Reproduce the results of the paper.

NEMAT allows you to create a starting directory with the precomputed input files used in the paper (DOI (preprint): https://www.biorxiv.org/content/10.64898/2025.12.09.692605v1). Follow these steps:

1. Create a new directory (for example, nemat\_test).
2. `cd nemat_test`
3. `nemat example`
4. You can now follow the steps from section 8.

In case you want to reproduce the 6a analogues (Tab. 2), you must change the edges in `input.yaml` with:

```bash
edges:                                 # List of lists containing the edges.  
  - ['6a', '6i']
  - ['6a', '6f']
  - ['6a', '6h']
  - ['6a', '6m']
  - ['6a', '6g']
  - ['6a', '6l']
  - ['6a', '6j']
  - ['6a', '6n']  
```


# License

This work is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0) license.

You are free to:

* Share — copy and redistribute the material in any medium or format

Under the following terms:

* Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.

* NonCommercial — You may not use the material for commercial purposes.

* NoDerivatives — If you remix, transform, or build upon the material, you may not distribute the modified material.

* No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
