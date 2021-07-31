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


# import pyximport; pyximport.install(setup_args={"include_dirs": np.get_include()})
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from skimage import color
from skimage import img_as_ubyte
import time
import multiprocessing

import colourpaletteextractor.model.algorithms.cielabcube as cielabcube
import colourpaletteextractor.model.algorithms.palettealgorithm as palettealgorithm

# from colourpaletteextractor.model.algorithms import nieves2020cython


class Nieves2020(palettealgorithm.PaletteAlgorithm, ABC):

    COLOUR_CHANNELS = 3  # (R, G, B)

    # Default algorithm primary constants
    CUBE_SIZE = 20  # Default delta-E* length of cube side (units)
    THRESHOLD = 0.03  # Minimum threshold colour in each cube (0.03 = 3%)

    # Default algorithm secondary constants
    C_STAR_PERCENTILE = 50  # 50-th percentile of C*
    SECONDARY_THRESHOLD = 0.03 / 8  # Minimum secondary pixel count
    L_STAR_PERCENTILE_THRESHOLD = 0.03 / 8  # 3/8-th percentile
    MIN_L_STAR = 80  # Minimum L* value

    # TODO: Add cube size as variable in constructor
    # TODO: Add cube size check (ie make sure it divides into the CIELAB volume ok)

    def __init__(self, name, url):
        """Constructor."""
        super().__init__(name, url)

        # Setting the primary parameters for the algorithm to the default values
        self._cube_size = Nieves2020.CUBE_SIZE
        self._threshold = Nieves2020.THRESHOLD

        # Setting the secondary parameters for the algorithm to the default values
        self._c_star_percentile = Nieves2020.C_STAR_PERCENTILE
        self._l_star_percentile = Nieves2020.L_STAR_PERCENTILE_THRESHOLD
        self._secondary_threshold = Nieves2020.SECONDARY_THRESHOLD
        self._min_l_star = Nieves2020.MIN_L_STAR

    def generate_colour_palette(self, image) -> tuple[np.array, list[np.array], list[float]]:
        print("Generating colour palette...")

        self._set_progress(0)  # Initial progress = 0%
        if not self._continue_thread:
            return None, [], []

        # print(image.shape)

        # TODO: Add checks to make sure image is originally in the sRGB colour space

        # Convert greyscale image into an RGB image
        if image.ndim == 2:
            image = color.gray2rgb(image)

        # Step 1: Compute L*, a*, b* and C* of each pixel (under D65 illuminant)
        lab = convert_rgb_2_lab(image)
        c_stars = get_c_stars(lab)
        pixel_count = lab.size / Nieves2020.COLOUR_CHANNELS

        self._set_progress(5)  # Progress = 5%
        if not self._continue_thread:
            return None, [], []
        # print(pixel_count)

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
        print("Number of relevant colours:", len(relevant_cubes))

        # Step 14-19: Segmenting image in terms of relevant colours
        # old_lab = lab.copy()
        self._update_pixel_colours(lab, cubes, cube_assignments, relevant_cubes, 90)  # Progress = 90%
        if not self._continue_thread:
            return None, [], []

        # if np.array_equal(old_lab, lab):
        #     print("Nothing has changed")
        # else:
        #     print("Something as changed!")

        # Convert image back into rgb
        recoloured_image = convert_lab_2_rgb(lab)
        self._set_progress(95)  # Progress = 95%
        if not self._continue_thread:
            return None, [], []

        # Get colour palette as a list of rgb colours
        colour_palette = []
        for cube in relevant_cubes:
            lab_mean_colour = cube.mean_colour.copy()
            colour = convert_lab_2_rgb(cube.mean_colour)  # Scale to 8-bit
            colour_palette.append(colour)
            # print("Cube mean CIELAB colour:", lab_mean_colour, "Cube mean sRGB colour:", colour)
        self._set_progress(97)  # Progress = 97%
        if not self._continue_thread:
            return None, [], []

        # Get relative frequency of each colour
        relative_frequencies = cielabcube.get_relative_frequencies(relevant_cubes=relevant_cubes,
                                                                   total_pixels=int(pixel_count))

        self._set_progress(100)  # Progress = 100%

        return recoloured_image, colour_palette, relative_frequencies

    @abstractmethod
    def _divide_cielab_space(self, lab, final_percent):
        """Generate the required CIELAB cubes for the given image
        and return the coordinates of the cube that each pixel is to be assigned to."""
        pass

    def _assign_pixels_to_cube(self, lab, cubes, cube_assignments, c_stars, final_percent):
        """Add each pixel to their assigned CIELAB cube."""

        # Using Cython
        # start_time = time.time()
        # nieves2020cython.divide_cielab_space(lab, cube_assignments, cubes)
        # print("--- %s seconds for Cython ---" % (time.time() - start_time))
        # print(len(cubes[0, 0, 0].pixels))

        # Using Python
        start_time = time.time()
        rows = lab.shape[0]
        cols = lab.shape[1]

        # Getting progress bar increments
        increment_percent = self._get_increment_percent(final_percent, rows)
        update_progress = 0

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

        print("--- %s seconds for Python cube assignment loop ---" % (time.time() - start_time))

        # print(len(cubes[0, 0, 0].pixels))
        # print(cubes[0, 0, 0].get_cube_coordinates())

    def _set_cubes_relevance_status(self, cubes, pixel_count, c_stars, final_percent):
        """Determine which CIELAB cubes are deemed to be relevant, and change their
        status to reflect this."""

        # Primary relevance variables
        threshold_pixel_count = pixel_count * self._threshold  # Minimum number of pixels to be in a cube

        # Secondary relevance variables
        c_star_image_percentile_value = np.percentile(c_stars, self._c_star_percentile)
        # print(c_star_image_percentile_value)  # k-th percentile of C* for entire image
        secondary_threshold_pixel_count = pixel_count * self._secondary_threshold  # Secondary minimum number of pixels
        print("Secondary pixel count threshold:", secondary_threshold_pixel_count)

        # Dimensions of matrix of cubes
        l_star_dim = cubes.shape[0]
        a_star_dim = cubes.shape[1]
        b_star_dim = cubes.shape[2]
        # print(l_star_dim, a_star_dim, b_star_dim)

        tot_pixels = 0

        # Getting progress bar increments
        increment_percent = self._get_increment_percent(final_percent, l_star_dim)
        update_progress = 0

        for i in range(l_star_dim):
            for j in range(a_star_dim):
                for k in range(b_star_dim):
                    cube = cubes[i, j, k]

                    # Step 4: Get cube pixel count
                    num_pixels = len(cube.pixels)
                    tot_pixels = tot_pixels + num_pixels  # Updating current pixel count

                    # Step 5: Calculate mean pixel colour (cube colour)
                    cube.calculate_mean_colour()

                    # Step 6-11: Determining if cube is relevant
                    if num_pixels > threshold_pixel_count:  # possibly >= (pseudo-code in paper uses >)
                        print("Cube meets primary requirements with:", num_pixels, "pixels")
                        cube.relevant = True

                    elif num_pixels == 0:  # No pixels in cube
                        cube.relevant = False

                    else:  # Secondary relevance checks

                        # At least 3/8% of pixels in cube have L* > 80
                        # or At least 3/8% of pixels in cube have C* above 50th percentile OF THE IMAGE

                        # Get number of pixels in cube that meet the secondary C* requirements
                        c_stars = cube.c_stars
                        c_star_cube_count = np.count_nonzero(c_stars > c_star_image_percentile_value)

                        # Get the number of pixels in cube that meet the secondary L* requirements
                        l_stars = cube.l_stars
                        l_star_cube_count = np.count_nonzero(l_stars > self._min_l_star)

                        # print(secondary_threshold_pixel_count, c_star_cube_count, l_star_cube_count)

                        # Check if cube meets secondary relevancy requirements
                        if c_star_cube_count > secondary_threshold_pixel_count:
                            cube.relevant = True
                            print("Cube below meets secondary requirements for C*...")
                            print("----C* cube count:", c_star_cube_count,
                                  "; L* cube count:", l_star_cube_count,
                                  "; Threshold pixel count:", threshold_pixel_count,
                                  "; Secondary threshold pixel count", secondary_threshold_pixel_count,
                                  "; Number of pixels:", num_pixels)

                        elif l_star_cube_count > secondary_threshold_pixel_count:
                            cube.relevant = True
                            print("Cube below meets secondary requirements for L*...")
                            print("----C* cube count:", c_star_cube_count,
                                  "; L* cube count:", l_star_cube_count,
                                  "; Threshold pixel count:", threshold_pixel_count,
                                  "; Secondary threshold pixel count", secondary_threshold_pixel_count,
                                  "; Number of pixels:", num_pixels)

                        else:
                            cube.relevant = False

                        # mean_l_star = cube.mean_colour[0]
                        # mean_c_star = cube.calculate_mean_c_star()
                        # c_star_50_percentile = cube.get_c_star_percentile(percentile=self._c_star_percentile)
                        #
                        # if (mean_l_star > 80 or mean_c_star > c_star_50_percentile) and (
                        #         (threshold_pixel_count / 8) <= pixel_count < threshold_pixel_count):
                        #     cube.relevant = True

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
            print("Dimensions don't match")
            # TODO: throw exception here

    def _get_relevant_cubes(self, cubes, final_percent):
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

        if num_relevant_cubes != 0:
            return relevant_cubes
        else:
            return np.array([])

    def _update_pixel_colours(self, lab, cubes, cube_assignments, relevant_cubes, final_percent):

        # Get array of relevant_cube mean colours
        relevant_cubes_mean_colours = []
        for cube in relevant_cubes:
            relevant_cubes_mean_colours.append(cube.mean_colour)
        relevant_cubes_mean_colours = np.array(relevant_cubes_mean_colours)

        # Cython Implementation
        # start_time = time.time()
        # Get array of relevant_cube coordinates
        # relevant_cube_coordinates = []
        # for cube in relevant_cubes:
        #     relevant_cube_coordinates.append(cube.coordinates)
        # relevant_cube_coordinates = np.array(relevant_cube_coordinates)

        # nieves2020cython.update_pixel_colours(lab,
        #                                       cube_assignments,
        #                                       relevant_cubes,
        #                                       relevant_cube_coordinates,
        #                                       relevant_cubes_mean_colours,
        #                                       cubes)
        # print("--- %s seconds for Cython pixel colour update loop ---" % (time.time() - start_time))

        # # Python Implementation
        start_time = time.time()
        rows = lab.shape[0]
        cols = lab.shape[1]

        # Getting progress bar increments
        increment_percent = self._get_increment_percent(final_percent, rows)
        update_progress = 0

        print("Updating pixel colours...")
        for i in range(rows):  # For each row of image
            for j in range(cols):  # For each column of image
                pixel_coordinates = cube_assignments[i, j]
                pixel_relevant = False

                # Alternative approach, check if pixel is in the relevant cube by finding the
                # cube it was assigned and checking if it is a relevant cube
                cube = cubes[pixel_coordinates[0], pixel_coordinates[1], pixel_coordinates[2]]

                if cube.relevant:
                    lab[i, j] = cube.mean_colour  # Assign cube's mean colour
                    cube.increment_pixel_count_after_reassignment()  # Increase count of pixels with this colour by one
                    # pixel_relevant = True
                else:
                    # Calculate closest relevant cube and use the mean colour for the pixel

                    # start_time = time.time()
                    pixel = np.full((relevant_cubes_mean_colours.shape[0], lab.shape[2]), lab[i, j])
                    euclidean_distances = np.linalg.norm(pixel - relevant_cubes_mean_colours, axis=1)
                    # min_distance = np.min(euclidean_distances)
                    min_distance_index = np.argmin(euclidean_distances)
                    # print("--- %s seconds for new Python pixel colour update loop ---" % (time.time() - start_time))

                    # start_time = time.time()
                    # pixel = lab[i, j]
                    # euclidean_distances = []
                    # for relevant_cube in relevant_cubes:
                    #     euclidean_distance = np.linalg.norm(pixel - relevant_cube.mean_colour)  # TODO: vectorise this!
                    #     euclidean_distances.append(euclidean_distance)
                    #
                    #     # TODO: What happens if there is a tie?
                    #
                    # # print(min(euclidean_distances))
                    # min_distance = min(euclidean_distances)
                    # min_distance_index = euclidean_distances.index(min_distance)
                    # print("--- %s seconds for old Python pixel colour update loop ---" % (time.time() - start_time))

                    # Updating pixel's colour with the closest colour
                    # new_pixel_colour = relevant_cubes[min_distance_index].mean_colour
                    new_pixel_colour = relevant_cubes_mean_colours[min_distance_index]
                    lab[i, j] = new_pixel_colour
                    relevant_cubes[min_distance_index] \
                        .increment_pixel_count_after_reassignment()  # Increase count of pixels with this colour by one

                # for relevant_cube in relevant_cubes:

                # if np.array_equal(pixel_coordinates, relevant_cube.coordinates):
                #     lab[i, j] = relevant_cube.mean_colour.copy()
                #     pixel_relevant = True
                #     break

                # if not pixel_relevant:
            #             # Calculate closest relevant cube and use the mean colour for the pixel
            #
            #             pixel = lab[i, j]
            #             euclidean_distances = []
            #
            #             for relevant_cube in relevant_cubes:
            #
            #                 euclidean_distance = np.linalg.norm(pixel - relevant_cube.mean_colour)
            #                 euclidean_distances.append(euclidean_distance)
            #
            #                 # TODO: What happens if there is a tie?
            #
            #             min_distance = min(euclidean_distances)
            #             min_distance_index = euclidean_distances.index(min_distance)
            #
            #             # Updating pixel's colour with the closest colour
            #             new_pixel_colour = relevant_cubes[min_distance_index].mean_colour.copy()
            #             lab[i, j] = new_pixel_colour

            # get the pixels cube
            # Is the cube a relevant colour - replace!
            # If not, find the nearest relevant colour and use that
            # TODO: this technically might not be the nearest colour...

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

        print("--- %s seconds for Python pixel colour update loop ---" % (time.time() - start_time))


