# import pyximport; pyximport.install()
import numpy as np
from skimage import color
from skimage import img_as_ubyte
import time

from colourpaletteextractor.model.algorithms import cielabcube, palettealgorithm
from colourpaletteextractor.model.algorithms import nieves2020cython


class Nieves2020(palettealgorithm.PaletteAlgorithm):
    COLOUR_CHANNELS = 3

    # TODO: Add cube size as variable in constructor
    # TODO: Add cube size check (ie make sure it divides into the CIELAB volume ok)

    def __init__(self):
        """Constructor."""
        super().__init__()
        self._cube_size = 20
        self._cubes = np.empty([0, 0, 0], dtype=cielabcube.CielabCube)
        self._threshold = 0.03

    def generate_colour_palette(self, image):
        print("Generating colour palette...")

        # Remove alpha channel in case it has not already been removed

        # Step 1: Compute L*, a*, b* and C* of each pixel (under D65 illuminant)
        lab = self._convert_rgb_2_lab(image)
        c_stars = self._get_c_stars(lab)
        pixel_count = lab.size / Nieves2020.COLOUR_CHANNELS

        # (r, g, b) = lab[0, 0]
        # print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))

        # Step 2: Divide CIELAB colour space into cubes
        cube_assignments = self._divide_cielab_space(lab)

        # Steps 3-12: Determine if cube colour is relevant
        self._assign_pixels_to_cube(lab, cube_assignments, c_stars)
        self._set_cubes_relevance_status(pixel_count)

        # Step 13: Obtain relevant colours
        relevant_cubes = self._get_relevant_cubes()
        print("Number of relevant colours:", len(relevant_cubes))

        # Step 14-19: Segmenting image in terms of relevant colours
        # old_lab = lab.copy()
        self._update_pixel_colours(lab, cube_assignments, relevant_cubes)

        # if np.array_equal(old_lab, lab):
        #     print("Nothing has changed")
        # else:
        #     print("Something as changed!")

        # Convert image back into rgb
        recoloured_image = self._convert_lab_2_rgb(lab)

        # Get colour palette as a list of rgb colours
        colour_palette = []
        for cube in relevant_cubes:
            print("Old colour: ", cube.mean_colour)
            colour = self._convert_lab_2_rgb(cube.mean_colour)  # Scale to 8-bit
            print("New colour: ", colour)
            colour_palette.append(colour)

        return recoloured_image, colour_palette




    @staticmethod
    def _convert_rgb_2_lab(image):
        """Convert an RBG image into the CIELAB colour space."""
        if image.shape[2] == 4:
            image = color.rgba2rgb(image)

            # TODO: set observer??

        return color.rgb2lab(image, illuminant="D65")

    @staticmethod
    def _convert_lab_2_rgb(image):
        """Convert an CIELAB image into the RGB colour space."""
        new_image = color.lab2rgb(image, illuminant="D65")

        # Scaling to 8-bit
        new_image = img_as_ubyte(new_image)

        return new_image

    @staticmethod
    def _get_c_stars(lab):
        """Return the matrix of C* (chroma) values for each pixel in the image."""
        lab_squared = np.square(lab)
        a_squared = lab_squared[:, :, 1]
        b_squared = lab_squared[:, :, 2]
        c_stars = np.sqrt(a_squared + b_squared)
        # print(c_stars.shape)
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
                    # TODO: Optimisation section - talk about how storing cubes in a np.array is faster to find
                    #   them again, rather than in a list that must be iterated through each time

        return cube_assignments

    def _assign_pixels_to_cube(self, lab, cube_assignments, c_stars):

        # Using Cython
        # start_time = time.time()
        # nieves2020cython.divide_cielab_space(lab, cube_assignments, self._cubes)
        # print("--- %s seconds for Cython ---" % (time.time() - start_time))
        # print(len(self._cubes[0, 0, 0].pixels))

        # Using Python
        start_time = time.time()
        rows = lab.shape[0]
        cols = lab.shape[1]

        print("Starting cube assignment loop...")
        for i in range(rows):  # For each row of image
            for j in range(cols):  # For each column of image
                pixel = lab[i, j]
                c_star = c_stars[i, j]
                pixel_coordinates = cube_assignments[i, j]
                cube = self._cubes[pixel_coordinates[0], pixel_coordinates[1], pixel_coordinates[2]]
                # cube = cielabcube.get_cielab_cube(self._cubes, pixel_coordinates)
                cube.add_pixel_to_cube(pixel, c_star)

        print("--- %s seconds for Python cube assignment loop ---" % (time.time() - start_time))

        # print(len(self._cubes[0, 0, 0].pixels))
        # print(self._cubes[0, 0, 0].get_cube_coordinates())

        # Need to divide each pixel tuple by the size of each cube, removing the remainder
        # This will give the 3d coordinates to find the cube associated with a given pixel
        # print(np.floor_divide(-7, 3))

        # pixel_to_cube_map = np.zeros((rows, cols))
        # print(pixel_to_cube_map.shape)

        # Number of cubes
        # start with the centre point and work outwards from there

    def _set_cubes_relevance_status(self, pixel_count):

        threshold_pixel_count = pixel_count * self._threshold
        # print(threshold_pixel_count)

        # print(self._cubes.shape)
        l_star_dim = self._cubes.shape[0]
        a_star_dim = self._cubes.shape[1]
        b_star_dim = self._cubes.shape[2]

        # print(l_star_dim, a_star_dim, b_star_dim)

        tot_pixels = 0

        for i in range(l_star_dim):
            for j in range(a_star_dim):
                for k in range(b_star_dim):
                    cube = self._cubes[i, j, k]

                    # Step 4: Get cube pixel count
                    num_pixels = len(cube.pixels)
                    tot_pixels = tot_pixels + num_pixels

                    # Step 5: Calculate mean pixel colour
                    cube.calculate_mean_colour()

                    # Step 6-11: Determining if cube is relevant
                    if num_pixels > threshold_pixel_count: # possibly >= (pseudo-code in paper uses >)
                        cube.relevant = True
                    elif num_pixels == 0:
                        cube.relevant = False
                    else:

                        mean_l_star = cube.mean_colour[0]
                        mean_c_star = cube.calculate_mean_c_star()
                        c_star_50_percentile = cube.get_c_star_percentile(50)

                        if (mean_l_star > 80 or mean_c_star > c_star_50_percentile) and (
                                (threshold_pixel_count / 8) <= pixel_count < threshold_pixel_count):
                            cube.relevant = True

        if tot_pixels != pixel_count:
            print("Dimensions don't match")
            # TODO: throw exception here

    def _get_relevant_cubes(self):
        relevant_cubes = []
        num_relevant_cubes = 0

        l_star_dim = self._cubes.shape[0]
        a_star_dim = self._cubes.shape[1]
        b_star_dim = self._cubes.shape[2]

        for i in range(l_star_dim):
            for j in range(a_star_dim):
                for k in range(b_star_dim):
                    cube = self._cubes[i, j, k]

                    if cube.relevant:
                        relevant_cubes.append(cube)
                        num_relevant_cubes += 1

        if num_relevant_cubes != 0:
            return relevant_cubes
        else:
            return np.array([])

    def _update_pixel_colours(self, lab, cube_assignments, relevant_cubes):

        start_time = time.time()
        rows = lab.shape[0]
        cols = lab.shape[1]

        print("Updating pixel colours...")
        for i in range(rows):  # For each row of image
            for j in range(cols):  # For each column of image
                pixel_coordinates = cube_assignments[i, j]

                pixel_relevant = False
                for relevant_cube in relevant_cubes:

                    if np.array_equal(pixel_coordinates, relevant_cube.coordinates):
                        lab[i, j] = relevant_cube.mean_colour.copy()
                        pixel_relevant = True
                        break

                if not pixel_relevant:
                    # Calculate closest relevant cube and use the mean colour for the pixel

                    pixel = lab[i, j]
                    euclidean_distances = []

                    for relevant_cube in relevant_cubes:

                        euclidean_distance = np.linalg.norm(pixel - relevant_cube.mean_colour)
                        euclidean_distances.append(euclidean_distance)

                        # TODO: What happens if there is a tie?

                    min_distance = min(euclidean_distances)
                    min_distance_index = euclidean_distances.index(min_distance)

                    # Updating pixel's colour with the closest colour
                    new_pixel_colour = relevant_cubes[min_distance_index].mean_colour.copy()
                    lab[i, j] = new_pixel_colour

                # get the pixels cube
                # Is the cube a relevant colour - replace!
                # If not, find the nearest relevant colour and use that
                # TODO: this technically might not be the nearest colour...


        print("--- %s seconds for Python pixel colour update loop ---" % (time.time() - start_time))
