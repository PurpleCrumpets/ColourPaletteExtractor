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


from colourpaletteextractor.model.algorithms.nieves2020 import Nieves2020OffsetCubes
from colourpaletteextractor.model.model import generate_colour_palette_from_image

# Path to sample image
file_name = "./colourpaletteextractor//data/sampleImages/annunciation-1434.jpg"

# Using the default algorithm
print("Using the default algorithm")
recoloured_image, colour_palette, relative_frequencies = generate_colour_palette_from_image(file_name)

# Specifying the algorithm to use
print("Specifying the algorithm to use")
recoloured_image, colour_palette, relative_frequencies \
    = generate_colour_palette_from_image(path_to_file=file_name, algorithm=Nieves2020OffsetCubes)