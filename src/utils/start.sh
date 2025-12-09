#!/usr/bin/env bash
set -e

# Check that NMT_HOME is set
if [ -z "$NMT_HOME" ]; then
    echo "Error: NMT_HOME is not set."
    echo "Please activate your environment or export NMT_HOME first."
    exit 1
fi

# Define source and destination
SRC="$NMT_HOME/data"
DEST="$(pwd)"

check=$(ls "$DEST" | wc -l)
if [ "$check" -ne 0 ]; then
    echo -e "\033[31mError:\033[0m Current directory ($DEST) is not empty. \"\033[33mnemat start\033[0m\" must be run in an empty directory."
    exit 1
fi

echo "Preparing $DEST for a NEMAT run..."
cp -r "$SRC"/* "$DEST"/
cp $NMT_HOME/input.yaml "$DEST"/input.yaml

echo -e "All set up! Use \"\033[33mnemat prep\033[0m\" to start the simulation.\n"
