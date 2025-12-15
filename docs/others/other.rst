.. _other:

10. Other features.
====================

10.1. Clean backup files: ``nemat clean``.
------------------------------------------

Since multiple edges can be run at once, the number of useless backup files generated can grow quite high. Hence, you can use ``nemat clean`` to erase all backup files. If you do so, a message will be prompted indicating how much space the files occupy and how many files there are. If you choose to remove them, all of them will be erased.

10.2. Reset run: ``nemat new``.
---------------------------------

In case you need to start your run again (for example, you find an error), using ``nemat new`` will reset the workspace so that you need to start from the preparation of the system but maintaining all the other files (like ``input.yaml``).

10.3. Changing the name of the directory.
------------------------------------------

If you rename the directory where you are running NEMAT, trying to run anything will cause an error since the paths of the topology are for the other directory. You must run 

``nemat prep``

before continuing with anything else, to ensure that all the internal paths are correct. Using ``nemat update`` is not possible here. 

``nemat update`` is useful in the following contexts:

1. You change a parameter that affects an _mdp_ file (``mdtime``, ``titime``)
2. You change a parameter that affects the SLURM parameters (``JOBsimtime``)

Elsewhere, the parameters will be automatically updated when using any NEMAT command (for example, when changing analysis parameters, you don't need to update).