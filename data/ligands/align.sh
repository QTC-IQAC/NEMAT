#!/bin/bash

mkdir -p aligned
rm -f aligned/*.sdf
if [ -f "ref_lig.mol2" ]; then
    mv ref_lig.mol2 ref_lig.bak
    rm -f *.mol2
    mv ref_lig.bak ref_lig.mol2
else
    rm -f *.mol2
fi

ref_lig=$(ls ref_lig.*)
file_type=$(echo "${ref_lig##*.}")
echo -e "--> Aligning ligands using file type: $file_type "
if [ $file_type == ".pdb" ];then
    echo -e " \t --> \033[33m WARNING: PDB files may not contain proper bond information!!!!!\033[0m"
fi

python align_SM.py --ft "$file_type"

for file in aligned/*.sdf; do
    base_name=$(basename "$file" .sdf)
    obabel -isdf aligned/"$base_name".sdf -O $base_name.mol2 1&>align.log
done

rm -f ligands.sdf
cat aligned/*.sdf > ligands.sdf


