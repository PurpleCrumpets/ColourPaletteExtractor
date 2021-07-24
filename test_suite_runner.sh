#!/bin/bash

############################
## User-defined variables ##
############################
# Connect to virtual Python environment (provide absolute path to the 'activate' file)
source /Users/tim/PythonVirtualEnvironments/ColourPaletteExtraction/bin/activate

############################
############################


echo "Running test suite..."
pytest colourpaletteextractor/tests

echo "Finished!"