# (r, g, b) = lab[0, 0]
# print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))


class Nieves2020OffsetCubes(Nieves2020):
    name = "Nieves, Gomez-Robledo, Chen and Romero (2020) - Cube corners at CIELAB origin"
    url = "https://doi.org/10.1364/AO.378659"

    def __init__(self):
        """Constructor."""
        super().__init__(Nieves2020OffsetCubes.name, Nieves2020OffsetCubes.url)

    def _get_cube_assignments(self, lab):
        # Calculating how many cubes to generate
        return (np.floor_divide(lab, self._cube_size)).astype(int)  # Cube coordinates for each pixel

    def _divide_cielab_space(self, lab, final_percent):
        """Generate the required CIELAB cubes for the given image
        and return the coordinates of the cube that each pixel is to be assigned to."""

        # Calculating how many cubes to generate
        cube_assignments = self._get_cube_assignments(lab)  # Cube coordinates for each pixel

        # Check extent of cube generation
        l_star_max = cube_assignments[:, :, 0].max()
        l_star_min = 0  # l_star_min is always 0
        a_star_max = cube_assignments[:, :, 1].max()
        a_star_min = cube_assignments[:, :, 1].min()
        b_star_max = cube_assignments[:, :, 2].max()
        b_star_min = cube_assignments[:, :, 2].min()

        # print("l* range: " + str(l_star_min) + "," + str(l_star_max))
        # print("a* range: " + str(a_star_min) + "," + str(a_star_max))
        # print("b* range: " + str(b_star_min) + "," + str(b_star_max))

        # Maxing sure ranges are valid and always include 0 in the range
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

        # Getting progress bar increments
        increment_percent = self._get_increment_percent(final_percent, l_star_range)
        update_progress = 0

        # Generating required cubes and adding them to the 3D array of cubes
        cubes = np.empty([l_star_range, a_star_range, b_star_range], dtype=cielabcube.CielabCube)
        for l_star in range(l_star_min, l_star_max + 1):
            for a_star in range(a_star_min, a_star_max + 1):
                for b_star in range(b_star_min, b_star_max + 1):
                    # Generate new cube
                    # print(l_star, a_star, b_star)
                    cubes[l_star, a_star, b_star] = cielabcube.CielabCube(l_star, a_star, b_star)
                    # This approach works as negative l_Star will be assigned to the far right of the cube and work back
                    # TODO: Optimisation section - talk about how storing cubes in a np.array is faster to find
                    #   them again, rather than in a list that must be iterated through each time

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

        print(cubes.size, "CIELAB cubes generated...")
        return cubes, cube_assignments


