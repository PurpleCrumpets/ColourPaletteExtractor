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


import errno
import os
import sys
import tempfile
from typing import Optional

import numpy as np

from PySide2.QtCore import QStandardPaths, QSettings, QSize, QPoint

from colourpaletteextractor import _version
from colourpaletteextractor.model.imagedata import ImageData
from colourpaletteextractor.model.algorithms import nieves2020
from colourpaletteextractor.model.algorithms.palettealgorithm import PaletteAlgorithm
from colourpaletteextractor.view.tabview import NewTab


def generate_colour_palette_from_image(path_to_file: str, algorithm: type[PaletteAlgorithm] = None) -> \
        tuple[np.ndarray, list[np.ndarray], list[float]]:
    """Generate the colour palette for the given images using the specified colour palette extraction algorithm.

    An example algorithm would be nieves2020.Nieves2020CentredCubes

    Args:
        path_to_file (str): Path to the image to be analysed.
        algorithm (type[PaletteAlgorithm]): The Python class of the the colour palette extraction algorithm.

    Returns:
        (np.ndarray): THe recoloured image using just the colours in the colour palette.
        (list[np.ndarray]): The list of colours ([R,G,B] triplets) in the colour palette.
        (list[float]): The relative frequencies of the colours in the colour palette in the recoloured image.
    """

    model = ColourPaletteExtractorModel()

    # Check if the provided file exists
    if os.path.isfile(path_to_file) is False:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), path_to_file)
    else:
        image_data_id, image_data = model.add_image(path_to_file)

    # Get the colour palette of the image
    if algorithm is None:
        model.generate_palette(image_data_id, None, None,
                               algorithm=ColourPaletteExtractorModel.DEFAULT_ALGORITHM)
    else:
        model.generate_palette(image_data_id, None, None, algorithm=algorithm)

    new_recoloured_image = image_data.recoloured_image
    image_colour_palette = image_data.colour_palette
    relative_frequency = image_data.colour_palette_relative_frequency

    return new_recoloured_image, image_colour_palette, relative_frequency


def get_settings() -> QSettings:
    """Get the settings file for the ColourPaletteExtraction application.

    Returns:
        (QSettings): The settings for the ColourPaletteExtraction application.
    """

    settings = QSettings(QSettings.IniFormat,
                         QSettings.UserScope,
                         _version.__organisation__,
                         _version.__application_name__)
    return settings


