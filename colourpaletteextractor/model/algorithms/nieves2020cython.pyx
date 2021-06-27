#cython: language_level=3

from colourpaletteextractor.model.algorithms import cielabcube

def divide_cielab_space(double [:, :, :] image, long [:, :, :] cube_assignments):

    # Set the variable extension types
    cdef int i, j, cols, rows
    cdef double [:] pixel
    cdef long [:] pixel_coordinates

    # Grab the image dimensions
    rows = image.shape[0]
    cols = image.shape[1]

    # Loop over the image
    for i in range(rows):  # For each row of image
        for j in range(cols):  # For each column of image
            pixel = image[i, j]
            # print(pixel.shape)
            pixel_coordinates = cube_assignments[i, j]
            test = cielabcube.CielabCube(1, 2, 3)

            # pixel_coordinates = np.ndarray.tolist(pixel_coordinates)
            # cube = self._get_cielab_cube(pixel_coordinates)
            # print(cube)
            # cube.add_pixel_to_cube(pixel)

    # Return the image



