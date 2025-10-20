#!/bin/bash

mkdir -p aligned
rm -f aligned/*_a.pdb

python align_SM.py
mkdir -p aligned/sdf
mkdir -p aligned/mol2

for file in ligands/*.pdb; do
    base_name=$(basename "$file" .pdb)
    if [ $base_name != ref_lig ]; then
	    # lovoalign -all -p1 ligands/$file -p2 ref_lig.pdb -o aligned/"$base_name"_a.pdb
        obabel -ipdb aligned/"$base_name"_a.pdb -O aligned/sdf/"$base_name".sdf 1&>align.log
        obabel -ipdb aligned/"$base_name"_a.pdb -O aligned/mol2/"$base_name".mol2 1&>align.log
    fi
done


rm -f ligands.sdf
cat aligned/sdf/*.sdf > ligands.sdf


