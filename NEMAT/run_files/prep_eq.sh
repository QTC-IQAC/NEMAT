#!/bin/bash
#SBATCH --job-name=NEMAT_eq
#SBATCH -e logs/eq.err
#SBATCH -o logs/eq.log
#SBATCH -c 1
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -p gpu
#SBATCH --gres=gpu:1
#SBATCH -t 00-01:00

module load gromacs-plumed/2024.2-2.9.2

python NEMAT/file_gestor.py --step eq