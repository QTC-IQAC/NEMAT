#!/bin/bash

file=$1

echo ""
cat logs/warnings_$file.log
echo ""
echo ""
cat logs/errors_$file.log
echo ""

