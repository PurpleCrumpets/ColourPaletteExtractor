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

SPEC_FILE="$(pwd)/${NAME}.spec"

#echo $SPEC_FILE

if test -f "$SPEC_FILE"
then
  echo "Spec file found! Using this to build the application!"

# Update version number in spec file
OUTPUT=$(python ./_version.py)
sed -i "" -e "s/version='\(.*\)'/version='$OUTPUT'/g" "$SPEC_FILE"
wait

# Build application
  pyinstaller --clean \
  --workpath $OUTPUT_DIR/build \
  --distpath $OUTPUT_DIR/dist \
  --noconfirm \
  "${NAME}.spec"

else
  echo "Spec file not found! Building application from scratch!"

  pyinstaller __main__.py \
  --clean \
  --workpath $OUTPUT_DIR/build \
  --distpath $OUTPUT_DIR/dist \
  --add-data './view/resources:resources' \
  --name $NAME \
  --icon=app_icon.icns \
  --windowed \
  --noconfirm \
  --onedir

fi

echo "Finished!"
