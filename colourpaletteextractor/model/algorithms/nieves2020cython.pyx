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


#cython: language_level=3
# cython: boundscheck=False

import numpy as np
cimport numpy as np

from colourpaletteextractor.model.algorithms import cielabcube

# np.import_array()



def divide_cielab_space(double [:, :, :] image, long [:, :, :] cube_assignments, object cubes):

    # Set the variable extension types
    cdef int i, j, cols, rows
    cdef double [:] pixel
    cdef long [:] pixel_coordinates

    # Get the image dimensions
    rows = image.shape[0]
    cols = image.shape[1]

    # Loop over the image
    for i in range(rows):  # For each row of image
        for j in range(cols):  # For each column of image
            pixel = image[i, j]
            pixel_coordinates = cube_assignments[i, j]
            cube = cubes[pixel_coordinates[0], pixel_coordinates[1], pixel_coordinates[2]]
            cube.add_pixel_to_cube(pixel)


def get_cielab_cube(object cubes, long[:] pixel_coordinates):
    """Return the cube with the same simplified coordinates as the given pixel."""
    cdef bint cube_found = False
    cdef long[:] cube_coordinates


    for cube in cubes:
        cube_coordinates = cube.coordinates
        # print(pixel_coordinates.type)
        if pixel_coordinates[0] == cube_coordinates[0]:
        # if pixel_coordinates == cube_coordinates:
            cube_found = True
            return cube

    # print("Cube not found for pixel with coordinates: ", pixel_coordinates)
    # TODO: add checks to make sure that the coordinates are valid for a cube

def update_pixel_colours(double [:, :, :] lab,
                         long[:, :, :] cube_assignments,
                         object relevant_cubes,
                         long[:, :] relevant_coordinates,
                         double[:, :] relevant_cubes_mean_colours,
                         object cubes):

    cdef long [:] pixel_coordinates
    cdef bint pixel_relevant = False
    cdef object cube
    cdef double[:] pixel, euclidean_distance

    cdef double[:] mean_colour
    cdef list euclidean_distances = []



    cdef Py_ssize_t i, j, k, rows, cols, num_colours, num_channels
    rows = lab.shape[0]
    cols = lab.shape[1]

    for i in range(rows):
        for j in range(cols):
            pixel_coordinates = cube_assignments[i, j]
            pixel_relevant = False

            cube = cubes[pixel_coordinates[0], pixel_coordinates[1], pixel_coordinates[2]]

            if cube.relevant:
                mean_colour = cube.mean_colour
                lab[i, j, 0] = mean_colour[0]
                lab[i, j, 1] = mean_colour[1]
                lab[i, j, 2] = mean_colour[2]

                pixel_relevant = True

            else:
                # Calculate closest relevant cube and use the mean colour for the pixel
                pixel = lab[i, j]
                euclidean_distances = []

                num_colours = relevant_cubes_mean_colours.shape[0]
                num_channels = relevant_cubes_mean_colours.shape[1]

                for k in range(num_colours):
                    # for l in range(num_channels):

                        # euclidean_distance[l] = np.linalg.norm(pixel[l] - relevant_cubes_mean_colours[k, l])
                    euclidean_distance = np.linalg.norm(np.asarray(pixel) - np.asarray(relevant_cubes_mean_colours[k]))
                    euclidean_distances.append(euclidean_distance)

                    # TODO: What happens if there is a tie?

                min_distance = min(euclidean_distances)
                min_distance_index = euclidean_distances.index(min_distance)

                # Updating pixel's colour with the closest colour
                new_pixel_colour = relevant_cubes[min_distance_index].mean_colour

                lab[i, j, 0] = new_pixel_colour[0]
                lab[i, j, 1] = new_pixel_colour[1]
                lab[i, j, 2] = new_pixel_colour[2]
