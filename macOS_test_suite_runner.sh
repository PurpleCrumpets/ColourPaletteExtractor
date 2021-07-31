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

##############################################################
## Run the ColourPaletteExtractor Python Test Suite - macOS ##
##############################################################

echo "Loading settings from macOS.config..."
source macOS.config || exit

# Connect to virtual Python environment
source $python_virtual_environment_path

echo "Running test suite..."
pytest colourpaletteextractor/tests

echo "Finished!"