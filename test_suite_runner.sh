#!/bin/bash

########################################################
# Run the ColourPaletteExtractor Python Test Suite
########################################################

echo "Loading settings from macOS.config..."
source macOS.config || exit

# Connect to virtual Python environment (provide absolute path to the 'activate' file)
source $python_virtual_environment_path

echo "Running test suite..."
pytest colourpaletteextractor/tests

echo "Finished!"
