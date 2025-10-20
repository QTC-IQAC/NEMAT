#!/bin/bash
#SBATCH --job-name=NEMAT_min
#SBATCH -e logs/min.err
#SBATCH -o logs/min.log
#SBATCH -c 1
#SBATCH -N 1
#SBATCH -n 8
#SBATCH -p long
#SBATCH --gres=gpu:1
python $NMT_HOME/src/NEMAT/file_gestor.py --step min