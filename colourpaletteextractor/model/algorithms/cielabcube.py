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

    @property
    def pixels(self):
        """Returns the list of pixels in the cube."""
        return self._pixels

    @property
    def coordinates(self):
        return self._coordinates

    def get_cube_coordinates(self):
        return [self._l_star_coord, self._a_star_coord, self._b_star_coord]

    def add_pixel_to_cube(self, pixel):
        """Assign pixel to the cube"""
        self._pixels.append(pixel)
    # Alternatively, create a new 2d matrix and give each pixel a number corresponding to the given cube
    # Therefore, you would not need to create a bunch of object?
