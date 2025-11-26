#!/bin/bash

wp=$1
step=$2

current_dir=$(pwd)

cd $(pwd)/$wp/${step}_jobscripts

sbatch submit_jobs.sh

cd $current_dir
