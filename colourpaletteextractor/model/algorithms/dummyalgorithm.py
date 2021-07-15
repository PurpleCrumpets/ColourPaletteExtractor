from colourpaletteextractor.model.algorithms import palettealgorithm


class TestAlgorithm(palettealgorithm.PaletteAlgorithm):

    def __init__(self):
        """Constructor."""
        super().__init__(None, None)

        pass

    def generate_colour_palette(self, image):
        pass