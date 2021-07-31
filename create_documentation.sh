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


########################################################
# Create the Documentation for ColourPaletteExtractor
########################################################

echo "Loading settings from macOS.config..."
source macOS.config || exit

# Connect to virtual Python environment (provide absolute path to the 'activate' file)
source $python_virtual_environment_path

# Properties
NAME="ColourPaletteExtractor"  # Name of the executable
OUTPUT_PATH=./docs/source # source path
MODULE_PATH=./colourpaletteextractor  # Python modules path

# Add Python modules
echo "Adding Python modules to documentation..."
sphinx-apidoc -f -o $OUTPUT_PATH $MODULE_PATH

# Build documentation
echo "Building html documentation for $NAME..."
cd ./docs || exit
make html

echo "Building PDF documentation for $NAME..."
sphinx-build -b rinoh source build/pdf

echo "Finished!"
