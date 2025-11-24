#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 input.mdp time nframes"
    exit 1
fi

input_file="$1"
time="$2"
nframes="$3"

dt=0.002  # Time step in ps

nsteps=$(awk -v t=$time -v d=$dt 'BEGIN { printf("%d", t*1000/d) }')
dl=$(awk -v n=$nsteps 'BEGIN { printf("%.9f", 1/n) }')

# update nsteps
sed -i "s/^[[:space:]]*nsteps[[:space:]]*=.*/nsteps = $nsteps/" "$input_file"

# Compute output frequency to save nframes 
freq=$(( nsteps / nframes ))
if [ $freq -lt 1 ]; then
    freq=1
fi

freq_log=$(( freq * 10 ))

# Update trajectory output in compressed mode
sed -i "s/^[[:space:]]*nstxout-compressed[[:space:]]*=.*/nstxout-compressed = $freq/" "$input_file"

# Update velocities, energy, log output
sed -i "s/^[[:space:]]*nstenergy[[:space:]]*=.*/nstenergy = $freq/" "$input_file"
sed -i "s/^[[:space:]]*nstlog[[:space:]]*=.*/nstlog = $freq_log/" "$input_file"
sed -i "s/^[[:space:]]*nstcheckpoint[[:space:]]*=.*/nstcheckpoint = $freq_log/" "$input_file"

# Update delta-lambda
if [[ "$input_file" == *"_ti_l0"* ]]; then
    sed -i "s/^[[:space:]]*delta-lambda[[:space:]]*=.*/delta-lambda = $dl/" "$input_file"
elif [[ "$input_file" == *"_ti_l1"* ]]; then
    sed -i "s/^[[:space:]]*delta-lambda[[:space:]]*=.*/delta-lambda = -$dl/" "$input_file"
fi
