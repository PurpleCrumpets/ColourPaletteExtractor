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

import os.path

import numpy as np
from PySide2.QtGui import QImage
from skimage import io, color, img_as_ubyte

import colourpaletteextractor.model.algorithms.palettealgorithm as palettealgorithm


class ImageData:
    """Object to hold the data associated with an image to be analysed.

    Stores the original image, its colour palette, the recoloured image, the relative frequency of each colour in the
    recoloured image, the algorithm used to generate the colour palette and the execution status of the thread used
    to generate the colour palette.

    Args:
        file_name_and_path (str): Path to the image to be added.


    Raises:
        ValueError: If the file_name_and_path argument is None.

    """

    def __init__(self, file_name_and_path: str):

        self._recoloured_image = None
        self._colour_palette = []
        self._colour_palette_relative_frequency = []
        self._algorithm_used = None
        self._continue_thread = True

        if file_name_and_path is None:
            raise ValueError("The path to an image cannot be None!")

        else:
            self._file_name_and_path = file_name_and_path
            self._image = img_as_ubyte(io.imread(file_name_and_path))

            if self._image.shape == 4:  # Removing Alpha channel from image
                self._image = color.rgba2rgb(self._image)

            # Get file name and extension
            _, self._extension = os.path.splitext(file_name_and_path)
            self._name = os.path.basename(file_name_and_path)
            while "." in self._name:
                self._name = os.path.splitext(self._name)[0]

    @staticmethod
    def get_image_as_q_image(image: np.array) -> QImage:
        """Convert a Numpy array representation of an image to a QImage.

        Args:
            image (np.array): An image represented by a Numpy array.

        Returns:
            (QImage): The image converted to a QImage.

        Raises:
            ValueError: If the provided image is not a greyscale, rGB or RGBA image (1, 3, or 4 colour channels).
        """

        if image.ndim == 3:
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            return QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        elif image.ndim == 2:
            height, width = image.shape
            bytes_per_line = 1 * width
            return QImage(image.data, width, height, bytes_per_line, QImage.Format_Indexed8)
        else:
            raise ValueError("The provided image should be a greyscale image, RGB image or RGBA image!")

    def sort_colour_palette(self, reverse: bool = True) -> None:
        """Sort the colour palette by their relative frequencies in the recoloured image.

        Args:
            reverse (bool): If True, the colour palette is sorted from largest relative frequency to the smallest.
                If False, the order is smallest to largest. The default is True.
        """

        self._colour_palette = [colour for _, colour in sorted(zip(self._colour_palette_relative_frequency,
                                                                   self._colour_palette),
                                                               key=lambda pair: pair[0],
                                                               reverse=reverse)]
        self._colour_palette_relative_frequency.sort(reverse=reverse)

    @property
    def continue_thread(self) -> bool:
        """Specify if the thread for generating the colour palette or the report should be cancelled.

        Returns:
            (bool): True if the thread should be continued. Otherwise False.
        """

        return self._continue_thread

    @continue_thread.setter
    def continue_thread(self, value: bool):
        self._continue_thread = value

    @property
    def algorithm_used(self) -> type[palettealgorithm.PaletteAlgorithm]:
        """The algorithm used to generate the image's colour palette.

        Returns:
            (type[palettealgorithm.PaletteAlgorithm]): The class name of the colour palette extraction algorithm.
        """

        return self._algorithm_used

    @algorithm_used.setter
    def algorithm_used(self, value: type[palettealgorithm.PaletteAlgorithm]):
        self._algorithm_used = value

    @property
    def colour_palette_relative_frequency(self) -> list[float]:
        """The relative frequencies of each colour in the colour palette in the recoloured image.

        The order of the relative frequencies matches the order of the colours in the colour palette.

        Returns:
            (list[float]): The list of relative frequencies of the colour palette.
        """

        return self._colour_palette_relative_frequency

    @colour_palette_relative_frequency.setter
    def colour_palette_relative_frequency(self, value: list[float]):
        self._colour_palette_relative_frequency = value

    @property
    def file_name_and_path(self) -> str:
        """The file path to the original image.

        Returns:
            (str): File path to the original image.

        """
        return self._file_name_and_path

    @property
    def extension(self) -> str:
        """The file extension of the original image.

        Returns:
            (str): The file extension of the original image.
        """

        return self._extension

    @property
    def image(self) -> np.array:
        """The original image, represented as a 2 or 3-D Numpy array.

        Returns:
            (np.array): The original image as a Numpy array.
        """

        return self._image

    @property
    def recoloured_image(self):
        """The recoloured image, represented as a 3-D Numpy array.

        Returns:
            (np.array): The recoloured image as a Numpy array.
        """

        return self._recoloured_image

    @recoloured_image.setter
    def recoloured_image(self, value: np.array):
        self._recoloured_image = value

    @property
    def colour_palette(self) -> list[np.array]:
        """The list of colours in the image's colour palette.

        Returns:
            (list[np.array]): The list of colours ([R,G,B] triplets) in the colour palette.
        """

        return self._colour_palette

    @colour_palette.setter
    def colour_palette(self, value: list[np.array]):
        self._colour_palette = value

    @property
    def name(self) -> str:
        """The name of the image, without its file extension.

        Returns:
            (str): The image file name, without its extension.
        """

        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
