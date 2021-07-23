# TODO: add ability to run the model by itself, without the GUI using __main__
import ctypes
import errno
import os
import sys
import tempfile

from sys import argv

from PySide2.QtCore import QStandardPaths, QSettings, QSize

import numpy as np

from colourpaletteextractor import _version
from colourpaletteextractor.model.imagedata import ImageData
from colourpaletteextractor.model.algorithms import nieves2020
# from colourpaletteextractor.model.algorithms import grogan2018
# from colourpaletteextractor.model.algorithms import dummyalgorithm
from colourpaletteextractor.model.algorithms.palettealgorithm import PaletteAlgorithm


def generate_colour_palette_from_image(path_to_file: str, algorithm: type[PaletteAlgorithm] = None) -> tuple[np.ndarray, list[np.ndarray], list[float]]:
    # TODO: check output types

    model = ColourPaletteExtractorModel()

    if os.path.isfile(path_to_file) is False:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), path_to_file)
        # TODO: explain why the file is invalid (ie make sure that there are no spaces in the names of folders etc)
        # Put it in quotes
    else:
        image_data_id, image_data = model.add_image(path_to_file)

    print("Added image!")

    # Get colour palette of the image (image 0 in list)

    if algorithm is None:
        model.generate_palette(image_data_id, "Tab_0", None,
                               temp_algorithm=ColourPaletteExtractorModel.DEFAULT_ALGORITHM)
    else:
        model.generate_palette(image_data_id, "Tab_0", None, temp_algorithm=algorithm)

    print("\n---------------")
    print("Colour Palette:")
    for colour in image_data.colour_palette:
        print(colour)
    print("---------------")

    new_recoloured_image = image_data.recoloured_image
    image_colour_palette = image_data.colour_palette
    relative_frequency = image_data.colour_palette_relative_frequency

    return new_recoloured_image, image_colour_palette, relative_frequency


def get_settings() -> QSettings:
    settings = QSettings(QSettings.IniFormat,
                         QSettings.UserScope,
                         _version.__organisation__,
                         _version.__application_name__)
    return settings


