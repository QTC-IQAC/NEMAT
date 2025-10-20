#!/bin/bash
#SBATCH --job-name=NEMAT_prep
#SBATCH -e logs/prep.err
#SBATCH -o logs/prep.log
#SBATCH -c 1
#SBATCH -N 1
#SBATCH -n 8
#SBATCH -p long
#SBATCH --gres=gpu:1
python $NMT_HOME/src/NEMAT/prepare_inputs_md.py --NMT_HOME $NMT_HOME
python $NMT_HOME/src/NEMAT/file_gestor.py --step prep --NMT_HOME $NMT_HOME