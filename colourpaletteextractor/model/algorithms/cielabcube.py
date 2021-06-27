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