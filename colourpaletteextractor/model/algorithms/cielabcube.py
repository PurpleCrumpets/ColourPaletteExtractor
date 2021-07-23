import numpy as np

class CielabCube:
    """A cube representing a fixed region in the CIELAB colour space.

    The cube is used to hold pixels in an image that exist within the cube's region of the CIELAB colour space. The
    input parameters do not refer to the actual L*, a* and b* values, but depend on the `CUBE_SIZE` specified by the
    colour palette algorithm (in particular, any variant on the `Nieves 2020`_ algorithm).

    Args:
        l_star_coord: Perceptual lightness cube coordinate
        a_star_coord: Green-red cube coordinate
        b_star_coord: Blue-yellow cube coordinate

    .. _Nieves 2020:
       https://doi.org/10.1364/AO.378659
    """

    def __init__(self, l_star_coord: int, a_star_coord: int, b_star_coord: int):

        self._l_star_coord = l_star_coord
        self._a_star_coord = a_star_coord
        self._b_star_coord = b_star_coord

        self._coordinates = np.array([self._l_star_coord, self._a_star_coord, self._b_star_coord])

        self._pixels = []

        self._pixel_count_after_reassignment = 0

        self._mean_colour = np.empty([3])
        self._c_stars = []

        self._relevant = False  # Cube is initially not considered to be a relevant colour

    @property
    def pixel_count_after_reassignment(self):
        return self._pixel_count_after_reassignment

    def increment_pixel_count_after_reassignment(self):
        self._pixel_count_after_reassignment += 1

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
    def l_stars(self):
        pixel_array = np.array(self._pixels)
        return pixel_array[:, 0]  # First column of each row representing a pixel


    @property
    def c_stars(self):
        return self._c_stars

    def calculate_mean_c_star(self):
        c_stars_array = np.array(self._c_stars)

        if c_stars_array.size != 0:
            return c_stars_array.mean()
        # TODO: add checks

    def get_l_star_percentile_value(self, percentile):
        pixel_array = np.array(self._pixels)
        l_stars_array = pixel_array[:, 0]  # First column of each row representing a pixel

        if l_stars_array.size != 0:
            return np.percentile(l_stars_array, percentile)
        else:
            return 0

    def get_c_star_percentile_value(self, percentile):
        c_stars_array = np.array(self._c_stars)

        if c_stars_array.size != 0:
            return np.percentile(c_stars_array, percentile)
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


def get_relative_frequencies(relevant_cubes: list[CielabCube], total_pixels: int) -> list[float]:
    """Calculate the relative frequency of

    Args:
        relevant_cubes:
        total_pixels:

    Returns:

    """

    frequencies = []
    for cube in relevant_cubes:
        frequency = cube.pixel_count_after_reassignment / total_pixels
        frequencies.append(frequency)

    return frequencies


def get_cielab_cube(cubes, pixel_coordinates):
    """Return the cube with the same simplified coordinates as the given pixel.

    Args:
        cubes:
        pixel_coordinates:

    Returns:

    """

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


