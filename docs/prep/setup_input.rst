.. _setup_input:

7. Set up of NEMAT: the ``input.yaml`` file
===========================================

An example of an input for the FEP simulation can be found in ``input.yaml``:

.. code-block:: yaml

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


Remember to load GROMACS using ``JOBmodules`` if it's a module or manually. More modules can be loaded, but only GROMACS is strictly necessary. 

On the other hand, it is important that the GROMACS executable ``gmx`` exists. If you only have ``gmx_mpi`` as an executable, the program will fail.

Other options for the input file are:

- **thermCycleBranches**  : list (water, membrane, protein); if you want to run only some branches of the thermodynamic cycle, include them here. For example, to run only the water and protein branches, use ``thermCycleBranches: ['water', 'protein']``.
- **color_f**             : string; Hexcode of the color for the forward free energy lines in the results plot. Default is ``'#008080'``.
- **color_b**             : string; Hexcode of the color for the backward free energy lines in the results plot. Default is ``'#ff8559'``.
- **boxshape**            : string; Shape of the simulation box for the water system. Options are 'rectangular', 'dodecahedron' or 'triclinic'. Default is ``'dodecahedron'``.
- **boxd**                : float; Minimum distance between the solute and the box edge for the water system. Default is 1.5.
- **water**               : string; Water model to use in the simulations. Default is ``'tip3p'``.
- **conc**                : float; Concentration of ions to add to the systems (in M). Default is 0.15.
- **bootstrap**           : int; Number of bootstrap resamplings to perform in the analysis. Default is 100.
- **chargeType**          : string; Type of charge to use for the ligands. Default is ``'bcc'``.
- **JOBmem**              : string; Amount of memory to request for the simulation jobs. Default is ``''``.
- **JOBbackup**           : bool; If True, save gromacs backup files for transitions. Default is False.

7.1. Job script setup.
-----------------------

Aside from the obvious parameters, the following things may be of your interest.

* ``JOBsimtime`` is the time that will be used for the minimization, equilibration, production, and transition jobs. If it is not set, no time will appear in these jobs. 
* ``JOBmpi``, depending on your GROMACS installation, you may have to explicitly state ``-ntmpi 1`` to avoid a ranks error. This option does it for you. 
* You can always add whatever you want to the ``JOBgmx`` command if your cluster has a specific problem. For example, it is a good idea to add *-maxh 72* if you set ``JOBsimtime`` to 3 days.

7.2. Production and Transitions setup.
---------------------------------------

The production will save ``saveFrames`` frames. This means that, at maximum, you will be able to perform ``saveFrames`` transitions. 

The number of transitions is selected with ``frameNum``. If this is bigger than ``saveFrames``, there will be ``saveFrame`` transitions, which is the maximum available. If not, the ``frameNum`` transitions will be the last ``frameNum``  saved frames. 

In case that ``tstart`` is defined (recommended), the ``frameNum`` transitions will be evenly spaced from ``tstart`` to the total simulation time. If it can not be evenly spaced, NEMAT will take as much evenly spaced transitions as possible and select the remaining ones randomly. For example, if I have a simulation of 20 ns, ``saveFrame = 200``, ``frameNum = 100``, and ``tstart = 5 ns``, this would lead to 150 available frames for transitions, which is not divisible by 100. Then 75 evenly spaced frames would be taken, and 25 out of the remaining possible frames would be selected at random. The selected frames can be found inside *your_workpath/edge_a_b/system/runX/transitions/extracted_frames.txt*

7.3. Analysis setup.
----------------------

The analysis parameters are only needed for the analysis step. This means that you can modify them even after the transitions have run. 

The analysis setup aims to be as flexible as possible to enable the user to perform as many different analysis as possible without rerunning anything. 

Go to the `analysis section <analysis>` for more information about the analysis parameters. 