#!/bin/bash

file=$1

echo ""
if [ -f "logs/warnings_$file.log" ]; then
    cat logs/warnings_$file.log
    echo ""
    echo ""

    cat logs/errors_$file.log
    echo ""
else
    echo -e "logs/warnings_$file.log doesn't exist, \033[31man error may have occurred before finishing\033[0m. Check logs/$file.err for errors."
fi