class ColourPaletteExtractorModel:
    # Default preferences for the settings file (if it doesn't yet exist)
    DEFAULT_ALGORITHM = nieves2020.Nieves2020
    DEFAULT_USER_DIRECTORY = os.path.join(QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
                                          _version.__application_name__,
                                          "Output")
    if sys.platform == "win32":
        DEFAULT_USER_DIRECTORY = DEFAULT_USER_DIRECTORY.replace("\\", "/")  # Consistent looking path

    DEFAULT_USE_USER_DIRECTORY = False
    DEFAULT_HEIGHT = 894  # Based on size of 'how-to' image
    DEFAULT_WIDTH = 1523  # Based on size of 'how-to' image

    ERROR_MSG = "Error! :'("
    SUPPORTED_IMAGE_TYPES = {"png", "jpg", "jpeg"}

    def __init__(self, algorithm_class_name=None):

        self._image_data_id_counter = 0
        self._image_data_id_dictionary = {}
        self._active_thread_counter = 0

        # Create temporary directory for storing generated reports
        self._temp_dir = tempfile.TemporaryDirectory(prefix=_version.__application_name__)

        # Read-in settings file
        self._read_settings()

        # Update selected algorithm
        if algorithm_class_name is not None:

            # Check if provided algorithm class name is valid
            if self._check_algorithm_valid(algorithm_class_name=algorithm_class_name):
                # TODO: check it is an instance
                self._settings.setValue("algorithm/selected algorithm", algorithm_class_name)
            else:
                pass
                # TODO: Throw exception?

        # print(str(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)))

    @property
    def active_thread_counter(self) -> int:
        return self._active_thread_counter

    @active_thread_counter.setter
    def active_thread_counter(self, value: int) -> None:
        self._active_thread_counter = value

    def change_output_directory(self, use_user_dir: bool, new_user_directory):
        print("Updating output directory...")

        # Update settings file
        self._settings.setValue("output directory/use user directory", int(use_user_dir))
        self._settings.setValue("output directory/user directory", new_user_directory)
        self._settings.sync()

        # TODO: if user dr is none but was selected - throw an exception?

    def _read_settings(self):
        print("Reading application settings...")

        # Try and set a location config file?? - make the application portable?
        self._settings = get_settings()

        print(self._settings.fileName())

        # Check if settings file exists
        if not self._settings.contains('output directory/user directory'):
            print("Settings file not found...")
            self.write_default_settings()
        else:
            print("Settings file found...")
            self._settings.setValue('output directory/temporary directory',
                                    self._temp_dir.name)  # Update path to new temporary directory
            self._settings.sync()

    def write_default_settings(self):
        print("Writing default settings to config file...")

        # Set default main window preferences
        self._settings.beginGroup("main window")
        self._settings.setValue("size", QSize(ColourPaletteExtractorModel.DEFAULT_WIDTH,
                                              ColourPaletteExtractorModel.DEFAULT_HEIGHT))
        self._settings.endGroup()

        # Set default output directory preferences
        self._settings.beginGroup("output directory")
        self._settings.setValue('temporary directory', self._temp_dir.name)
        self._settings.setValue('user directory', ColourPaletteExtractorModel.DEFAULT_USER_DIRECTORY)
        self._settings.setValue('use user directory', int(ColourPaletteExtractorModel.DEFAULT_USE_USER_DIRECTORY))
        self._settings.endGroup()

        # Set default algorithm preferences
        self._settings.beginGroup("algorithm")
        self._settings.setValue('default algorithm', ColourPaletteExtractorModel.DEFAULT_ALGORITHM)
        self._settings.setValue('selected algorithm', ColourPaletteExtractorModel.DEFAULT_ALGORITHM)
        self._settings.endGroup()

        # Update settings file
        self._settings.sync()

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

    def close_temporary_directory(self) -> None:
        self._temp_dir.cleanup()  # Removing temporary directory

    def _get_algorithm(self, algorithm: type[PaletteAlgorithm] = None):
        if algorithm is None:
            print(self._settings.value("algorithm/selected algorithm"))
            print(self._settings.value("algorithm/selected algorithm")())
            return self._settings.value("algorithm/selected algorithm")()  # Create a new instance of the algorithm

        else:
            print("Using temporary algorithm...")
            if self._check_algorithm_valid(algorithm_class_name=algorithm):
                return algorithm()
            else:
                # TODO throw exception
                pass

    def _check_algorithm_valid(self, algorithm_class_name):

        # Check if provided class name is a sub-class of PaletteAlgorithm
        if issubclass(algorithm_class_name, PaletteAlgorithm):
            return True
        else:
            pass
            # TODO: throw error here

    def set_algorithm(self, algorithm_class_name=DEFAULT_ALGORITHM):
        """Set the algorithm use to extract the colour palette of an image."""

        # Check if provided class name is a sub-class of PaletteAlgorithm
        if self._check_algorithm_valid(algorithm_class_name=algorithm_class_name):
            print("Updating selected algorithm to " + str(algorithm_class_name) + "...")

            # Update settings file
            self._settings.setValue("algorithm/selected algorithm", algorithm_class_name)
            self._settings.sync()

    def add_image(self, file_name_and_path: str):
        """From the path to an image, create a new image_data object and add it to the
         dictionary of image_data objects with a new ID number."""

        # Create new ImageData object to hold image (and later the colour palette)
        new_image_data = ImageData(file_name_and_path)

        # Add to image dictionary
        new_image_data_id = ("Tab_" + str(self._image_data_id_counter))
        self._image_data_id_counter += 1
        self._image_data_id_dictionary[new_image_data_id] = new_image_data
        # TODO: Add checks to make sure new key doesn't overwrite a current key

        return new_image_data_id, new_image_data

    def remove_image_data(self, image_data_id):
        """Remove image from list of images by its index."""
        # self._images.pop(i)
        self._image_data_id_dictionary.pop(image_data_id)
        # TODO: add checks if not found

    # def _get_image_copy(self, image_data_id):
    #     print("Retrieving copy of image...")
    #     image_data = self._image_data_id_dictionary.get(image_data_id)
    #
    #     return image_data.image.copy()

    def get_image_data(self, image_data_id):
        return self._image_data_id_dictionary.get(image_data_id)
        # TODO: Add checks for the index in case it is out of range

    @property
    def image_data_id_dictionary(self):
        return self._image_data_id_dictionary

    def generate_palette(self, image_data_id, tab, progress_callback=None, temp_algorithm=None):
        print("Generating colour palette for image:", image_data_id)

        image_data = self.get_image_data(image_data_id)
        image_data.continue_thread = True

        # Get algorithm and process image with it
        algorithm = self._get_algorithm(algorithm=temp_algorithm)
        if progress_callback is not None:
            algorithm.set_progress_callback(progress_callback, tab, image_data)

        # Set algorithm type used for the given image
        image_data.algorithm_used = type(algorithm)

        # Generate colour palette
        image = image_data.image.copy()
        new_recoloured_image, image_colour_palette, new_relative_frequencies = \
            algorithm.generate_colour_palette(image)

        # Check if image_data_id still exists
        if image_data_id in self._image_data_id_dictionary:

            # Assigning properties to image_data
            self._image_data_id_dictionary[image_data_id].recoloured_image = new_recoloured_image
            self._image_data_id_dictionary[image_data_id].colour_palette = image_colour_palette
            self._image_data_id_dictionary[image_data_id].colour_palette_relative_frequency = new_relative_frequencies

            # Sorting colour palette by relative frequency
            self._image_data_id_dictionary[image_data_id].sort_colour_palette(reverse=True)

        # print(new_recoloured_image.shape, len(image_colour_palette))


if __name__ == "__main__":

    # data_dir = "data"
    # print(__file__)
    # os.getcwd() - where script executed from!
    # print(argv[0])  # Gives you absolute path to the file that was run - this could be useful later on

    file_name = argv[1]

    if len(argv) == 3:
        model_type = argv[2]

    recoloured_image, colour_palette, relative_frequencies = generate_colour_palette_from_image(file_name)

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
