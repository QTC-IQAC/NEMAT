.. _ligands:

5. Prepare the ligands.
========================

5.1. Obtaining the reference ligand: `ref_lig.pdb`.
----------------------------------------------------

First, we need to align the reference protein-ligand system (i.e., a crystallographic structure from the PDB containing the protein and the docked ligand) with the newly generated GROMACS system. Use VMD or any aligning tool to align the two proteins. For VMD, you could do:

1. Load the two proteins. In this case: ``system.gro`` and ``prot_lig.pdb``. 
2. Go to ``Extensions > Analysis > RMSD calculator``.  This will display a new window.
3. At the top left box, type ``name CA``.
4. Unclick the option *Backbone only*.
5. Click *Align* to align the two systems.
6. Save the new ligand coordinates.

.. warning::

   It is important that the GROMACS system (`system.gro`) is marked with the option *"T"* on the VMD main page. If not, the whole system will be aligned to the protein and not the other way around.

Then extract the ligand, which will serve as a reference for aligning the other ligands. Save it as *ref_lig.pdb*.


5.2. Aligning the ligands.
--------------------------

Add hydrogens to the reference ligand and to the rest (for example, using `CHARMM-GUI <https://www.charmm-gui.org/>`_). You can manually align the ligands and directly save the *mol2* files at the *ligands* folder.

If you have *pdb* files of the ligands, the ``align.sh`` file might be useful. Save all the *pdb* files of your ligands inside the "*/ligands/ligands*" folder and the *ref_ligand.pdb* on the "/ligands" folder. Then use:

``cd ligands``
``bash align.sh``

This will generate ``ligands.sdf`` and all the necessary files: it will align the ligands with the reference ligand and then generate *mol2* files for every ligand. 

You can use the *ligands.sdf* file to both visualize all the ligands at once and, for example, to use some program such as `openFE <https://colab.research.google.com/github/OpenFreeEnergy/ExampleNotebooks/blob/main/openmm_rbfe/OpenFE_showcase_1_RBFE_of_T4lysozyme.ipynb>`_ to generate a mapping of the ligands and determine the possible edges.

The *ligands* folder should contain (at least) the *mol2* of all the ligands. The whole folder, including the reference ligand and the alignment script, should look like this: 

.. code-block:: text

    ligands
      |  |
      |  |-- ligands
      |       |-- ligand1.pdb
      |       |-- ligand2.pdb
      |       |-- ...
      |
      |-- ref_lig.pdb
      |-- ligands.sdf
      |-- align.sh
      |-- ligand1.mol2
      |-- ligand2.mol2
      |-- ...

.. note::

   When starting a NEMAT run, some dummy files are inside the *ligands* and *lignads/ligands* folders to help the user know where every kind of file should be placed. Remove them before aligning with ``align.sh``. 

   Check that the ligand alignment is correct. If the molecule is small, it is possible that something went wrong. You can manually align the ligands and directly save the *mol2* files at the *ligands* folder. 
