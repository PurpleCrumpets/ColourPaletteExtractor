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
from PySide2.QtGui import QImage
from skimage import io, color

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

        # TODO: Need to check that the image has been saved using three colour channels (assuming RGB)
        # TODO: Check colour space and adapt to that
        # Otherwise - remove alpha channel in the case of PNG images
        # Convert from greyscale to rgb as well

        if file_name_and_path is None:
            raise ValueError("The path to an image cannot be None!")

        else:
            self._file_name_and_path = file_name_and_path
            self._image = io.imread(file_name_and_path)

            if self._image.shape == 4:
                self._remove_alpha_channel()

            _, self._extension = os.path.splitext(file_name_and_path)
            self._name = os.path.basename(file_name_and_path)
            while "." in self._name:
                self._name = os.path.splitext(self._name)[0]
            # TODO: what happens if the file has no extension?

    def sort_colour_palette(self, reverse=True):
        self._colour_palette = [colour for _, colour in sorted(zip(self._colour_palette_relative_frequency,
                                                                   self._colour_palette),
                                                               key=lambda pair: pair[0],
                                                               reverse=reverse)]
        self._colour_palette_relative_frequency.sort(reverse=reverse)

    @property
    def continue_thread(self):
        return self._continue_thread

    @continue_thread.setter
    def continue_thread(self, value: bool):
        self._continue_thread = value

    @property
    def algorithm_used(self):
        return self._algorithm_used

    @algorithm_used.setter
    def algorithm_used(self, value: type[palettealgorithm.PaletteAlgorithm]):
        self._algorithm_used = value

    @property
    def colour_palette_relative_frequency(self):
        return self._colour_palette_relative_frequency

    @colour_palette_relative_frequency.setter
    def colour_palette_relative_frequency(self, value):
        self._colour_palette_relative_frequency = value

    @property
    def file_name_and_path(self):
        return self._file_name_and_path

    @property
    def extension(self):
        return self._extension

    @property
    def image(self):
        return self._image

    @property
    def recoloured_image(self):
        return self._recoloured_image

    @recoloured_image.setter
    def recoloured_image(self, value):
        self._recoloured_image = value

    @property
    def colour_palette(self):
        return self._colour_palette

    @colour_palette.setter
    def colour_palette(self, value):
        self._colour_palette = value

    @staticmethod
    def get_image_as_q_image(image):
        if image.ndim == 3:
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            return QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        elif image.ndim == 2:
            height, width = image.shape
            bytes_per_line = 1 * width
            return QImage(image.data, width, height, bytes_per_line, QImage.Format_Indexed8)
        else:
            raise ValueError("The provided image should be a greyscale image, RGB image or ARGB image!")

    def _remove_alpha_channel(self):
        self._image = color.rgba2rgb(self._image)

    def _check_colour_space(self):
        print("Checking colour space")

        # rgb = io.imread(file_name_and_path)
        # (r, g, b) = rgb[0, 0]
        # print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))
        #
        # # Update pixel at [0, 0] to be blue to confirm the white point
        # rgb[0, 0] = (0, 0, 255)
        # (r, g, b) = rgb[0, 0]
        # print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))
        #
        # lab = color.rgb2lab(rgb, illuminant="D65")
        #
        # (r, g, b) = lab[0, 0]
        # print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))

        # print("Done!")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
