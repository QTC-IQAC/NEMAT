#!/bin/bash
#SBATCH --job-name=NEMAT_eq
#SBATCH -e logs/eq.err
#SBATCH -o logs/eq.log
#SBATCH -c 1
#SBATCH -N 1
#SBATCH -n 8
#SBATCH -p long
#SBATCH --gres=gpu:1
python $NMT_HOME/src/NEMAT/file_gestor.py --step eq