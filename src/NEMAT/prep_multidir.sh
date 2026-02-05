#!/bin/bash

path=$1
n_transitions=$2
cwd=$(pwd)
#prepare dir
mkdir -p ${path}/multidir
for i in $(seq 0 $((n_transitions-1))); do
    mkdir -p ${path}/multidir/ti${i}
    cp ${path}/ti${i}.tpr ${path}/multidir/ti${i}/ti.tpr
done
