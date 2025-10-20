#! /bin/bash

# Checks how many of the slurm files in a directory have finished successfully

step=$1

wp=$(grep "workPath:" input.yaml | sed -E "s/.*workPath:[[:space:]]*'([^']+)'.*/\1/")

jobs_dir="$wp/${step}_jobscripts"

current_dir=$(pwd)

cd $jobs_dir



for file in job_* 
do 
    check=$(grep "GROMACS reminds you:" $file | wc -l)
    if [ $check -eq 0 ]; then
        echo "$file" >> fail.temp
    else
        if [ "$step" == 'eq' ]; then
            kind_m=$(grep "/membrane/" $file | wc -l)
            kind_w=$(grep "/water/" $file | wc -l)
            kind_p=$(grep "/protein/" $file | wc -l)

            if [ $kind_m -ne 0 ] || [ $kind_p -ne 0 ]; then
                if [ $check -eq 11 ]; then
                    echo "$file" >> succ.temp
                else
                    echo -e "$file" >> fail.temp
                fi
            else
                if [ $check -eq 1 ]; then
                    echo "$file" >> succ.temp
                else
                    echo -e "$file" >> fail.temp
                fi
            fi
        else
            echo "$file" >> succ.temp
        fi            
    fi
done

succes=$(cat succ.temp | wc -l)
total=$(ls job_* | wc -l)

if [ $succes -eq $total ]; then
    color="\033[0;32m"  # Green
else
    color="\033[0;31m"  # Red
    failed=$(cat fail.temp)
fi

echo -e "\n\t$color$succes jobs\033[0m finished successfully out of $total total jobs.\n"

if [ $color == "\033[0;31m" ]; then
    echo -e "\nFailed jobs:\n"
    for job in $failed; do
        suffix="${job##*_}"
        suffix="${suffix%%.*}"
        echo -e "\t--> job $suffix)"
    done
    echo ""
fi

rm -f succ.temp fail.temp

cd $current_dir

