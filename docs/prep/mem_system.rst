.. _mem_system:

4. Prepare the membrane system. 
===============================

Prepare a bilayer membrane system that is consistent with the membrane-embedded protein system. This means using the same kind of water (TP3, OPC...), the same AMBER FF, and the same lipids that are on the membrane (usually only POPC). 

The *XY* size of the box can be of approximately 4 nm (40 Angstroms), which means 24 POPCs per layer. For very large ligands (or peptides), this must be increased, which will only have an effect on the running time.  

**A standard POPC membrane is provided and can be used. The size of the membrane is 4 nm (XY) and the ions used are Na+ Cl-. If you use this membrane, you can skip to the** :ref:`next section <ligands>`.

4.1. Create the membrane system using CHARMM-GUI.
-------------------------------------------------

As in the MEP system (see :ref:`MEP system <mep_system>`), take from the *gromacs* folder and change the *step5_input.gro* file name for *membrane.gro* and the *topol.top* for *membrane.top*. Add them to the ``membrane`` folder.

The *membrane* folder should contain at least the following:

.. code-block:: text

    membrane
      |  |
      |  |-- toppar
      |  |-- membrane.gro
      |  |-- membrane.top

4.2. Using a different method.
--------------------------------

NEMAT searches for the files ``membrane.top`` (which references files inside the ``toppar`` folder), ``membrane.gro``, and the folder ``toppar``. Therefore, any set of files following this structure is a valid input for NEMAT. 

.. note::

   Actually, you could just change a force field folder’s name to ``toppar`` 
   and update the ``#include`` inside the topology file. This would still 
   provide a valid input for NEMAT.


If you are using a custom force field, it is recommended to use the same for the MEP system. 
