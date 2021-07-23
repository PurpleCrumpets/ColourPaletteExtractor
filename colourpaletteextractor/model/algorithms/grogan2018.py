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