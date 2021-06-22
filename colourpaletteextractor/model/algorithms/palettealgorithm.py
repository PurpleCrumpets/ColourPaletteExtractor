from abc import ABC, abstractmethod


class PaletteAlgorithm(ABC):

    def __init__(self):
        """Constructor."""
        pass

    @abstractmethod
    def generate_colour_palette(self, image):
        """From the given image, return its colour palette"""
        pass
