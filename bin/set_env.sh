#!/bin/bash


# Set the path to NEMAT
NMT_HOME=$(pwd)

cond=$(which mamba | wc -l)
if [ $cond -eq 0 ]; then
    cond=$(which conda | wc -l)
    if [ $cond -eq 0 ]; then
        echo -e "\033[31m--> Neither mamba nor conda found, please install one of them in order to use NEMAT <--\033[0m"
        exit 1
    else
        cond="conda"
    fi
else
    cond="mamba"
fi

if [ -d "$($cond info --base)/envs/NEMAT" ]; then
    echo ""
    echo -e "\033[32mNEMAT environment already exists in $($cond info --base)/envs/NEMAT\033[0m"
    echo ""
    exit 1
else
    $cond env create -f $NMT_HOME/env/environment.yml
    if [[ $? -ne 0 ]]; then
        echo -e "\033[31mERROR: conda env creation failed\033[0m"
        exit 1
    else
        echo -e "\033[32mNEMAT environment is set up.\033[0m To activate it, run:\n\nconda activate NEMAT\n"
    fi
fi


if ! command -v gmx >/dev/null 2>&1; then
    echo -e "\033[31m--> WARNING: gmx executable not found, please install GROMACS in order to use NEMAT <--\033[0m"
fi

conda env config vars set -n NEMAT NMT_HOME=$NMT_HOME
echo -e "\nNMT_HOME set to $NMT_HOME\n"

echo "export PATH=\"\$PATH:$NMT_HOME/bin\"" >> ~/.bashrc
source ~/.bashrc
