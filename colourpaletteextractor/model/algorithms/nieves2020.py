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

from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from skimage import color
from skimage import img_as_ubyte
import time

import colourpaletteextractor.model.algorithms.cielabcube as cielabcube
import colourpaletteextractor.model.algorithms.palettealgorithm as palettealgorithm

from colourpaletteextractor import _settings

class Nieves2020(palettealgorithm.PaletteAlgorithm, ABC):
    """Abstract class representing an algorithm to extract the colour palette from an image.

    Based on the algorithm proposed by Nieves et al. (2020); see `algorithm` for more information.

    .. _algorithm:
       https://doi.org/10.1364/AO.378659

    """

    # Default algorithm primary constants
    CUBE_SIZE = 20
    """Default delta-E* length of cube side (units)."""

    THRESHOLD = 0.03
    """Minimum threshold colour in each cube (0.03 = 3%) for primary relevancy requirements."""

    # Default algorithm secondary constants
    C_STAR_PERCENTILE = 50
    """x-th percentile of C* (50%) for secondary relevancy requirements."""

    SECONDARY_THRESHOLD = THRESHOLD / 8
    """Minimum secondary pixel count (%) for secondary relevancy requirements."""

    MIN_L_STAR = 80
    """Minimum L* value for secondary relevancy requirements (units)."""

    def __init__(self, name, url):

        super().__init__(name, url)

        # Set the primary parameters for the algorithm to the default values
        self._cube_size = Nieves2020.CUBE_SIZE
        self._threshold = Nieves2020.THRESHOLD

        # Set the secondary parameters for the algorithm to the default values
        self._c_star_percentile = Nieves2020.C_STAR_PERCENTILE
        self._secondary_threshold = Nieves2020.SECONDARY_THRESHOLD
        self._min_l_star = Nieves2020.MIN_L_STAR

    def generate_colour_palette(self, image: np.array) -> tuple[np.array, list[np.array], list[float]]:
        """Generate the colour palette and the recoloured image of the provided image.

        Args:
            image (np.array): The image for which the colour palette is to be generated (in sRGB colour space).

        Returns:
            (np.array): The recoloured image using only the colours in the colour palette.
            (list[np.array]): The list of colours ([R,G,B] triplets) in the image's colour palette.
            (list[float]): The relative frequencies of the colours in the recoloured image.
        """

        # Initial progress = 0%
        self._set_progress(0)
        if not self._continue_thread:
            return None, [], []

        # Convert greyscale image into an RGB image
        if image.ndim == 2:
            image = color.gray2rgb(image)

        # Step 1: Compute L*, a*, b* and C* of each pixel (under D65 illuminant)
        lab = convert_rgb_2_lab(image)
        c_stars = get_c_stars(lab)
        pixel_count = lab.size / lab.shape[2]

        # Progress = 5%
        self._set_progress(5)
        if not self._continue_thread:
            return None, [], []

        # Step 2: Divide CIELAB colour space into cubes
        cubes, cube_assignments = self._divide_cielab_space(lab, 10)  # Progress = 10%
        if not self._continue_thread:
            return None, [], []

        # Steps 3-12: Determine if cube colour is relevant
        self._assign_pixels_to_cube(lab, cubes, cube_assignments, c_stars, 25)  # Progress = 25%
        if not self._continue_thread:
            return None, [], []

        self._set_cubes_relevance_status(cubes, pixel_count, c_stars, 40)  # Progress = 40%
        if not self._continue_thread:
            return None, [], []

        # Step 13: Obtain relevant colours
        relevant_cubes = self._get_relevant_cubes(cubes, 50)
        if not self._continue_thread:
            return None, [], []

        if _settings.__VERBOSE__:
            print("Number of relevant colours:", len(relevant_cubes))

        # Step 14-19: Segmenting image in terms of relevant colours
        self._update_pixel_colours(lab, cubes, cube_assignments, relevant_cubes, 90)  # Progress = 90%
        if not self._continue_thread:
            return None, [], []

        # Convert image back from CIELAB back into RGB
        recoloured_image = convert_lab_2_rgb(lab)
        self._set_progress(95)  # Progress = 95%
        if not self._continue_thread:
            return None, [], []

        # Get colour palette as a list of rgb colours
        colour_palette = []
        for cube in relevant_cubes:
            colour = convert_lab_2_rgb(cube.mean_colour)  # Scale to 8-bit
            colour_palette.append(colour)

            if _settings.__VERBOSE__:
                lab_mean_colour = cube.mean_colour.copy()
                print("Cube mean CIELAB colour:", lab_mean_colour, "Cube mean sRGB colour:", colour)

        # Progress = 97%
        self._set_progress(97)
        if not self._continue_thread:
            return None, [], []

        # Get relative frequency of each colour
        relative_frequencies = cielabcube.get_relative_frequencies(relevant_cubes=relevant_cubes,
                                                                   total_pixels=int(pixel_count))

        # Progress = 100%
        self._set_progress(100)

        return recoloured_image, colour_palette, relative_frequencies

    @abstractmethod
    def _divide_cielab_space(self, lab, final_percent) -> tuple[np.array, np.array]:
        """Generate CIELAB cubes for the image, returning the coordinates of the cube that each pixel is to be assigned.

        Args:
            lab (np.array): The image in the CIELAB colour space.
            final_percent (int): Percentage value that the progress bar should finish on after completing this method.

        Returns:
            (np.array): Array of :class:`cielabcube.CielabCube` objects for pixels to be assigned to.
            (np.array): Array of cube coordinates corresponding to each pixel in the image.
        """

        pass

    def _assign_pixels_to_cube(self, lab: np.array, cubes: np.array, cube_assignments: np.array,
                               c_stars: np.array, final_percent: int) -> None:
        """Add each pixel to their assigned CIELAB cube.

        Args:
            lab (np.array): The image in the CIELAB colour space.
            cubes (np.array): Array of :class:`cielabcube.CielabCube` objects for pixels to be assigned to.
            cube_assignments (np.array): Array of cube coordinates corresponding to each pixel in the image.
            c_stars (np.array): Array of C* values corresponding to each pixel in the image.
            final_percent (int): Percentage value that the progress bar should finish on after completing this method.
        """

        start_time = time.time()
        rows = lab.shape[0]
        cols = lab.shape[1]

        # Get progress bar increments
        increment_percent = self._get_increment_percent(final_percent, rows)
        update_progress = 0

        if _settings.__VERBOSE__:
            print("Assigning each pixel to the appropriate CIELAB cube...")

        for i in range(rows):  # For each row of image
            for j in range(cols):  # For each column of image
                pixel = lab[i, j]
                c_star = c_stars[i, j]
                pixel_coordinates = cube_assignments[i, j]
                cube = cubes[pixel_coordinates[0], pixel_coordinates[1], pixel_coordinates[2]]
                cube.add_pixel_to_cube(pixel, c_star)

            # Update progress bar (every eighth loop to reduce GUI thread burden)
            if update_progress == 7:
                self._increment_progress(8 * increment_percent)
                update_progress = 0
                if not self._continue_thread:
                    return
            else:
                update_progress += 1

        # Set progress bar (prevent rounding issues)
        self._set_progress(final_percent)

        if _settings.__VERBOSE__:
            print("--- %s seconds for Python cube assignment loop ---" % (time.time() - start_time))

    def _set_cubes_relevance_status(self, cubes: np.array, pixel_count: int, c_stars: np.array,
                                    final_percent: int) -> None:
        """Set the relevancy status of each cube according to the requirements specified by Nieves et al. (2020).

        If the cube is found to meet the relevancy requirements, it will contribute a colour towards the image's
        colour palette.

        Args:
            cubes (np.array): Array of :class:`cielabcube.CielabCube` objects that pixels have been assigned to.
            pixel_count (int): The number of pixels in the image.
            c_stars (np.array): Array of C* values corresponding to each pixel in the image.
            final_percent (int): Percentage value that the progress bar should finish on after completing this method.

        Raises:
            ValueError: If the number of pixels analysed does not match the total number of pixels in the image (not all
                of the pixels have been accounted for).
        """

        # Primary relevancy variables
        threshold_pixel_count = pixel_count * self._threshold  # Minimum number of pixels to be in a cube

        # Secondary relevancy variables
        c_star_image_percentile_value = np.percentile(c_stars, self._c_star_percentile)
        secondary_threshold_pixel_count = pixel_count * self._secondary_threshold  # Secondary minimum number of pixels

        if _settings.__VERBOSE__:
            print("Secondary pixel count threshold:", secondary_threshold_pixel_count)

        # Dimensions of matrix of cubes
        l_star_dim = cubes.shape[0]
        a_star_dim = cubes.shape[1]
        b_star_dim = cubes.shape[2]

        tot_pixels = 0  # Number of pixels that have been processed. Initially 0

        # Get progress bar increments
        increment_percent = self._get_increment_percent(final_percent, l_star_dim)
        update_progress = 0

        for i in range(l_star_dim):
            for j in range(a_star_dim):
                for k in range(b_star_dim):
                    cube = cubes[i, j, k]

                    # Step 4: Get cube pixel count
                    num_pixels = len(cube.pixels)
                    tot_pixels = tot_pixels + num_pixels  # Update current pixel count

                    # Step 5: Calculate mean pixel colour (cube colour)
                    cube.calculate_mean_colour()

                    # Step 6-11: Determine if cube is relevant
                    if num_pixels > threshold_pixel_count:  # possibly >= (pseudo-code in paper uses >)

                        if _settings.__VERBOSE__:
                            print("Cube with coordinates: " + str(cube.coordinates)
                                  + " meets primary requirements with:", num_pixels, "out of", pixel_count, "pixels")

                        cube.relevant = True

                    elif num_pixels == 0:  # No pixels in cube
                        cube.relevant = False

                    else:  # Secondary relevance checks
                        # At least 3/8% of pixels in cube have L* > 80
                        # OR At least 3/8% of pixels in cube have C* above 50th percentile OF THE IMAGE

                        # Get number of pixels in cube that meet the secondary C* requirements
                        c_stars = cube.c_stars
                        c_star_cube_count = np.count_nonzero(c_stars > c_star_image_percentile_value)

                        # Get the number of pixels in cube that meet the secondary L* requirements
                        l_stars = cube.l_stars
                        l_star_cube_count = np.count_nonzero(l_stars > self._min_l_star)

                        # Check if cube meets secondary relevancy requirements
                        if c_star_cube_count > secondary_threshold_pixel_count:
                            cube.relevant = True

                            if _settings.__VERBOSE__:
                                print("Cube below with coordinates: " + str(cube.coordinates)
                                      + " meets secondary requirements for C*...")
                                print("----C* cube count:", c_star_cube_count,
                                      "; L* cube count:", l_star_cube_count,
                                      "; Threshold pixel count:", threshold_pixel_count,
                                      "; Secondary threshold pixel count", secondary_threshold_pixel_count,
                                      "; Number of pixels:", num_pixels, "out of", pixel_count)

                        elif l_star_cube_count > secondary_threshold_pixel_count:
                            cube.relevant = True

                            if _settings.__VERBOSE__:
                                print("Cube below with coordinates: " + str(cube.coordinates)
                                      + " meets tertiary requirements for L*...")
                                print("----C* cube count:", c_star_cube_count,
                                      "; L* cube count:", l_star_cube_count,
                                      "; Threshold pixel count:", threshold_pixel_count,
                                      "; Secondary threshold pixel count", secondary_threshold_pixel_count,
                                      "; Number of pixels:", num_pixels, "out of", pixel_count)

                        else:
                            cube.relevant = False

            # Update progress bar (every fourth loop to reduce GUI thread burden)
            if update_progress == 7:
                self._increment_progress(8 * increment_percent)
                update_progress = 0
                if not self._continue_thread:
                    return
            else:
                update_progress += 1

        # Set progress bar (prevent rounding issues)
        self._set_progress(final_percent)

        if tot_pixels != pixel_count:
            raise ValueError("Not all of the pixels have been accounted for!",
                             tot_pixels, "analysed out of", str(pixel_count) + ".")

    def _get_relevant_cubes(self, cubes: np.array, final_percent: int):
        """Get the list of the relevant cubes.

        Args:
            cubes (np.array): Array of :class:`cielabcube.CielabCube` objects that pixels have been assigned to.
            final_percent (int): Percentage value that the progress bar should finish on after completing this method.

        Returns:
            list(cielabcube.CielabCube): List of relevant cubes.

        Raises:
            ValueError: If no relevant cubes are found.
        """

        relevant_cubes = []
        num_relevant_cubes = 0

        l_star_dim = cubes.shape[0]
        a_star_dim = cubes.shape[1]
        b_star_dim = cubes.shape[2]

        # Getting progress bar increments
        increment_percent = self._get_increment_percent(final_percent, l_star_dim)
        update_progress = True

        for i in range(l_star_dim):
            for j in range(a_star_dim):
                for k in range(b_star_dim):
                    cube = cubes[i, j, k]

                    if cube.relevant:
                        relevant_cubes.append(cube)
                        num_relevant_cubes += 1

            # Update progress bar (every eighth loop to reduce GUI thread burden)
            if update_progress == 7:
                self._increment_progress(8 * increment_percent)
                update_progress = 0
                if not self._continue_thread:
                    return
            else:
                update_progress += 1

        # Set progress bar (prevent rounding issues)
        self._set_progress(final_percent)

        # Check that at least one relevant cube has been found
        if num_relevant_cubes > 0:
            return relevant_cubes
        else:
            raise ValueError("No relevant cubes found!")

    def _update_pixel_colours(self, lab: np.array, cubes: np.array, cube_assignments: np.array,
                              relevant_cubes: list[cielabcube.CielabCube], final_percent: int) -> None:
        """Update the colours in the image using the mean colours from the cubes that are deemed to be relevant.

        Args:
            lab (np.array): The image in the CIELAB colour space.
            cubes (np.array): Array of :class:`cielabcube.CielabCube` objects that pixels have been assigned to.
            cube_assignments (np.array): Array of cube coordinates corresponding to each pixel in the image.
            relevant_cubes(list(cielabcube.CielabCube): List of relevant cubes.
            final_percent (int): Percentage value that the progress bar should finish on after completing this method.
        """

        # Get array of relevant_cube mean colours
        relevant_cubes_mean_colours = []
        for cube in relevant_cubes:
            relevant_cubes_mean_colours.append(cube.mean_colour)
        relevant_cubes_mean_colours = np.array(relevant_cubes_mean_colours)

        start_time = time.time()
        rows = lab.shape[0]
        cols = lab.shape[1]

        # Get progress bar increments
        increment_percent = self._get_increment_percent(final_percent, rows)
        update_progress = 0

        if _settings.__VERBOSE__:
            print("Updating pixel colours...")

        # Update each pixel's colour
        for i in range(rows):  # For each row of image
            for j in range(cols):  # For each column of image
                pixel_coordinates = cube_assignments[i, j]

                # Check if pixel is in the relevant cube by finding the
                # cube it was assigned to and checking if it is a relevant cube
                cube = cubes[pixel_coordinates[0], pixel_coordinates[1], pixel_coordinates[2]]

                if cube.relevant:
                    lab[i, j] = cube.mean_colour  # Assign cube's mean colour
                    cube.increment_pixel_count_after_reassignment()  # Increase count of pixels with this colour by one
                else:
                    # Calculate closest relevant cube and use the mean colour for the pixel
                    pixel = np.full((relevant_cubes_mean_colours.shape[0], lab.shape[2]), lab[i, j])
                    euclidean_distances = np.linalg.norm(pixel - relevant_cubes_mean_colours, axis=1)
                    min_distance_index = np.argmin(euclidean_distances)  # If there is a tie, the first colour is chosen

                    # Update pixel's colour with the closest colour
                    new_pixel_colour = relevant_cubes_mean_colours[min_distance_index]
                    lab[i, j] = new_pixel_colour
                    relevant_cubes[min_distance_index] \
                        .increment_pixel_count_after_reassignment()  # Increase count of pixels with this colour by one

            # Update progress bar (every eighth loop to reduce GUI thread burden)
            if update_progress == 7:
                self._increment_progress(8 * increment_percent)
                update_progress = 0
                if not self._continue_thread:
                    return
            else:
                update_progress += 1

        # Set progress bar (prevent rounding issues)
        self._set_progress(final_percent)

        if _settings.__VERBOSE__:
            print("--- %s seconds for Python pixel colour update loop ---" % (time.time() - start_time))


