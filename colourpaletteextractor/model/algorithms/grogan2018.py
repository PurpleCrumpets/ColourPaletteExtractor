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


from __future__ import annotations

from colourpaletteextractor.model.algorithms import palettealgorithm


class Grogan2018(palettealgorithm.PaletteAlgorithm):

    name = "Grogan, Hudon, McCormack and Smolic (2018) [NOT IMPLEMENTED!]"
    url = "https://v-sense.scss.tcd.ie/research/vfx-animation/automatic-palette-extraction-for-image-editing/"

    def __init__(self):
        """Constructor."""
        super().__init__(Grogan2018.name, Grogan2018.url)

    def generate_colour_palette(self, image):
        pass