#!/bin/bash

# Check if there are any .md files
if ! ls *.md &> /dev/null; then
    echo "No .md files found in the current directory."
    exit 0
fi

# Iterate over all .md files in the current directory
for md_file in *.md; do
    # Generate the new filename
    txt_file="${md_file%.md}.txt"

    # Rename the file
    mv "$md_file" "$txt_file"

    # Check if the rename was successful
    if [ $? -eq 0 ]; then
        echo "Renamed: $md_file -> $txt_file"
    else
        echo "Error renaming: $md_file"
    fi
done

echo "All .md files have been renamed to .txt"