class Nieves2020OffsetCubes(Nieves2020):
    """Subclass of :class:`Nieves2020` with the cube coordinates corresponding to the cube's corner closest the origin.

    As a result, there are eight cube that touch the origin in the CIELAB colour space.
    """

    NAME = "Nieves, Gomez-Robledo, Chen and Romero (2020) - Cube corners at CIELAB origin"
    """Name of the algorithm."""

    URL = "https://doi.org/10.1364/AO.378659"
    "Link to more information about the algorithm."

    def __init__(self):
        """Constructor."""
        super().__init__(Nieves2020OffsetCubes.NAME, Nieves2020OffsetCubes.URL)

    def _get_cube_assignments(self, lab: np.array) -> np.array:
        """Get an array of cube coordinates corresponding to each pixel's assignment.

        * Divide each pixel's L*, a*, and b* value by :attr:`Nieves2020.CUBE_SIZE` (20), returning
        the number of times each value fits completely with no remainder (floor divide).

        Args:
            lab (np.array): The image in the CIELAB colour space.

        Returns:
            (np.array): Array of cube coordinates corresponding to each pixel in the image.
        """
        # Calculate how many cubes to generate
        return (np.floor_divide(lab, self._cube_size)).astype(int)  # Cube coordinates for each pixel

    def _divide_cielab_space(self, lab: np.array, final_percent: int) -> Optional[tuple[np.array, np.array]]:
        """Generate CIELAB cubes for the image, returning the coordinates of the cube that each pixel is to be assigned.

        Returns none if the thread created to generate the colour palette is cancelled.

        Args:
            lab (np.array): The image in the CIELAB colour space.
            final_percent (int): Percentage value that the progress bar should finish on after completing this method.

        Returns:
            (np.array): Array of :class:`cielabcube.CielabCube` objects for pixels to be assigned to.
            (np.array): Array of cube coordinates corresponding to each pixel in the image.
        """

        # Calculate how many cubes to generate
        cube_assignments = self._get_cube_assignments(lab)  # Cube coordinates for each pixel

        # Check extent of cube generation
        l_star_max = cube_assignments[:, :, 0].max()
        l_star_min = 0  # l_star_min is always 0
        a_star_max = cube_assignments[:, :, 1].max()
        a_star_min = cube_assignments[:, :, 1].min()
        b_star_max = cube_assignments[:, :, 2].max()
        b_star_min = cube_assignments[:, :, 2].min()

        if _settings.__VERBOSE__:
            print("l* range: " + str(l_star_min) + "," + str(l_star_max))
            print("a* range: " + str(a_star_min) + "," + str(a_star_max))
            print("b* range: " + str(b_star_min) + "," + str(b_star_max))

        # Make sure ranges are valid and always include 0 in the range
        if a_star_min > 0:
            a_star_min = 0
        if b_star_min > 0:
            b_star_min = 0
        if a_star_max < 0:
            a_star_max = 0
        if b_star_max < 0:
            b_star_max = 0

        # Ranges for each component
        l_star_range = l_star_max - l_star_min + 1
        a_star_range = a_star_max - a_star_min + 1
        b_star_range = b_star_max - b_star_min + 1

        # Get progress bar increments
        increment_percent = self._get_increment_percent(final_percent, l_star_range)
        update_progress = 0

        # Generate required cubes and adding them to the 3D array of cubes
        cubes = np.empty([l_star_range, a_star_range, b_star_range], dtype=cielabcube.CielabCube)
        for l_star in range(l_star_min, l_star_max + 1):
            for a_star in range(a_star_min, a_star_max + 1):
                for b_star in range(b_star_min, b_star_max + 1):

                    # Generate new cube
                    cubes[l_star, a_star, b_star] = cielabcube.CielabCube(l_star, a_star, b_star)
                    # This approach works as negative l_Star will be assigned to the far right of the cube and work back

            # Update progress bar (every eighth loop to reduce GUI thread burden)
            if update_progress == 7:
                self._increment_progress(8 * increment_percent)
                update_progress = 0
                if not self._continue_thread:
                    return
            else:
                update_progress += 1

        # Set progress bar (prevent rounding issues)
        self._set_progress(final_percent)

        if _settings.__VERBOSE__:
            print(cubes.size, "CIELAB cubes generated...")

        return cubes, cube_assignments


