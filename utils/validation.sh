#!/bin/bash

logfile="logs/analysis.log"
edges=()
validations=()
capture=0
buffer=""

echo ""

while IFS= read -r line; do
    if [[ "$line" == "--> edge_"* ]]; then
        edges+=("$line")
    elif [[ "$line" =~ -+VALIDATION-+ ]]; then
        capture=1
        buffer="$line"
    elif [[ "$line" =~ -{3,} && $capture -eq 1 ]]; then
        buffer+=$'\n'"$line"
        validations+=("$buffer")
        capture=0
        buffer=""
    elif [[ $capture -eq 1 ]]; then
        buffer+=$'\n'"$line"
    fi
done < "$logfile"

# Print each edge with its validation block
for i in "${!edges[@]}"; do
    echo -e "${edges[i]}\n"
    echo -e "${validations[i]}\n"
    echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    echo
    echo
done


