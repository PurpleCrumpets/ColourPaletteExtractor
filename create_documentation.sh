#!/bin/bash

############################
## User-defined variables ##
############################
# Connect to virtual Python environment (provide absolute path to the 'activate' file)
source /Users/tim/PythonVirtualEnvironments/ColourPaletteExtraction/bin/activate

############################
############################

# Properties
NAME="ColourPaletteExtractor"  # Name of the executable
OUTPUT_PATH=./docs/source # source path
MODULE_PATH=./colourpaletteextractor  # Python modules path

# Add Python modules
echo "Adding Python modules to documentation..."
sphinx-apidoc -f -o $OUTPUT_PATH $MODULE_PATH

# Build documentation
echo "Building html documentation for $NAME..."

cd ./docs
make html

echo "Finished!"
