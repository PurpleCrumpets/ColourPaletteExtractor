#!/bin/bash

# Name of the executable
NAME="ColourPaletteExtractor"

# PyInstaller output directory
OUTPUT_DIR=/Users/tim/Documents/ColourPaletteExtractor-Executables

# Connect to virtual Python environment
source /Users/tim/PythonVirtualEnvironments/ColourPaletteExtraction/bin/activate

# Build application
echo "Building $NAME app using __main__.py file..."

cd ./colourpaletteextractor || exit

pyinstaller __main__.py --onefile \
--clean \
--workpath $OUTPUT_DIR/build \
--distpath $OUTPUT_DIR/dist \
--add-data './view/resources:resources' \
--name $NAME \
--icon=app_icon.icns \
--windowed \
--noconfirm \
--onedir

echo "Finished!"
