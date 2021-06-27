# import pyximport; pyximport.install()
import numpy as np
from skimage import color
import time

from colourpaletteextractor.model.algorithms import cielabcube, palettealgorithm
from colourpaletteextractor.model.algorithms import nieves2020cython


class Nieves2020(palettealgorithm.PaletteAlgorithm):

    # TODO: Add cube size as variable in constructor
    # TODO: Add cube size check (ie make sure it divides into the CIELAB volume ok)

    def __init__(self):
        """Constructor."""
        super().__init__()
        self._cube_size = 20
        self._cubes = np.empty([0, 0, 0], dtype=cielabcube.CielabCube)

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

        return color.rgb2lab(image, illuminant="D65")

    def _get_c_star(self, lab):
        """Return the matrix of C* (chroma) values for each pixel in the image."""
        lab_squared = np.square(lab)
        a_squared = lab_squared[:, :, 1]
        b_squared = lab_squared[:, :, 2]
        c_stars = np.sqrt(a_squared + b_squared)
        return c_stars

        # TODO: mention the limit of L can be greater than 100 - Linhares

    def _divide_cielab_space(self, lab):
        """Assign pixels to the a cube"""

        # Calculating how many cubes to generate
        cube_assignments = (np.floor_divide(lab, self._cube_size)).astype(int)  # Cube coordinates for each pixel

        l_star_max = cube_assignments[:, :, 0].max()
        l_star_min = cube_assignments[:, :, 0].min()
        a_star_max = cube_assignments[:, :, 1].max()
        a_star_min = cube_assignments[:, :, 1].min()
        b_star_max = cube_assignments[:, :, 2].max()
        b_star_min = cube_assignments[:, :, 2].min()

        # print("l: " + str(l_star_max) + "," + str(l_star_min))
        # print("a: " + str(a_star_max) + "," + str(a_star_min))
        # print("b: " + str(b_star_max) + "," + str(b_star_min))

        l_star_range = l_star_max - l_star_min + 1
        a_star_range = a_star_max - a_star_min + 1
        b_star_range = b_star_max - b_star_min + 1

        # Generating required cubes
        self._cubes = np.empty([l_star_range, a_star_range, b_star_range], dtype=cielabcube.CielabCube)
        for l_star in range(l_star_min, l_star_max + 1):
            for a_star in range(a_star_min, a_star_max + 1):
                for b_star in range(b_star_min, b_star_max + 1):

                    # Generate new cube
                    self._cubes[l_star, a_star, b_star] = cielabcube.CielabCube(l_star, a_star, b_star)
                    # This approach works as negative l_Star will be assigned to the far right of the cube and work back

        return cube_assignments

    def _assign_pixels_to_cube(self, lab, cube_assignments):

        # Using Cython
        # start_time = time.time()
        # nieves2020cython.divide_cielab_space(lab, cube_assignments, self._cubes)
        # print("--- %s seconds for Cython ---" % (time.time() - start_time))
        # print(len(self._cubes[0, 0, 0].pixels))


        # Using Python
        start_time = time.time()
        rows = lab.shape[0]
        cols = lab.shape[1]

        print("Starting loop...")
        for i in range(rows):  # For each row of image
            for j in range(cols):  # For each column of image
                pixel = lab[i, j]
                pixel_coordinates = cube_assignments[i, j]
                cube = self._cubes[pixel_coordinates[0], pixel_coordinates[1], pixel_coordinates[2]]
                # cube = cielabcube.get_cielab_cube(self._cubes, pixel_coordinates)
                cube.add_pixel_to_cube(pixel)

        print("--- %s seconds for Python ---" % (time.time() - start_time))

        print(len(self._cubes[0, 0, 0].pixels))
        print(self._cubes[0, 0, 0].get_cube_coordinates())

        # Need to divide each pixel tuple by the size of each cube, removing the remainder
        # This will give the 3d coordinates to find the cube associated with a given pixel
        # print(np.floor_divide(-7, 3))

        # pixel_to_cube_map = np.zeros((rows, cols))
        # print(pixel_to_cube_map.shape)

        # Number of cubes
        # start with the centre point and work outwards from there
