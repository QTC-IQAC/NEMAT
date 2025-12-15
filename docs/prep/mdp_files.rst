.. _mdpfiles:

6. About the *mdp* files
=========================

There are some things that may be difficult to track about the *mdp* files. One of them is the ``tc-grps`` and how they are defined. For the protein we have:

.. code-block:: text

    tc-grps = PROT MEMB SOLV ION

Where SOLV (for solvent) includes the water and the ions, MEMB is the membrane and includes POPC and other lipids (if present), and SOLU (for solute) is the protein and the ligand. On the ``_prepare_prot_tpr()`` and ``_prepare_memb_tpr()`` functions from ``src/NEMAT/nemat.py``, an index is generated and used in the ``grompp`` automatically. If you are having problems, look there :).

Again, the program assumes that the input files were generated using `CHARMM-GUI <https://www.charmm-gui.org/>`_. For the membrane, we have:

.. code-block:: text

    tc_grps = MEMB SOLV LIG

Which is as stated before, but now the ligand, since it's the only solute, is named LIG.

The default *mdp* files are stored in the *mdppath* folder. This folder contains:

1. Minimization files for the protein, the ligand, and the membrane systems. These are named as "`prot_em_l0.mdp`".
2. Equilibration files for  the protein (6), the ligand (1), and the membrane (6) systems. These are named as "`prot_eq(n)\_l0.mdp`" where :math:`n \in [1,6]`.
3. Production files for the protein, the ligand, and the membrane systems. They are named as "`prot_md_l0.mdp`". 
4. Finally, the transitions files are named as "`prot_ti_l0.mdp`".

.. note::

   If you are using your own *mdp* files, don't forget to add the free energy inputs to all the *mdp* files. At least the ``init-lambda`` parameter is needed to indicate if the ligand is in state A or B. At the transitions, the other parameters become relevant:
   
   .. code-block:: text

        ; Free energy control stuff
        free-energy = yes
        init-lambda = 0 ; 0 for state A and 1 for state B
        delta-lambda = 0
        sc-alpha = 0.3
        sc-sigma = 0.25
        sc-power = 1
        sc-coul = yes

