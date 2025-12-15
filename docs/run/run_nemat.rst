.. _run_nemat:

8. Running NEMAT.
====================

Use ``nemat`` or ``nemat help`` to display all the options. You can use ``nemat wf`` to display a simplified workflow for a NEMAT run:

.. code-block:: text

    >>> submit this steps sequentially for a complete NEMAT run... ([ ]  <-- You are here!  marks the last completed step)

	 1. Prepare the system        : nemat prep

       [ 2. Prepare minimization      : nemat prep_min ]  <-- You are here!

	 3. Run minimization          : nemat run_min

	 4. Prepare equilibration     : nemat prep_eq
	 5. Run equilibration         : nemat run_eq

	 6. Prepare production        : nemat prep_md
	 7. Run production            : nemat run_md

	 8. Prepare transitions       : nemat prep_ti
	 9. Run transitions           : nemat run_ti

	10. Analyze results           : nemat analyze

.. note::

    You can always use `nemat check_{step}` to display the warnings and errors that occurred during the preparation of a specific step (*prep*, *min*, *eq*, *md*, *ti*, or *analyze*).

    This will display the warnings and errors **produced by GROMACS**. Each warning and error is titled as error_{line} or warning_{line} where *line* is the line of the original file where the error occurred.

    *IMPORTANT: the check file only searches errors produced by GROMACS. If the program has failed before completing every step, you won't be able to use* ``check_{step}`` *to find the error. Look at the corresponding log in the* ``logs`` *folder.*


8.1. Prepare the system. 
------------------------

First of all, generate the structure of the simulation results and also process the ligand with *acpype* (creates GROMACS files of the ligands):

``nemat prep``

Check the new input folder that was created. It must contain:

1. A folder named *ligands* containing all the ligands involved in the edges.
2. A folder named *proteins* containing the protein files.
3. A folder named *membrane* containing the membrane files.
4. A folder named *mdppath* containing the *mpd* files for the simulations.

Also, a workpath folder has been created: 


.. code-block:: text

    /path/to/workpath/
    |
    |--edge_lig1_lig2
    |--|--water
    |--|--|--stateA # ligand 1 (lambda 0)
    |--|--|--|--run1/2/3 # number of replicas
    |--|--|--|--|--em/eq/md/transitions
    |--|--|--stateB # ligand 2 (lambda 1)
    |--|--|--|--run1/2/3
    |--|--|--|--|--em/eq/md/transitions
    |--|--membrane
    |--|--|--stateA
    |--|--|--|--run1/2/3
    |--|--|--|--|--em/eq/md/transitions
    |--|--|--stateB
    |--|--|--|--run1/2/3
    |--|--|--|--|--em/eq/md/transitions
    |--|--protein
    |--|--|--stateA
    |--|--|--|--run1/2/3
    |--|--|--|--|--em/eq/md/transitions
    |--|--|--stateB
    |--|--|--|--run1/2/3
    |--|--|--|--|--em/eq/md/transitions
    |--|--hybridStrTop # hybrid topology of lig1 and lig2
    |--edge_...


Using ``nemat check_prep`` will print a summary of the system parameters. If you want to change any parameter of the ``input.yaml`` file, you can now use ``nemat update``, which will check that all involved files are corrected and will print the same summary:

.. code-block:: text

    -->-->--> System check <--<--<--

    -- SIMULATION TIMES (ns) --
    +------------+------------+------------+------------+
    |            | eq         | md         | ti         |
    +------------+------------+------------+------------+
    | water      | 0.5        | 20         | 0.2        |
    | membrane   | 1.5        | 20         | 0.2        |
    | protein    | 1.5        | 20         | 0.2        |
    +------------+------------+------------+------------+

    -- INFO --

    |	--> Frames saved in md          : 200
    |	--> Number of transitions       : 100
    |	--> dt transitions              : 0.15 ns
    |		--> This means that the first transition frame would be 50 (at 5.0 ns).
    |
    |	--> Transitions for analysis    : 100
    |	--> Spaced frames for analysis  : True
    |
    |	--> Replicas per system         : 1
    |	--> Simulations will run for 1 edges.
    |		--> This means 6 jobs per step.
    |
    |	--> Edges:
            * edge_a_b
    |
    |	--> Temperature                 : 298 K
    |	--> Charge type                 : bcc
    |	--> Results will be in          : kcal
    |
    |	--> CPUs per job                : 8 
    |	--> GPU enabled                 : True.



