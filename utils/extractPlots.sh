#! /bin/bash

work_dir=$1
mkdir -p $work_dir/plots
cd $work_dir/plots
plots_dir=$(pwd)
cd ..

edges=$(find -type d -name "edge*")

for edge in $edges; do
    echo $edge
    cd $edge
    pwd
    analyse=$(find -type d -name "analyse*")
    for ani in $analyse; do
        cd $ani
        pwd
        name=$(echo "$ani" | sed "s/\//_/g")
        echo $name
        cp wplot.png $plots_dir/$edge-$name.png
        cd ../..
    done
    cd ..
done
cd ..