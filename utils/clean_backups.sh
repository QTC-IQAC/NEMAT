#!/bin/bash

# This script cleans up old backup files of the project. 

nfiles=$(find . -type f -name '#*' 2>/dev/null | wc -l)
memfiles=$(find . -type f -name '#*' -print0 | du --files0-from=- -ch | awk '/total$/ {print $1}')

if [ $nfiles -gt 0 ]; then
    echo -e "Found \033[31m$nfiles\033[0m backup files, consuming \033[31m$memfiles\033[0m. Do you want to continue? (yes/no): "
    read answer
    answer=${answer,,}  # convert to lowercase
    
    if [[ "$answer" == "yes" || "$answer" == "y" ]]; then
        echo "Removing backup files..."
        find . -type f -name '#*' -delete
        echo "Backup files removed."
    else
        echo "Operation cancelled."
    fi
else
    echo "No backup files found."
fi
