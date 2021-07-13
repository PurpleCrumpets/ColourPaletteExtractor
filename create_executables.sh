#!/bin/bash

############################
## User-defined variables ##
############################
# Connect to virtual Python environment (provide absolute path to the 'activate' file
source /Users/tim/PythonVirtualEnvironments/ColourPaletteExtraction/bin/activate

# PyInstaller output directory
OUTPUT_DIR=/Users/tim/Documents/ColourPaletteExtractor-Executables

############################
############################

# Name of the executable
NAME="ColourPaletteExtractor"

# Build application
echo "Building $NAME app using __main__.py file..."

cd ./colourpaletteextractor || exit

# Name of expected PyInstaller SPEC file
SPEC_FILE="$(pwd)/${NAME}.spec"

if test -f "$SPEC_FILE"
then
  echo "Spec file found! Using this to build the application!"

  # Update pathex in spec file
  CURRENT_DIR=$(pwd)
  PATTERN="pathex=\['\(.*\)'\]"
  REPLACEMENT="pathex=\['$CURRENT_DIR'\]"
  sed -i "" -e 's,'"$PATTERN"','"$REPLACEMENT"',g' "$SPEC_FILE"
  wait

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
  echo "Once built, please run this file again to add in version information..."

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
