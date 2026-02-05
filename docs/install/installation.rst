.. _installation:

1. Installation
================

This section provides instructions on how to install NEMAT on your HPC system.

1.1. Prerequisites
-------------------   

Before installing NEMAT, ensure that you have the following prerequisites:
 
- A **SLURM-managed** HPC system
- **GPUs** available for computation (this is not a strict requirement, but it is not realistic (time-wise) to run NEMAT without GPUs)
- **GROMACS** installed on the system (version 2024.2 was used in the development of NEMAT)

OPTIONAL:

- **GROMACS** with multidir for parallelization of the transitions. Make sure that a ``gmx`` executable exists in addition to the ``gmx_mpi`` executable.

1.2. Installation Steps
------------------------

1.2.1. Download NEMAT version (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the desired version (X.Y, i.e., 0.9) from the NEMAT GitHub:

``wget https://github.com/QTC-IQAC/NEMAT/archive/refs/tags/vX.Y.tar.gz -O NEMAT-vX.Y.tar.gz``

Then unpack with:

``tar -xzf NEMAT-vX.Y.tar.gz``

Then enter the nemat directory with

``cd NEMAT-X.Y``

.. code-block:: text

    For the LAST version (0.9):

    wget https://github.com/QTC-IQAC/NEMAT/archive/refs/tags/v0.9.tar.gz -O NEMAT-v0.9.tar.gz
    tar -xzf NEMAT-v0.9.tar.gz
    cd NEMAT-0.9

First set up env:

``bash bin/set_env.sh``

If *mamba* is available, the environment will be created with mamba. If not, *conda* will be used. Make sure that any of these are loaded before running the setup script (``module load mamba``). Then, give execute permissions to the NEMAT executable

``chmod +x $NMT_HOME/bin/nemat``

If using nemat is not available, try updating the *.bashrc* file:

``source ~/.bashrc``

Verify the installation by activating the environment and then running:

``nemat``

This should display the NEMAT help message, confirming that the installation was successful.



1.2.2. Download NEMAT on the current state
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download NEMAT from GitHub using:

``git clone https://github.com/QTC-IQAC/NEMAT.git``

``cd NEMAT``

First set up env:

``bash bin/set_env.sh``

If *mamba* is available, the environment will be created with mamba. If not, *conda* will be used. Make sure that any of these are loaded before running the setup script (``module load mamba``). Then, give execute permissions to the NEMAT executable

``chmod +x $NMT_HOME/bin/nemat``

If using nemat is not available, try updating the *.bashrc* file:

``source ~/.bashrc``

Verify the installation by activating the environment and then running:

``nemat``

This should display the NEMAT help message, confirming that the installation was successful.
