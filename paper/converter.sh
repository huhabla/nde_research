#!/bin/bash

# Check if pdf2txt.py exists
if [ ! -f "pdf2txt.py" ]; then
    echo "Error: pdf2txt.py not found in the current directory."
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in the PATH."
    exit 1
fi

# Iterate over all PDF files in the current directory
for pdf_file in *.pdf; do
    # Check if there are actually any PDF files
    if [ ! -e "$pdf_file" ]; then
        echo "No PDF files found in the current directory."
        exit 0
    fi

    # Execute the Python script
    python pdf2txt.py "$pdf_file"

    echo "------------------------"
done

echo "All PDF files processed."