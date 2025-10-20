#!/bin/bash
#SBATCH --job-name=NEMAT_ti
#SBATCH -e logs/ti.err
#SBATCH -o logs/ti.log
#SBATCH -c 1
#SBATCH -N 1
#SBATCH -n 8
#SBATCH -p long
#SBATCH --gres=gpu:1
python $NMT_HOME/src/NEMAT/file_gestor.py --step ti