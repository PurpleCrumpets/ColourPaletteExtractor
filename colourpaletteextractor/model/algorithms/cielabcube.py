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
from typing import Union

import numpy as np


class CielabCube:
    """A cube representing a fixed region in the CIELAB colour space.

    The cube is used to hold pixels in an image that exist within the cube's region of the CIELAB colour space. The
    input parameters do not refer to the actual L*, a* and b* values, but depend on the `CUBE_SIZE` specified by the
    colour palette algorithm (in particular, any variant on the `Nieves 2020`_ algorithm).

    In the case of the :class:`nieves2020.Nieves2020CentredCubes` algorithm, the coordinates refer to the centre of the
    cube. For the :class:`nieves2020.Nieves2020OffsetCubes` algorithm, the coordinates refer to the corner of the cube
    closest to the origin.

    Args:
        l_star_coord (int): Perceptual lightness cube coordinate
        a_star_coord (int): Green-red cube coordinate
        b_star_coord (int): Blue-yellow cube coordinate

    .. _Nieves 2020:
       https://doi.org/10.1364/AO.378659
    """

    def __init__(self, l_star_coord: int, a_star_coord: int, b_star_coord: int):

        self._l_star_coord = l_star_coord
        self._a_star_coord = a_star_coord
        self._b_star_coord = b_star_coord

        self._coordinates = np.array([self._l_star_coord, self._a_star_coord, self._b_star_coord])

        self._pixels = []  # List of pixels

        self._pixel_count_after_reassignment = 0  #

        self._mean_colour = np.empty([3])  # Mean colour of cube
        self._c_stars = []  # List of C* values for pixels in the cube

        self._relevant = False  # Cube is initially not considered to be a relevant colour

    @property
    def pixel_count_after_reassignment(self) -> int:
        """The number of pixels in the recoloured image with this cube's mean colour.

        Returns:
            (int): The number of pixels with the cube's mean colour.
        """

        return self._pixel_count_after_reassignment

    def increment_pixel_count_after_reassignment(self) -> None:
        """Increase the number of pixels with this cube's mean colour by one."""

        self._pixel_count_after_reassignment += 1

    @property
    def pixels(self) -> list[np.array]:
        """The list of pixels ([L*, a*, b*] triplets) in the cube.

        Returns:
            (list[np.array]): The list of pixels in the cube.
        """

        return self._pixels

    @property
    def coordinates(self) -> np.array:
        """The coordinates of the cube ([L*, a*, b*]).

        In the case of the :class:`nieves2020.Nieves2020CentredCubes` algorithm, the coordinates refer to the centre of
        the cube. For the :class:`nieves2020.Nieves2020OffsetCubes` algorithm, the coordinates refer to the corner of
        the cube closest to the origin.

        Returns:
            (np.array): The cube's coordinates.
        """

        return self._coordinates

    @property
    def mean_colour(self) -> np.array:
        """The mean colour of the pixels in the cube.

        Returns:
            (np.array): The mean colour of the cube as a [L*,a*,b*] triplet.
        """

        return self._mean_colour

    def calculate_mean_colour(self) -> None:
        """Calculate the mean colour of the pixels in the cube.

        Nothing is calculated if the number of pixels in the cube is equal to 0.
        """

        pixel_array = np.array(self._pixels)  # Convert from a list to a Numpy array
        if pixel_array.size != 0:
            self._mean_colour = pixel_array.mean(axis=0)

    @property
    def relevant(self) -> bool:
        """The relevancy status of the cube.

        Returns:
            (bool): True if the cube is a relevant cube. Otherwise False.
        """

        return self._relevant

    @relevant.setter
    def relevant(self, value: bool) -> None:
        self._relevant = value

    @property
    def l_stars(self) -> np.array:
        """The L* values for all pixels in the cube.

        Returns:
            (np.array): Array of L* values for all pixels in the cube.
        """

        pixel_array = np.array(self._pixels)
        return pixel_array[:, 0]  # First column of each row representing a pixel

    @property
    def c_stars(self) -> list[np.float64]:
        """The C* (chroma, relative saturation) values for all of the pixels in the cube.

        .. math::
            C^{*} = \sqrt{{a^{*}}^{2} + {b^{*}}^{2}}

        Returns:
            (list[np.float64]): The list of C* values for all pixels in the cube.
        """

        return self._c_stars

    def get_l_star_percentile_value(self, percentile: float) -> Union[int, np.percentile]:
        """Returns the L* value for the given percentile based on the pixels in the cube.

        Args:
            percentile (float): The percentile to calculate the L* value for.

        Returns:
            (Union[int, np.percentile]): The L* value for the chosen percentile. If no pixels are found, the return
                value is 0.
        """

        pixel_array = np.array(self._pixels)
        l_stars_array = pixel_array[:, 0]  # First column of each row representing a pixel

        if l_stars_array.size != 0:
            return np.percentile(l_stars_array, percentile)
        else:
            return 0

    def get_c_star_percentile_value(self, percentile: float) -> Union[int, np.percentile]:
        """Returns the C* value for the given percentile based on the pixels in the cube.

        Args:
            percentile (float): The percentile to calculate the C* value for.

        Returns:
            (Union[int, np.percentile]): The C* value for the chosen percentile. If no pixels are found, the return
                value is 0.
        """

        c_stars_array = np.array(self._c_stars)

        if c_stars_array.size != 0:
            return np.percentile(c_stars_array, percentile)
        else:
            return 0

    def add_pixel_to_cube(self, pixel: np.array, c_star: np.float64) -> None:
        """Assign a pixel to the cube.

        Args:
            pixel (np.array): The pixel as a [L*,a*,b*] triplet.
            c_star (np.float64): The C* (chroma, relative saturation) value for the pixel.
        """

        self._pixels.append(pixel)
        self._c_stars.append(c_star)


def get_relative_frequencies(relevant_cubes: list[CielabCube], total_pixels: int) -> list[float]:
    """Calculate the relative frequency of each colour (relevant colour) in the recoloured image.

    Args:
        relevant_cubes (list[CielabCube]): List of relevant :class:`CielabCube` objects.
        total_pixels (int): The total number of pixels in the image.

    Returns:
        (list[float]): The list of relative frequencies for each relevant cube.
    """

    frequencies = []
    for cube in relevant_cubes:
        frequency = cube.pixel_count_after_reassignment / total_pixels
        frequencies.append(frequency)

    return frequencies
