.. _installation:

1. Installation
================

This section provides instructions on how to install NEMAT on your HPC system.

Prerequisites
-------------   

Before installing NEMAT, ensure that you have the following prerequisites:
 
- A **SLURM-managed** HPC system
- **GPUs** available for computation (this is not a strict requirement, but it is not realistic (time-wise) to run NEMAT without GPUs)
- **GROMACS** installed on the system (version 2024.2 was used in the development of NEMAT)

Installation Steps
------------------

Download NEMAT from GitHub using:

``git clone https://github.com/QTC-IQAC/NEMAT.git``

First set up env:

``cd NEMAT``

``bash bin/set_env.sh``

If *mamba* is available, the environment will be created with mamba. If not, *conda* will be used. Make sure that any of these are loaded before running the setup script (``module load mamba``). Then give execute permissions to the NEMAT executable

``chmod +x $NMT_HOME/bin/nemat``

If using nemat is not available, try updating the *.bashrc* file:

``source ~/.bashrc``

Verify the installation by running:

``nemat``

This should display the NEMAT help message, confirming that the installation was successful.
