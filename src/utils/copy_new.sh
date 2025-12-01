#!/bin/bash
# Usage: ./copy_workpath.sh <source_workpath> <dest_workpath> <level>
# <level> must be "eq", "md" or "all"

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <source_workpath> <dest_workpath> <new_workpath> <level>"
    echo "Example: $0 workpath_X input_path new_run eq"
    exit 1
fi

src="$1"
inp="$2"
dst_="$3"
inp_=$(basename "$inp")
level="$4"

new_wp=$(basename "$src")

dst="$dst_/$new_wp"
src=$(realpath "$src")
src_=$(dirname "$src")



if [ $level != "eq" ] && [ $level != "md" ] && [ $level != "all" ]; then
    echo "Error: <level> must be 'eq', 'md' or 'all'."
    exit 1
fi

if [ ! "$level" == "all" ]; then
    echo -e "Do you want to copy the contents of \033[1;33m$src\033[0m up to \033[1;33m$level\033[0m to the new destination \033[1;33m$dst\033[0m? (yes/no): "
    read answer
    answer=${answer,,}  # convert to lowercase
else
    memfiles=$(cd $src &&  du -sh | cut -f1)
    echo -e "This will copy the entire contents of \033[1;33m$src\033[0m to the new destination \033[1;33m$dst\033[0m, consuming \033[31m$memfiles\033[0m. Do you want to proceed? (yes/no): "
    read answer
    answer=${answer,,}  # convert to lowercase
fi

if [[ "$answer" == "yes" || "$answer" == "y" ]]; then

    RSYNC_FLAGS=(-a --info=progress2 --human-readable)

    mkdir -p "$dst_"
    mkdir -p "$dst_/logs"

    cp -r "$inp" "$dst_/$inp_"
    cp "$src_/input.yaml" "$dst_/input.yaml"
    
    # Common excludes (analyse folders, jobscripts, plots)
    if [ ! "$level" == "all" ]; then
        EXCLUDES=(
        --exclude '*/analyse*/**'
        --exclude 'plots/**'           
        --exclude 'em_jobscripts/**'
        --exclude 'eq_jobscripts/**'
        --exclude 'md_jobscripts/**'
        --exclude 'transitions_jobscripts/**'
        )
    fi

    if [ "$level" == "eq" ]; then
        rsync "${RSYNC_FLAGS[@]}" \
        --include '*/' \
        --include '*/em/***' \
        --include '*/eq/***' \
        --exclude '*/md/**' \
        --exclude '*/transitions/**' \
        "${EXCLUDES[@]}" \
        "$src/" "$dst/"
    elif [ "$level" == "md" ]; then
        rsync "${RSYNC_FLAGS[@]}" \
        --include '*/' \
        --include '*/em/***' \
        --include '*/eq/***' \
        --include '*/md/***' \
        --exclude '*/transitions/**' \
        "${EXCLUDES[@]}" \
        "$src/" "$dst/"
    elif [ "$level" == "all" ]; then
        rsync "${RSYNC_FLAGS[@]}" \
        --include '*/' \
        --include '*/em/***' \
        --include '*/eq/***' \
        --include '*/md/***' \
        --include '*/transitions/***' \
        "${EXCLUDES[@]}" \
        "$src/" "$dst/"
    fi


    if [ ! "$level" == "all" ]; then
        rm -rf "$dst/em_jobscripts" "$dst/eq_jobscripts" "$dst/md_jobscripts" "$dst/transitions_jobscripts"
        rm -rf "$dst/plots"
    fi

    # Find all target .top files
    find "$dst" -type f -path "$dst/edge_*/membrane/topol.top" | while read -r file
    do
        echo "Renaming paths in $file"
        
        # Replace all occurrences of $src with $dst
        sed -i "s|$src_|$dst_|g" "$file"
    done

    find "$dst" -type f -path "$dst/edge_*/protein/topol.top" | while read -r file
    do
        echo "Renaming paths in $file"
        
        # Replace all occurrences of $src with $dst
        sed -i "s|$src_|$dst_|g" "$file"
    done

    find "$dst" -type f -path "$dst/edge_*/water/topol.top" | while read -r file
    do
        echo "Renaming paths in $file"
        
        # Replace all occurrences of $src with $dst
        sed -i "s|$src_|$dst_|g" "$file"
    done

    echo "Copy completed successfully."
    echo "~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>"
    echo -e "\n\t \033[1;35mWARNING:\033[0m The copied workpath will use all the computed files from $src."
    echo -e "\t          Using \033[1;33mnemat prep\033[0m would create new topology files which won't match the existing trajectory files."
    echo -e "\t          If you change something on the input.yaml file, update it by using:"
    echo -e "\t\t\t \033[1;33mcd $dst\033[0m"
    echo -e "\t\t\t \033[1;33mnemat update\033[0m \n"
    echo "~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>"
else
    echo "Operation cancelled."
fi