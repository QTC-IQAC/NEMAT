#!/bin/bash
#SBATCH --job-name=NEMAT_an
#SBATCH -e logs/analysis.err
#SBATCH -o logs/analysis.log
#SBATCH -c 1
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -p gpu
#SBATCH --gres=gpu:1
#SBATCH -t 00-01:00

wp=$1
if [ -z "$wp" ]; then
    echo "Usage: $0 <work_dir>"
    exit 1
fi

module load gromacs-plumed/2024.2-2.9.2

python NEMAT/file_gestor.py --step analysis
bash utils/extractPlots.sh $wp