from skimage import color

from colourpaletteextractor.model.algorithms import palettealgorithm


class Nieves2020(palettealgorithm.PaletteAlgorithm):

    CUBE_SIZE = 20
    SPLITS_PER_DIMENSION = 5
    L_MAX = 100
    L_MIN = 0
    A_MAX = 127
    A_MIN = -128
    B_MAX = 127
    B_MIN = -128


    def __inti__(self):
        """Constructor."""
        super().__init__()

    def generate_colour_palette(self, image):
        print("Generating colour palette")

        # Remove alpha channel in case it has not already been removed


        # Step 1
        lab = self._convert_rgb_2_lab(image)
        (r, g, b) = lab[0, 0]
        print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))

        # Step 2
        self._divide_cielab_space(Nieves2020.SPLITS_PER_DIMENSION)




    def _convert_rgb_2_lab(self, image):
        if image.shape[2] == 4:
            image = color.rgba2rgb(image)
        print(image.shape)
        return color.rgb2lab(image, illuminant="D65")

    def _divide_cielab_space(self, splits):

        # Number of cubes
        num_cubes = 3 * splits


    class CielabCube:

        def __init__(self, light, a_star, b_star):
            self._light = light
            self._a_star = a_star
            self._b_star = b_star

            self._pixels = []

        # def add_pixel_to_cube
        # Alternatively, create a new 2d matrix and give each pixel a number corresponding to the given cube
        # Therefore, you would not need to create a bunch of object?


