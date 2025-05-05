#!/bin/bash

rm -f *_a.pdb

for file in *.pdb; do
    base_name="${file%.pdb}"
    if [ $base_name != ref_lig ]; then
	    lovoalign -all -p1 $file -p2 ref_lig.pdb -o "$base_name"_a.pdb
        obabel -ipdb "$base_name"_a.pdb -O "$base_name".sdf 1&>2
        obabel -ipdb "$base_name"_a.pdb -O "$base_name".mol2 1&>2
    fi
    
done

rm ligands.sdf
cat *.sdf > ligands.sdf


