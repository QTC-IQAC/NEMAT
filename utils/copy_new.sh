#!/bin/bash
# Usage: ./copy_workpath.sh <source_workpath> <dest_workpath> <level>
# <level> must be "eq", "md" or "all"

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <source_workpath> <dest_workpath> <level>"
    echo "Example: $0 ./workpath_X ./workpath_copy eq"
    exit 1
fi

src="$1"
dst="$2"
level="$3"

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
else
    echo "Operation cancelled."
fi