class Nieves2020CentredCubes(Nieves2020):
    """Subclass of :class:`Nieves2020` with the cube coordinates corresponding to the centre of the cube.

    As a result, there is only one cube that touches the origin in the CIELAB colour space (is in fact centred on the
     origin).
    """

    NAME = "Nieves, Gomez-Robledo, Chen and Romero (2020) - Cube centred on CIELAB origin"
    """Name of the algorithm."""

    URL = "https://doi.org/10.1364/AO.378659"
    "Link to more information about the algorithm."

    def __init__(self):

        super().__init__(Nieves2020CentredCubes.NAME, Nieves2020CentredCubes.URL)

    def _get_cube_assignments(self, lab: np.array) -> np.array:
        """Get an array of cube coordinates corresponding to each pixel's assignment.

        * Temporarily round each pixel LAB value to the nearest multiple of :attr:`Nieves2020.CUBE_SIZE` (20).
        * Divide all of these values by 20 to get each pixel's cube assignment.

        Args:
            lab (np.array): The image in the CIELAB colour space.

        Returns:
            (np.array): Array of cube coordinates corresponding to each pixel in the image.
        """

        cube_assignments = self._cube_size * np.round(lab / self._cube_size)
        cube_assignments = (cube_assignments / self._cube_size).astype(int)
        return cube_assignments  # Cube coordinates for each pixel

    def _divide_cielab_space(self, lab: np.array, final_percent: int) -> Optional[tuple[np.array, np.array]]:
        """Generate CIELAB cubes for the image, returning the coordinates of the cube that each pixel is to be assigned.

        Returns none if the thread created to generate the colour palette is cancelled.

        Args:
            lab (np.array): The image in the CIELAB colour space.
            final_percent (int): Percentage value that the progress bar should finish on after completing this method.

        Returns:
            (np.array): Array of :class:`cielabcube.CielabCube` objects for pixels to be assigned to.
            (np.array): Array of cube coordinates corresponding to each pixel in the image.
        """

        # Calculate how many cubes to generate
        cube_assignments = self._get_cube_assignments(lab)

        l_star_max = cube_assignments[:, :, 0].max()
        l_star_min = 0  # l_star_min is always 0
        a_star_max = cube_assignments[:, :, 1].max()
        a_star_min = cube_assignments[:, :, 1].min()
        b_star_max = cube_assignments[:, :, 2].max()
        b_star_min = cube_assignments[:, :, 2].min()

        if _settings.__VERBOSE__:
            print("l* range: " + str(l_star_min) + "," + str(l_star_max))
            print("a* range: " + str(a_star_min) + "," + str(a_star_max))
            print("b* range: " + str(b_star_min) + "," + str(b_star_max))

        # Make sure ranges are valid and always include 0 in the range
        if a_star_min > 0:
            a_star_min = 0
        if b_star_min > 0:
            b_star_min = 0
        if a_star_max < 0:
            a_star_max = 0
        if b_star_max < 0:
            b_star_max = 0

        # Ranges for each component
        l_star_range = l_star_max - l_star_min + 1
        a_star_range = a_star_max - a_star_min + 1
        b_star_range = b_star_max - b_star_min + 1

        # Get progress bar increments
        increment_percent = self._get_increment_percent(final_percent, l_star_range)
        update_progress = 0

        # Generate required cubes and adding them to the 3D array of cubes
        cubes = np.empty([l_star_range, a_star_range, b_star_range], dtype=cielabcube.CielabCube)
        for l_star in range(l_star_min, l_star_max + 1):
            for a_star in range(a_star_min, a_star_max + 1):
                for b_star in range(b_star_min, b_star_max + 1):

                    # Generate new cube
                    cubes[l_star, a_star, b_star] = cielabcube.CielabCube(l_star, a_star, b_star)
                    # This approach works as negative l_Star will be assigned to the far right of the cube and work back

            # Update progress bar (every eighth loop to reduce GUI thread burden)
            if update_progress == 7:
                self._increment_progress(8 * increment_percent)
                update_progress = 0
                if not self._continue_thread:
                    return
            else:
                update_progress += 1

        # Set progress bar (prevent rounding issues)
        self._set_progress(final_percent)

        if _settings.__VERBOSE__:
            print(cubes.size, "CIELAB cubes generated...")

        return cubes, cube_assignments


