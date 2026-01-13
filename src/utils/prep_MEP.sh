#!/bin/bash

single_name=$1
IMO=$2

if [ -z "$single_name" ] || [ -z "$IMO" ]; then
    echo "Usage (at least): $0 <single_name> <IMO>"
    exit 1
fi


system_name="step3_packing.pdb"

echo -e "\nUsing default system name: \033[33m$system_name\033[0m. If different, please modify the \033[33mmembrane.tcl\033[0m file accordingly.\n"


if [ ! -f "$single_name" ]; then
    echo -e "\033[31mError: File $single_name does not exist. Place it in the NEMAT working directory.\033[0m"
    exit 1
fi

echo -e "--> Changing beta factor of ${single_name}...\n"

python $NMT_HOME/src/utils/membrane_bfactor.py "${single_name}" "${IMO}"


echo -e "\n--> Copying membrane.tcl and preparing it..."
cp $NMT_HOME/src/utils/membrane.tcl .

sed -i "s|protein.pdb|${single_name}|g" membrane.tcl
sed -i "s|system.pdb|${system_name}|g" membrane.tcl

echo -e "\nPrepared membrane.tcl with single name=${single_name} and system name=${system_name}\n"
echo -e "\t> Use \033[33mvmd -e membrane.tcl\033[0m to load the structures in VMD."
echo -e "\t> Load the ruler using \033[33mExtensions > visualization > Ruler\033[0m in the VMD menu."
echo -e "\t> Make sure that the white colored part of the protein is inside the membrane.\n"