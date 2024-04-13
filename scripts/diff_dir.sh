#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 dir1 dir2"
    exit 1
fi

# Assign directories to variables
dir1="$1"
dir2="$2"

# Ensure both arguments are directories
if [ ! -d "$dir1" ] || [ ! -d "$dir2" ]; then
    echo "Both arguments must be directories."
    exit 1
fi

# Generate sorted lists of all directory entries
gfind "$dir1" -name \*ini -printf "%P\n" | sort > /tmp/dir1_contents.txt
gfind "$dir2" -name \*ini -printf "%P\n" | sort > /tmp/dir2_contents.txt

# Diff the contents
diff /tmp/dir1_contents.txt /tmp/dir2_contents.txt

# Clean up temporary files
rm /tmp/dir1_contents.txt /tmp/dir2_contents.txt
