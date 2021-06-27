# TODO: add ability to run the model by itself, without the GUI using __main__
import errno
import os
from sys import argv

from colourpaletteextractor.model import imagedata
from colourpaletteextractor.model.algorithms import nieves2020


class ColourPaletteExtractorModel:
    ERROR_MSG = "Error! :'("
    supported_image_types = {"png", "jpg"}

    def __init__(self, algorithm=None):
        self._images = []
        if algorithm is None:
            self._algorithm = nieves2020.Nieves2020()  # Default algorithm
        else:
            print("Algorithm not None")  # TODO: add new algorithm

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
        """Add a new image to the list of images."""

        # Create new ImageData object to hold image (and later the colour palette)
        new_image = imagedata.ImageData(file_name_and_path)
        self._images.append(new_image)

        return new_image

    def remove_image_data(self, i):
        """Remove image from list of images by its index."""
        self._images.pop(i)

    def _get_image(self, index):
        print("Retrieving image...")
        image_data = self._images[index]
        return image_data.image.copy()
        # TODO: Add checks for the index in case it is out of range

    def generate_palette(self, i):
        print("Generating colour palette for image ", i)

        image = self._get_image(i)
        new_image, relevant_cubes = self._algorithm.generate_colour_palette(image)

        print(new_image.shape, len(relevant_cubes))


if __name__ == "__main__":



    # data_dir = "data"
    # print(__file__)
    # os.getcwd() - where script executed from!
    # print(argv[0])  # Gives you absolute path to the file that was run - this could be useful later on

    file_name = argv[1]

    if len(argv) == 3:
        model_type = argv[2]

    model = ColourPaletteExtractorModel()

    if os.path.isfile(file_name) is False:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), file_name)
        # TODO: explain why the file is invalid (ie make sure that there are no spaces in the names of folders etc)
        # Put it in quotes
    else:
        model.add_image(file_name)

    print("Added image!")

    # Get colour palette of the image (image 0 in list)
    # print(len(model._images))
    model.generate_palette(0)







    # print(os.path.isfile(file_name))

    # # Check if file is an image
    # found = False
    # for file_type in model.supported_image_types:
    #     file_type = "." + file_type
    #     if search(file_type, file_name):
    #         found = True
    #         # model.add_image()
    #         break
    # Check if file can be found
    #
    #
    # # Check if file is a path
    # if os.path.isdir(file_name):
    #     print("Found directory")

    # TODO Check inputs
    # If provided with a directory, apply to all valid files inside
    # Else if just a file - just do that one
    # If provided with a second argument - this is used to control the algorithm used to extract

    # model.add_image()