class ColourPaletteExtractorModel:
    """ColourPaletteExtractor Model.

    Used as the model component of the ColourPaletteExtractor application.

    """

    # Default preferences for the settings file
    DEFAULT_ALGORITHM: type[PaletteAlgorithm] = nieves2020.Nieves2020CentredCubes
    """The default colour palette extraction algorithm Python Class."""

    DEFAULT_USER_DIRECTORY: str = os.path.join(QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
                                               _version.__application_name__,
                                               "Output")
    """The default user output directory for colour palette reports."""

    if sys.platform == "win32":
        DEFAULT_USER_DIRECTORY = DEFAULT_USER_DIRECTORY.replace("\\", "/")  # Consistent looking path

    DEFAULT_USE_USER_DIRECTORY: bool = False
    """Specify by default whether a user's output directory should be used for saving the colour palette report to."""

    DEFAULT_HEIGHT: int = 894  # Based on size of 'how-to' image
    """Default height of the ColourPaletteExtraction application.
    
        Size chosen to show the Quick Start Guide image without the need of scrollbars.
    """

    DEFAULT_WIDTH: int = 1523  # Based on size of 'how-to' image
    """Default width of the ColourPaletteExtraction application.

        Size chosen to show the Quick Start Guide image without the need of scrollbars.
    """

    SUPPORTED_IMAGE_TYPES: set[str] = {"png", "jpg", "jpeg"}
    """The set of supported image extensions."""

    def __init__(self) -> None:

        self._image_data_id_counter = 0
        self._image_data_id_dictionary = {}
        self._active_thread_counter = 0

        # Create temporary directory for storing generated reports
        self._temp_dir = tempfile.TemporaryDirectory(prefix=_version.__application_name__)

        # Read-in settings file
        self._read_settings()

    @staticmethod
    def _check_algorithm_valid(algorithm_class: type[PaletteAlgorithm]) -> bool:
        """Check if the provided algorithm class is a valid subclass of :class:`PaletteAlgorithm`.

        Args:
            algorithm_class (type[PaletteAlgorithm]): Algorithm class.

        Returns:
            (bool): True if the provided algorithm class is a valid subclass. Otherwise False.
        """

        if issubclass(algorithm_class, PaletteAlgorithm):
            return True
        else:
            return False

    @staticmethod
    def write_view_settings(size: QSize, position: QPoint) -> None:
        """Write the main window's size and shape to the settings file.

        Args:
            size (QSize): The size of the GUI.
            position (QPoint): The position of the GUI.
        """

        settings = get_settings()

        settings.beginGroup("main window")
        settings.setValue("position", position)
        settings.setValue("size", size)
        settings.endGroup()

        settings.sync()

    @staticmethod
    def read_view_settings() -> tuple[Optional[QSize], Optional[QPoint]]:
        """Get the size and shape of the main window of the GUI.

        Returns:
            (Optional[QSize]): The size of the main window. None if the appropriate setting cannot be found.
            (Optional[QPoint]): The position of the main window. None if the appropriate setting cannot be found.
        """

        settings = get_settings()
        settings.beginGroup("main window")

        size = None
        position = None

        # Get size of main window
        if settings.contains('size'):
            size = settings.value("size")

        # Get position of main window
        if settings.contains('position'):
            position = settings.value("position")

        return size, position

    @property
    def active_thread_counter(self) -> int:
        """The number of active threads still running as part of a batch operation.

        Returns:
            (int): The number of active threads still running.
        """

        return self._active_thread_counter

    @active_thread_counter.setter
    def active_thread_counter(self, value: int) -> None:
        self._active_thread_counter = value

    @property
    def image_data_id_dictionary(self) -> dict:
        """The dictionary storing the :class:`ImageData` objects for the images currently open.

        Returns:
            (dict): dictionary storing the :class:`ImageData` objects for the images currently open.
        """

        return self._image_data_id_dictionary

    def change_output_directory(self, use_user_dir: bool, new_user_directory: str) -> None:
        """Change the output directory for colour palette reports in the ColourPaletteExtractor.ini settings file.

        Args:
            use_user_dir (bool): True if the user-selected output directory is to be used. If False, use default
                temporary output directory.
            new_user_directory (str): The path to the new user-selected output directory
        """

        print("Updating output directory...")

        # Update settings file
        self._settings.setValue("output directory/use user directory", int(use_user_dir))
        self._settings.setValue("output directory/user directory", new_user_directory)
        self._settings.sync()

    def write_default_settings(self) -> None:
        """Write the default settings to the ColourPaletteExtractor.ini settings file."""

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

    def close_temporary_directory(self) -> None:
        """Delete the temporary output directory associated with the instance of the application."""

        self._temp_dir.cleanup()  # Removing temporary directory

    def set_algorithm(self, algorithm_class: type[PaletteAlgorithm] = DEFAULT_ALGORITHM) -> None:
        """Set the algorithm used to generate the colour palette of an image.

        If no algorithm_class_name is provided, the :const:`DEFAULT_ALGORITHM` is used.

        Args:
            algorithm_class (type[PaletteAlgorithm]): The algorithm class.
        """

        # Check if provided class name is a valid sub-class of PaletteAlgorithm
        if self._check_algorithm_valid(algorithm_class=algorithm_class):
            print("Updating selected algorithm to " + str(algorithm_class) + "...")

            # Update settings file
            self._settings.setValue("algorithm/selected algorithm", algorithm_class)
            self._settings.sync()

    def add_image(self, file_name_and_path: str) -> tuple[str, ImageData]:
        """Given the path to an image, create a new :class:`ImageData` object and return it and its ID key.

        Args:
            file_name_and_path (str): Path to the image.

        Returns:
            (str): The dictionary key ('Tab_xx') for the new :class:`ImageData` object in the
                :attr:`image_data_id_dictionary`.
            (ImageData): The new :class:`ImageData` object for holding information about the image (e.g., the colour
                palette, the recoloured image etc.)

        Raises:
            KeyError: If the generated dictionary key already exists in the model's dictionary of ImageData objects
                (:attr:`image_data_id_dictionary`).
        """

        # Create new ImageData object to hold image (and later the colour palette)
        new_image_data = ImageData(file_name_and_path)

        # Add to image dictionary
        new_image_data_id = ("Tab_" + str(self._image_data_id_counter))
        self._image_data_id_counter += 1

        if new_image_data_id not in  self._image_data_id_dictionary:
            self._image_data_id_dictionary[new_image_data_id] = new_image_data
        else:
            raise KeyError("The key:", new_image_data_id,
                           ", already exists in the model's dictionary of ImageData objects!")

        return new_image_data_id, new_image_data

    def remove_image_data(self, image_data_id: str) -> None:
        """Remove :class:`ImageData` object from the dictionary of images (:attr:`image_data_id_dictionary`) by its key.

        Args:
            image_data_id (str): The dictionary key ('Tab_xx') for the :class:`ImageData` object in the
                :attr:`image_data_id_dictionary` that should be removed.
        """

        self._image_data_id_dictionary.pop(image_data_id)

    def get_image_data(self, image_data_id: str) -> ImageData:
        """Returns the :class:`ImageData` object with the given ID/key in the :attr:`image_data_id_dictionary`.

        Args:
            image_data_id (str): The dictionary key/ID ('Tab_xx') for the :class:`ImageData` object in the
                :attr:`image_data_id_dictionary` that should be returned.

        Returns:
            (ImageData): :class:`ImageData` object with the given ID/key.
        """

        return self._image_data_id_dictionary.get(image_data_id)

    def generate_palette(self, image_data_id: str, tab: NewTab = None,
                         progress_callback=None, algorithm: type[PaletteAlgorithm] = None) -> None:
        """Generate the colour palette for the image in the :class:`ImageData` object with the given image_data_id ID.

        The recoloured image, colour palette and relative frequencies of each colour are added to the
        :class:`ImageData` object with the image_data_id dictionary key.

        Args:
            image_data_id (str): The dictionary key/ID ('Tab_xx') for the :class:`ImageData` object in the
                :attr:`image_data_id_dictionary` for which the colour palette of its associated image
                is to be generated for.
            tab (NewTab): The :class:`NewTab` linked to the image that is to have its colour palette generated.
            progress_callback (QtCore.SignalInstance): Signal that when emitted, is used to update the GUI.
            algorithm (type[PaletteAlgorithm]): The algorithm class to be used to generate the colur palette.
        """

        image_data = self.get_image_data(image_data_id)
        image_data.continue_thread = True

        # Get algorithm and process image with it
        algorithm = self._get_algorithm(algorithm=algorithm)
        if progress_callback is not None and tab is not None:
            algorithm.set_progress_callback(progress_callback, tab, image_data)

        # Set algorithm type used for the given image
        image_data.algorithm_used = type(algorithm)

        # Generate colour palette
        image = image_data.image.copy()
        new_recoloured_image, image_colour_palette, new_relative_frequencies = \
            algorithm.generate_colour_palette(image)

        # Check if image_data_id still exists
        if image_data_id in self._image_data_id_dictionary:

            # Assign properties to image_data
            self._image_data_id_dictionary[image_data_id].recoloured_image = new_recoloured_image
            self._image_data_id_dictionary[image_data_id].colour_palette = image_colour_palette
            self._image_data_id_dictionary[image_data_id].colour_palette_relative_frequency = new_relative_frequencies

            # Sort colour palette by relative frequency
            self._image_data_id_dictionary[image_data_id].sort_colour_palette(reverse=True)

    def _read_settings(self) -> None:
        """Read in the application settings from the ColourPaletteExtractor.ini settings file."""

        print("Reading in application settings...")
        self._settings = get_settings()

        # Check if settings file exists
        if not self._settings.contains('output directory/user directory'):
            print("Settings file not found...")
            self.write_default_settings()
        else:
            print("Settings file found...")
            self._settings.setValue('output directory/temporary directory',
                                    self._temp_dir.name)  # Update path to new temporary directory
            self._settings.sync()

    def _get_algorithm(self, algorithm: type[PaletteAlgorithm] = None) -> PaletteAlgorithm:
        """Get an instance of the algorithm class to be used to generate the colour palette of an image.

        If no algorithm is provided, the selected algorithm in the ColourPaletteExtractor.ini settings file.

        Args:
            algorithm (type[PaletteAlgorithm]): (Optional). If provided, it is checked to make sure that it is a
                valid algorithm class and and instance of that class is returned.

        Returns:
            (PaletteAlgorithm): Instance of the algorithm class.
        """

        if algorithm is None:
            # Create a new instance of the selected algorithm in the settings
            return self._settings.value("algorithm/selected algorithm")()

        else:
            # Use provided algorithm class
            if self._check_algorithm_valid(algorithm_class=algorithm):
                return algorithm()
            else:
                raise ValueError(algorithm, "is not a valid Class type!")
