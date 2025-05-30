#! /bin/bash

ref_file=$(realpath $1)
change_dir=inputs/ligands/$2
current_dir=$(pwd)

cd $change_dir
pwd

# Back up previous files
mv ligGeom.pdb OLDligGeom.pdb

# Check if ref file is pdb
ref_extension=$(echo "$ref_file" | cut -d'.' -f2)


if [ "$ref_extension" != "pdb" ]; then
  echo "Generating reference pdb file..."
  
  # Generate a new PDB file using the reference file
  obabel $ref_file -opdb > refGeom.pdb
fi

# Align OLDligGeom.pdb to the reference file
pmx atomMapping -i1 refGeom.pdb -i2 OLDligGeom.pdb -opdb2 ligGeom.pdb

# Remove connect lines from generated pdb file
grep -v "CONNECT" ligGeom.pdb

# Clean folder 
rm *.dat
rm *.log

cd $current_dir



