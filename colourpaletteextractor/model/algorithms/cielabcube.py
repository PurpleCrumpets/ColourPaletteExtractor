import numpy as np


def get_cielab_cube(cubes, pixel_coordinates):
    """Return the cube with the same simplified coordinates as the given pixel."""
    # pixel_coordinates = np.ndarray.tolist(pixel_coordinates)
    cube_found = False
    for cube in cubes:
        cube_coordinates = cube.get_cube_coordinates()
        # print(pixel_coordinates.type)
        if pixel_coordinates[0] == cube_coordinates[0]:
        # if pixel_coordinates == cube_coordinates:
            cube_found = True
            return cube
        # print(pixel_coordinates)
        # print(cube_coordinates)
        # print(cube_coordinates.type)
    print("Cube not found for pixel with coordinates: ", pixel_coordinates)


class CielabCube:

    def __init__(self, l_star_coord, a_star_coord, b_star_coord):
        self._l_star_coord = l_star_coord
        self._a_star_coord = a_star_coord
        self._b_star_coord = b_star_coord

        self._coordinates = np.array([self._l_star_coord, self._a_star_coord, self._b_star_coord])

        self._pixels = []
        self._mean_colour = np.empty([3])
        self._c_stars = []

        self._relevant = False

    @property
    def pixels(self):
        """Returns the list of pixels in the cube."""
        return self._pixels

    @property
    def coordinates(self):
        return self._coordinates

    @property
    def mean_colour(self):
        return self._mean_colour

    def calculate_mean_colour(self):
        pixel_array = np.array(self._pixels)
        # print(pixel_array)
        # TODO: Add checks
        if pixel_array.size != 0:
            # return pixel_array.mean(axis=0)
            self._mean_colour = pixel_array.mean(axis=0)
            # print("Mean colour: ", self._mean_colour)

    @property
    def relevant(self):
        return self._relevant

    @relevant.setter
    def relevant(self, value):
        self._relevant = value
        # TODO: Add check to make sure boolean


    @property
    def c_stars(self):
        return self._c_stars

    def calculate_mean_c_star(self):
        c_stars_array = np.array(self._c_stars)

        if c_stars_array.size != 0:
            return c_stars_array.mean()
        # TODO: add checks





    def get_c_star_percentile(self, percentile):
        c_stars_array = np.array(self._c_stars)

        if c_stars_array.size != 0:
            return np.percentile(c_stars_array, 50)
        else:
            return 0




    def get_cube_coordinates(self):
        return [self._l_star_coord, self._a_star_coord, self._b_star_coord]

    def add_pixel_to_cube(self, pixel, c_star):
        """Assign pixel to the cube"""
        self._pixels.append(pixel)
        self._c_stars.append(c_star)
        # TODO: possbly convert to numpy array and append that way to save converting it later?
    # Alternatively, create a new 2d matrix and give each pixel a number corresponding to the given cube
    # Therefore, you would not need to create a bunch of object?


