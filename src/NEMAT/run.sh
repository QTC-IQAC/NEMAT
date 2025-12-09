#!/bin/bash

wp=$1
step=$2
job_id=$3

current_dir=$(pwd)

cd $(pwd)/$wp/${step}_jobscripts

rm -f job_*.out # remove old output files

if [ -n "$job_id" ]; then
    sbatch --dependency=afterok:$job_id submit_jobs.sh
else
    sbatch submit_jobs.sh
fi

cd $current_dir
