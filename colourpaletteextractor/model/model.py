# TODO: add ability to run the model by itself, without the GUI using __main__
from colourpaletteextractor.model import imagedata
from colourpaletteextractor.model.algorithms import nieves2020


class ColourPaletteExtractorModel:
    ERROR_MSG = "Error! :'("
    supported_image_types = {"*.png", "*.jpg"}

    def __init__(self):
        self.images = []
        self._algorithm = nieves2020.Nieves2020()  # Default algorithm

    def evaluate_expression(self, expression):
        """slot function.
        :param expression:
        :return:
        """

        try:
            result = str(eval(expression, {}, {}))
        except Exception:
            result = ColourPaletteExtractorModel.ERROR_MSG

        return result

    def set_algorithm(self, algorithm_name):
        """Set the algorithm use to extract the colour palette of an image."""

        if algorithm_name == "nieves_2020":
            print("Nieves")
            self._algorithm = nieves2020.Nieves2020()

        else:
            print("Not a valid algorithm")
            # TODO: Throw exception

    def add_image(self, file_name_and_path):
        """Add a new image """

        # Create new ImageData object to hold image (and later the colour palette)
        self.images.append(imagedata.ImageData(file_name_and_path))

