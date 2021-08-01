#!/bin/bash

# ColourPaletteExtractor is a simple tool to generate the colour palette of an image.
# Copyright (C) 2021  Tim Churchfield
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#############################################################
## Create the ColourPaletteExtractor application for macOS ##
#############################################################

echo "Loading settings from macOS.config..."
source macOS.config || exit

# Connect to virtual Python environment
source $python_virtual_environment_path

# PyInstaller output directory
OUTPUT_DIR=$executable_output_directory

# Name of the executable
NAME="ColourPaletteExtractor"

# Build application
echo "Building $NAME application..."

cd ./colourpaletteextractor || exit

# Name of expected PyInstaller SPEC file
SPEC_FILE="$(pwd)/${NAME}.spec"

# Check if spec file exists. If it does, use it to build the application
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
  pyinstaller "${NAME}.spec" \
    --clean \
    --workpath $OUTPUT_DIR/build \
    --distpath $OUTPUT_DIR/dist \
    --noconfirm


else
  echo "Spec file not found! Building application from scratch!"
  echo "Once built, please run this file again to add in version information..."
  echo "Please be aware that the application may not run correctly or even open if the custom spec file cannot be found..."

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

# Add a copy of the README.md to the distribution folder
README="$(pwd)/../README.md"

if test -f "$README"
then
  echo "README.md found and added to the chosen distribution directory..."
  cp "$README" $OUTPUT_DIR/dist

else
  echo "README.md not found..."
fi

# Add a copy of the LICENCE.md to the distribution folder
LICENCE="$(pwd)/../LICENCE.md"

if test -f "$LICENCE"
then
  echo "LICENCE.md found and added to the chosen distribution directory..."
  cp "$LICENCE" $OUTPUT_DIR/dist

else
  echo "LICENCE.md not found..."
fi

echo "Finished!"
