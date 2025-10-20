#!/bin/bash

new_temp=$1
mdppath=$2

mdppath="${mdppath}/mdppath"

chmod 666 "$mdppath"/*

echo mdppath: $mdppath

for file in "$mdppath"/*; do
  if [[ -f "$file" ]]; then
    # Get the current number of values after ref-t
    line=$(grep -E '^\s*ref[-_]t\s*=' "$file")
    if [[ -n "$line" ]]; then
      num_vals=$(echo "$line" | sed -E 's/.*=\s*//' | wc -w)
      if [[ $num_vals -gt 0 ]]; then
        # Construct new value list like: "298 298 298"
        new_vals=$(yes "$new_temp" | head -n "$num_vals" | tr '\n' ' ' | sed 's/ *$//')
        # Replace the line in-place
        sed -i -E "s/^\s*(ref[-_]t\s*=).*/\1 $new_vals/" "$file"
      fi
    fi

    # Get the current number of values after gen-temp
    line=$(grep -E '^\s*gen[-_]temp\s*=' "$file")
    if [[ -n "$line" ]]; then
      num_vals=$(echo "$line" | sed -E 's/.*=\s*//' | wc -w)
      if [[ $num_vals -gt 0 ]]; then
        # Construct new value list like: "298 298 298"
        new_vals=$(yes "$new_temp" | head -n "$num_vals" | tr '\n' ' ' | sed 's/ *$//')
        # Replace the line in-place
        sed -i -E "s/^\s*(gen[-_]temp\s*=).*/\1 $new_vals/" "$file"
      fi
    fi
  fi
done