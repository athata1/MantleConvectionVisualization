#!/bin/bash

# Check if two arguments are provided (start and end file numbers)
if [ $# -ne 2 ]; then
    echo "Usage: $0 <start_file_number> <end_file_number>"
    exit 1
fi

# Get start and end file numbers from command line arguments
start_file_number=$1
end_file_number=$2

# Loop through the file numbers from start to end
for i in $(seq $start_file_number $end_file_number)
do
    echo "Running mantle2.py for file_number $i"
    python mantle2.py $i
done