8.2. Minimization.
-------------------

You can prepare the minimization files by using:

``nemat prep_min``

This will generate all the job scripts for the SLURM cluster. The generated jobs (``jobscript{n}``) and submission job (``submit_jobs.sh``) can be found at your workpath, where you will find a folder named ``em_jobscripts``.  It is highly recommended to check if there were any GROMACS errors when the minimization preparation ends:

``nemat check_min``

To submit the job array:

``nemat run_min``

Or, if you are sure that the preparation will be successful, you can use the job ID of the preparation job to submit with an "afterok" dependency the minimization jobs:

``nemat run_min job_id``

When the jobs finish running, you may use 

``nemat s_min``

to check if all the jobs have been successful. If not, the program will indicate which jobs (*job_num*) failed so you can look at the corresponding logs (at *your_workpath/em_jobscripts*, named ``job_{job_id}_{job_num}.out``). 


8.2.1. Errors during minimization.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During the minimization is where most of the GROMACS errors may occur due to placing the hybrid small molecule in a precoumputed system. Since the protein pocket is usually "empty", the most problematic systems are usually the membrane ones. The most common errors are:

.. warning::

    Energy minimization has stopped, but the forces have not converged to the
    requested precision Fmax < 1000 (which may not be possible for your system).
    It stopped because the algorithm tried to make a new step whose size was too
    small, or there was no change in the energy since the last step. Either way, we
    regard the minimization as converged to within the available machine
    precision, given your starting configuration and EM parameters.

Even though this is not explicitly a GROMACS error, this must be avoided at all costs. Usually, this will lead to something like:

.. code-block:: text
    
    Potential Energy  =  4.8533396e+09
    Maximum force     =  1.2402948e+12 on atom 8201
    Norm of force     =  3.6336824e+09

Which logically will eventually crash during the equilibration. This error occurs because the ligand was placed to near from an existing atom but not close enough for the system to crash. Luckily, this error is usually solvable. NEMAT provides a possible solution:

1. Use ``nemat atom``. This will copy `find_atom.tcl` in your directory and provide you with simple instructions:

.. code-block:: text

    Use it in VMD to find atom indices as follows:
	 > Open the gro file that fails (e.g., membrane.gro) with VMD
	 > Open find_atoms.tcl and change the atom index on the first line (0-based)
	 > Then, at the VMD command prompt, type: source find_atom.tcl
	 > The atom will be highlighted in red. Move it to avoid crashes


