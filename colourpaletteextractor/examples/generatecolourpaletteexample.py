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

"""Contains an example script demonstrating how to generate the colour palette of a sample image."""

import os

from colourpaletteextractor.model.algorithms.nieves2020 import Nieves2020OffsetCubes
from colourpaletteextractor.model.model import generate_colour_palette_from_image

if __name__ == '__main__':

    # Path to sample image
    file_name = "./colourpaletteextractor/data/sampleImages/annunciation-1434.jpg"
    file_name = os.path.abspath(file_name)

    # Using the default algorithm
    print("Using the default algorithm")
    recoloured_image_1, colour_palette_1, relative_frequencies_1 = generate_colour_palette_from_image(file_name)

    # Specifying the algorithm to use
    print("Specifying the algorithm to use")
    recoloured_image_2, colour_palette_2, relative_frequencies_2 \
        = generate_colour_palette_from_image(path_to_file=file_name, algorithm=Nieves2020OffsetCubes)
