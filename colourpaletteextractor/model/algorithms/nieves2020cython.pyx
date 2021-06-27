#cython: language_level=3

from colourpaletteextractor.model.algorithms import cielabcube


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


