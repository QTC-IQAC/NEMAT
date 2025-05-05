#! /bin/bash

# Checks how many of the slurm files in a directory have finished successfully

jobs_dir=$1

current_dir=$(pwd)

cd $jobs_dir

for file in slurm-* 
do 
    grep "GROMACS reminds you:" $file
done > temp.temp

wc -l temp.temp

rm -f temp.temp

cd $current_dir