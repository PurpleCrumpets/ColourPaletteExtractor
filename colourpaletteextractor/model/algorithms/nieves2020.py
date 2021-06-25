import numpy as np
from matplotlib import pyplot as plt
from skimage import color

from colourpaletteextractor.model.algorithms import palettealgorithm


class CielabCube:

    def __init__(self, l_star_coord, a_star_coord, b_star_coord):
        self._l_star_coord = l_star_coord
        self._a_star_coord = a_star_coord
        self._b_star_coord = b_star_coord

        self._pixels = []

    def get_cube_coordinates(self):
        return [self._l_star_coord, self._a_star_coord, self._b_star_coord]

    def add_pixel_to_cube(self, pixel):
        """Assign pixel to the cube"""
        self._pixels.append(pixel)
    # Alternatively, create a new 2d matrix and give each pixel a number corresponding to the given cube
    # Therefore, you would not need to create a bunch of object?


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

        # Step 1: Compute L*,
        lab = self._convert_rgb_2_lab(image)
        (r, g, b) = lab[0, 0]
        print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))

        # Step 2
        cube_assignments = self._divide_cielab_space(lab)

        # Step 3
        self._assign_pixels_to_cube(lab, cube_assignments)

    @staticmethod
    def _convert_rgb_2_lab(image):
        """Convert an RBG image into the CIELAB colour space."""
        if image.shape[2] == 4:
            image = color.rgba2rgb(image)
        print(image.shape)
        return color.rgb2lab(image, illuminant="D65")

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
        for l_star in range(min_l, max_l):
            for a_star in range(min_a, max_a):
                for b_star in range(min_b, max_b):
                    coords = [l_star, a_star, b_star]
                    # Generate new cube
                    self._cubes.append(CielabCube(l_star, a_star, b_star))
                    # print(coords)

        return cube_assignments

    def _assign_pixels_to_cube(self, lab, cube_assignments):
        rows = lab.shape[0]
        cols = lab.shape[1]

        for i in range(rows):  # For each row of image
            for j in range(cols):  # For each column of image
                pixel = lab[i, j]
                pixel_coordinates = cube_assignments[i, j]
                pixel_coordinates = np.ndarray.tolist(pixel_coordinates)
                cube = self._get_cielab_cube(pixel_coordinates)
                print(cube)
                cube.add_pixel_to_cube(pixel)


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



