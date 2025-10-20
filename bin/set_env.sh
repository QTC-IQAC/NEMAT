#!/bin/bash


# Set the path to NEMAT
NMT_HOME=$(pwd)
echo -e "\nNMT_HOME set to $NMT_HOME\n"

PATH=$NMT_HOME/bin:$PATH

cond=$(which mamba)
if [ -z "$cond" ]; then
    cond=$(which conda)
fi

if [ -d "$($cond info --base)/envs/NEMAT" ]; then
    echo ""
    echo -e "\033[32mNEMAT environment already exists in $($cond info --base)/envs/NEMAT\033[0m"
    echo ""
else

    $cond env create -f $NMT_HOME/env/environment.yml
    echo -e "\033[32mNEMAT environment is set up.\033[0m To activate it, run:\n\nconda activate NEMAT\n"
fi


if ! command -v gmx >/dev/null 2>&1; then
    echo -e "\033[31m--> gmx executable not found, please install GROMACS in order to use NEMAT <--\033[0m"
fi

conda env config vars set -n NEMAT NMT_HOME=$NMT_HOME

echo "export PATH=\"$PATH:$NMT_HOME/bin\"" >> ~/.bashrc
source ~/.bashrc