2. Inside ``find_atoms.tcl`` find ``set atomIndex 118`` (line 2) and change the atom index for the index that GROMACS provided you (i.e., in our example, is atom 8201, therefore we would set ``set atomIndex 8200`` since it's 0-based).
3. Go to *your_workpath/edge_that_failed/system*. Here is where the *.gro* file that needs to be modified is. 
4. Open this file with VMD and source the *tcl* file. 
5. Manually correct the atom(s) position(s). Don't worry if the structure is no exactly the one previous to the changes, the force field will do its work and reshape it during the minimization.
6. Save the new *gro* file and replace the original one. 

Now change your input file to avoid rerunning things that are errorless:


1. Comment the edges that are okay:

.. code-block:: yaml

    edges:                                   # List of lists containing the edges.  
        # - ['small_molec_1', 'small_molec_2']   # without the .mol2 
        - ['small_molec_1', 'small_molec_3']
        # - ['small_molec_2', 'small_molec_3']

2.  Use `thermCycleBranches` to select only the branch that failed.

.. code-block:: yaml

    thermCycleBranches: 
        - 'membrane'                         # Select only this branch because we are fixing it. 

3. Update with the new parameters.

``nemat update`` 

Now restart the minimization. 

.. important::

   Remember to change back the parameters of ``input.yaml`` after running the new minimization. Then use again ``nemat update``.


8.3. Equilibration.
--------------------

You can prepare the equilibration files by using:

``nemat prep_eq``

This will generate all the job scripts for the SLURM cluster. The generated jobs (``jobscript{n}``) and submission job (``submit_jobs.sh``) can be found at your workpath, where you will find a folder named ``eq_jobscripts``.  It is highly recommended to check if there were any GROMACS errors when the equilibration preparation ends:

``nemat check_eq``

To submit the job array:

``nemat run_eq``

Or, if you are sure that the preparation will be successful, you can use the job ID of the preparation job to submit with an "afterok" dependency the equilibration jobs:

``nemat run_eq job_id``

When the jobs finish running, you may use 

``nemat s_eq``

to check if all the jobs have been successful. If not, the program will indicate which jobs (*job_num*) failed so you can look at the corresponding logs (at *your_workpath/eq_jobscripts*, named ``job_{job_id}_{job_num}.out``).

8.4. Production.
-----------------

You can prepare the production files by using:

``nemat prep_md``

This will generate all the job scripts for the SLURM cluster. The generated jobs (``jobscript{n}``) and submission job (``submit_jobs.sh``) can be found at your workpath, where you will find a folder named ``md_jobscripts``.  It is highly recommended to check if there were any GROMACS errors when the production preparation ends:

``nemat check_md``

To submit the job array:

``nemat run_md``

Or, if you are sure that the preparation will be successful, you can use the job ID of the preparation job to submit with an "afterok" dependency the production jobs:

``nemat run_md job_id``

When the jobs finish running, you may use 

``nemat s_md``

to check if all the jobs have been successful. If not, the program will indicate which jobs (*job_num*) failed so you can look at the corresponding logs (at *your_workpath/md_jobscripts*, named ``job_{job_id}_{job_num}.out``). 


8.5. Transitions.
-------------------

You can prepare the production files by using:

``nemat prep_ti``

This will generate all the job scripts for the SLURM cluster. The generated jobs (``jobscript{n}``) and submission job (``submit_jobs.sh``) can be found at your workpath, where you will find a folder named ``transition_jobscripts``.  It is highly recommended to check if there were any GROMACS errors when the transition preparation ends:

``nemat check_ti``

To submit the job array:

``nemat run_ti``

Or, if you are sure that the preparation will be successful (this preparation will last for longer, so this is recommended), you can use the job ID of the preparation job to submit with an "afterok" dependency the transition jobs:

``nemat run_ti job_id``

When the jobs finish running, you may use 

``nemat s_ti``

to check if all the jobs have been successful. If not, the program will indicate which jobs (*job_num*) failed so you can look at the corresponding logs (at *your_workpath/transition_jobscripts*, named ``job_{job_id}_{job_num}.out``). 


8.5.1. Rerun transitions in a different directory: `nemat copy`.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``nemat copy`` option enables the user to copy a directory up to a certain step to another directory. This might be useful if you want, for example, to use the already run dynamics, but increase the number of transitions. 

After using ``nemat copy`` **from the directory you want to copy**, you will be prompted for:

1. The destination directory (absolute path to an empty directory).
2. Up to which level you want to copy (eq, md, or all)

Then, NEMAT will:

* Copy the workpath up to the specific level.
* Copy the input folder.
* Create a logs folder.
* Copy the ``input.yaml`` from the source.

This is enough to run anything above ``nemat prep``. Back to the example, after doing the copy, we would change ``input.yaml`` (increase ``frameNum``) and then continue with ``nemat update``  (to update the new parameter) and, finally, ``nemat prep_ti``....