class Nieves2020CentredCubes(Nieves2020):
    name = "Nieves, Gomez-Robledo, Chen and Romero (2020) - Cube centred on CIELAB origin"
    url = "https://doi.org/10.1364/AO.378659"

    def __init__(self):
        """Constructor."""
        super().__init__(Nieves2020CentredCubes.name, Nieves2020CentredCubes.url)

    def _get_cube_assignments(self, lab):
        # Calculating how many cubes to generate
        #   - temporarily round each pixel LAB value to the nearest multiple of 20
        #   - divide all of these values by 20 to get the cube assignment
        cube_assignments = self._cube_size * np.round(lab / self._cube_size)
        cube_assignments = (cube_assignments / self._cube_size).astype(int)
        return cube_assignments  # Cube coordinates for each pixel

    def _divide_cielab_space(self, lab, final_percent):
        """Generate the required CIELAB cubes for the given image
        and return the coordinates of the cube that each pixel is to be assigned to."""

        # Calculating how many cubes to generate
        cube_assignments = self._get_cube_assignments(lab)

        l_star_max = cube_assignments[:, :, 0].max()
        # l_star_min = cube_assignments[:, :, 0].min()
        l_star_min = 0  # l_star_min is always 0
        a_star_max = cube_assignments[:, :, 1].max()
        a_star_min = cube_assignments[:, :, 1].min()
        b_star_max = cube_assignments[:, :, 2].max()
        b_star_min = cube_assignments[:, :, 2].min()

        # print("l* range: " + str(l_star_min) + "," + str(l_star_max))
        # print("a* range: " + str(a_star_min) + "," + str(a_star_max))
        # print("b* range: " + str(b_star_min) + "," + str(b_star_max))

        # Maxing sure ranges are valid and always include 0 in the range
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

        # Getting progress bar increments
        increment_percent = self._get_increment_percent(final_percent, l_star_range)
        update_progress = 0

        # Generating required cubes and adding them to the 3D array of cubes
        cubes = np.empty([l_star_range, a_star_range, b_star_range], dtype=cielabcube.CielabCube)
        for l_star in range(l_star_min, l_star_max + 1):
            for a_star in range(a_star_min, a_star_max + 1):
                for b_star in range(b_star_min, b_star_max + 1):
                    # Generate new cube
                    # print(l_star, a_star, b_star)
                    cubes[l_star, a_star, b_star] = cielabcube.CielabCube(l_star, a_star, b_star)
                    # This approach works as negative l_Star will be assigned to the far right of the cube and work back
                    # TODO: Optimisation section - talk about how storing cubes in a np.array is faster to find
                    #   them again, rather than in a list that must be iterated through each time

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

        print(cubes.size, "CIELAB cubes generated...")
        return cubes, cube_assignments


def convert_rgb_2_lab(image):
    """Convert an sRBG image into the CIELAB colour space."""
    if image.shape[2] == 4:
        image = color.rgba2rgb(image)  # Removing alpha channel if present

    return color.rgb2lab(image, illuminant="D65")


def convert_lab_2_rgb(image):
    """Convert an image in the CIELAB colour space into the sRGB colour space."""
    new_image = color.lab2rgb(image, illuminant="D65")
    new_image = img_as_ubyte(new_image)  # Scaling to 8-bits per channel

    return new_image


def get_c_stars(lab):
    """Return the matrix of C* (chroma) values for each pixel in the image."""
    lab_squared = np.square(lab)  # Square each element of CIELAB image
    a_star_squared = lab_squared[:, :, 1]
    b_star_squared = lab_squared[:, :, 2]
    c_stars = np.sqrt(a_star_squared + b_star_squared)  # C* = sqrt(a*^2 + b*^2)
    return c_stars

    # TODO: mention the limit of L can be greater than 100 - Linhares
