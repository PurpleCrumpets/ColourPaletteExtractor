from colourpaletteextractor.model.algorithms import palettealgorithm


class Nieves2020(palettealgorithm.PaletteAlgorithm):

    def __inti__(self):
        """Constructor."""
        super().__init__()

    def generate_colour_palette(self, image):
        print("Generating colour palette")
