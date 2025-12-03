#!/usr/bin/env bash
set -e

# Check that NMT_HOME is set
if [ -z "$NMT_HOME" ]; then
    echo "Error: NMT_HOME is not set."
    echo "Please activate your environment or export NMT_HOME first."
    exit 1
fi

# Define source and destination
SRC="$NMT_HOME/example"
DEST="$(pwd)"

check=$(ls "$DEST" | wc -l)
if [ "$check" -ne 0 ]; then
    echo -e "\033[31mError:\033[0m Current directory ($DEST) is not empty. \"\033[33mnemat example\033[0m\" must be run in an empty directory."
    exit 1
fi

echo "Preparing $DEST for an example run..."
echo -e "\nThis example reproduces the results in Table 1 of the \033[33mNEMAT paper; DOI: XXXX\033[0m"
echo -e "\t --> Proteins: P2Y1 with internal water added with Dowser++"
echo -e "\t --> Ligands: 11a.mol2, 11b.mol2, 11c.mol2, 11f.mol2, 1.mol2 already aligned with a reference BPTU"
echo -e "\t --> Membrane: POPC bilayer generated with CHARMM-GUI (default)"
echo -e "\t --> input.yaml is pre-configured for this example simulation."
cp -r "$SRC"/* "$DEST"/

echo -e "\nAll set up! Use \"\033[33mnemat prep\033[0m\" to start the example simulation.\n"
