#!/bin/bash
# This script initiates a new run of the project by removing the previous run's input and working directory file.

input=$1
wp=$2

input="${input#./}"

echo -e "Do you want to remove ${input} and ${wp}? \033[31mThis process cannot be undone!\033[0m (yes/no): "
read answer
answer=${answer,,}  # convert to lowercase

if [[ "$answer" == "yes" || "$answer" == "y" ]]; then
    echo "Removing workpath ${wp}"
    rm -rf ${wp}
    echo "Removing input ${input}"
    rm -rf ${input}
    echo "Removing logs"
    rm -f logs/*
fi