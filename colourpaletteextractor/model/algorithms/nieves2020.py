# import pyximport; pyximport.install()
import numpy as np
from skimage import color
import time

from colourpaletteextractor.model.algorithms import cielabcube, palettealgorithm
from colourpaletteextractor.model.algorithms import nieves2020cython



class Nieves2020(palettealgorithm.PaletteAlgorithm):

    # CUBE_SIZE = 20
    # SPLITS_PER_DIMENSION = 5
    # L_MAX = 100
    # L_MIN = 0
    # A_MAX = 127
    # A_MIN = -128
    # B_MAX = 127
    # B_MIN = -128

    # TODO: Add cube size as variable in constructor
    # TODO: Add cube size check (ie make sure it divides into the CIELAB volume ok)

    def __init__(self):
        """Constructor."""
        super().__init__()
        self._cube_size = 20
        self._cubes = []

    def generate_colour_palette(self, image):
        print("Generating colour palette")

        # Remove alpha channel in case it has not already been removed

        # Step 1: Compute L*, a*, b* and C* of each pixel (under D65 illuminant)
        lab = self._convert_rgb_2_lab(image)
        c_star = self._get_c_star(lab)

        # (r, g, b) = lab[0, 0]
        # print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))

        # Step 2
        cube_assignments = self._divide_cielab_space(lab)

        # Step 3
        # start_time = time.time()
        self._assign_pixels_to_cube(lab, cube_assignments)
        # print("--- %s seconds for Step 3 ---" % (time.time() - start_time))

    @staticmethod
    def _convert_rgb_2_lab(image):
        """Convert an RBG image into the CIELAB colour space."""
        if image.shape[2] == 4:
            image = color.rgba2rgb(image)
        print(image.shape)
        return color.rgb2lab(image, illuminant="D65")

    def _get_c_star(self, lab):
        """Return the matrix of C* (chroma) values for each pixel in the image."""
        lab_squared = np.square(lab)
        a_squared = lab_squared[:, :, 1]
        b_squared = lab_squared[:, :, 2]
        c_stars = np.sqrt(a_squared + b_squared)
        return c_stars

        # TODO: mention the limit of L can be greater than 100 - Linhares

    # @cython.boundscheck(False)
    # cpdef unsigned char[:, :] _divide_cielab_space_fast(unsigned char [:, :] lab):
    #     # Set the variable extension types
    #     cdef int x, y, w, h

    def _divide_cielab_space(self, lab):
        """Assign pixels to the a cube"""

        cube_assignments = (np.floor_divide(lab, self._cube_size)).astype(int)  # Cube coordinates for each pixel

        # Calculating how many cubes to generate
        max_l = cube_assignments[:, :, 0].max()
        min_l = cube_assignments[:, :, 0].min()

        max_a = cube_assignments[:, :, 1].max()
        min_a = cube_assignments[:, :, 1].min()

        max_b = cube_assignments[:, :, 2].max()
        min_b = cube_assignments[:, :, 2].min()

        # print("l: " + str(max_l) + "," + str(min_l))
        # print("a: " + str(max_a) + "," + str(min_a))
        # print("b: " + str(max_b) + "," + str(min_b))

        # Generating required cubes
        for l_star in range(min_l, max_l + 1):
            for a_star in range(min_a, max_a + 1):
                for b_star in range(min_b, max_b + 1):
                    coords = [l_star, a_star, b_star]
                    # Generate new cube
                    self._cubes.append(cielabcube.CielabCube(l_star, a_star, b_star))
                    # print(coords)

        return cube_assignments

    def _assign_pixels_to_cube(self, lab, cube_assignments):

        start_time = time.time()
        # print(nieves2020cython.function(1, 2))

        nieves2020cython.divide_cielab_space(lab, cube_assignments)
        print("--- %s seconds for Cython ---" % (time.time() - start_time))

        rows = lab.shape[0]
        cols = lab.shape[1]

        for i in range(rows):  # For each row of image
            for j in range(cols):  # For each column of image
                pixel = lab[i, j]
                # print(pixel.shape)
                # pixel_coordinates = cube_assignments[i, j]
                # pixel_coordinates = np.ndarray.tolist(pixel_coordinates)
                # cube = self._get_cielab_cube(pixel_coordinates)
                # print(cube)
                # cube.add_pixel_to_cube(pixel)

                #
                # print(cube_assignment)
                # print(pixel)

        # Need to divide each pixel tuple by the size of each cube, removing the remainder
        # This will give the 3d coordinates to find the cube associated with a given pixel
        # print(np.floor_divide(-7, 3))

        # pixel_to_cube_map = np.zeros((rows, cols))
        # print(pixel_to_cube_map.shape)

        # Number of cubes
        # start with the centre point and work outwards from there

    def _get_cielab_cube(self, pixel_coordinates):
        """Return the cube with the same simplified coordinates as the given pixel."""
        cube_found = False
        for cube in self._cubes:
            cube_coordinates = cube.get_cube_coordinates()
            # print(pixel_coordinates.type)
            if pixel_coordinates == cube_coordinates:
                cube_found = True
                return cube
            # print(pixel_coordinates)
            # print(cube_coordinates)
            # print(cube_coordinates.type)
        print("Cube not found for pixel with coordinates: ", pixel_coordinates)
