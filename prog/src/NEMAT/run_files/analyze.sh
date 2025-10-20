#!/bin/bash
#SBATCH --job-name=NEMAT_an
#SBATCH -e logs/analysis.err
#SBATCH -o logs/analysis.log
#SBATCH -c 1
#SBATCH -N 1
#SBATCH -n 8
#SBATCH -p long
#SBATCH --gres=gpu:1
wp=$1
if [ -z "$wp" ]; then
    echo "Usage: $0 <work_dir>"
    exit 1
fi
python $NMT_HOME/src/NEMAT/file_gestor.py --step analysis
bash $NMT_HOME/src/utils/extractPlots.sh $wp