def convert_rgb_2_lab(image: np.array) -> np.array:
    """Convert an image from the sRGB colour space to the CIELAB colour space.

    The alpha channel of the image (RGBA) is removed if present.

    Illuminant = D65 (name of the illuminant)
    Observer = 2 (aperture angle of observer)

    Args:
        image (np.array): The image in the sRGB colour space.

    Returns:
        (np.array): The image in the CIELAB colour space.
    """

    if image.shape[2] == 4:
        image = color.rgba2rgb(image)  # Removing alpha channel if present

    return color.rgb2lab(image, illuminant="D65")


def convert_lab_2_rgb(image: np.array) -> np.array:
    """Convert an image from the CIELAB colour space to the sRGB colour space.

    After conversion, the image is scaled to 8-bit per colour channel (24-bit image).

    Illuminant = D65 (name of the illuminant)
    Observer = 2 (aperture angle of observer)

    Args:
        image (np.array): The image in the CIELAB colour space.

    Returns:
        (np.array): The image in the sRGB colour space.
    """

    new_image = color.lab2rgb(image, illuminant="D65")
    new_image = img_as_ubyte(new_image)  # Scale to 8-bits per channel

    return new_image


def get_c_stars(lab: np.array) -> np.array:
    """Get the matrix of C* (chroma) values for each pixel in the image.

    .. math::
        C^{*} = \sqrt{{a^{*}}^{2} + {b^{*}}^{2}}

    Args:
        lab (np.array): The image in the CIELAB colour space.

    Returns:
        (np.array): Array of C* values corresponding to each pixel in the image.
    """

    lab_squared = np.square(lab)  # Square each element of CIELAB image
    a_star_squared = lab_squared[:, :, 1]
    b_star_squared = lab_squared[:, :, 2]
    c_stars = np.sqrt(a_star_squared + b_star_squared)  # C* = sqrt(a*^2 + b*^2)
    return c_stars
