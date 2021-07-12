import os.path
from PySide2.QtGui import QImage
from skimage import io, color
# from skimage.viewer import ImageViewer
# from cv2 import imread, imshow, waitKey, COLOR_BGR2GRAY, cvtColor, split, COLOR_BGR2LAB


class ImageData:

    # default_file =

    def __init__(self, file_name_and_path=None):
        """Constructor."""

        self._recoloured_image = None
        self._colour_palette = []

        # TODO: Need to check that the image has been saved using three colour channels (assuming RGB)
        # TODO: Check colour space and adapt to that
        # Otherwise - remove alpha channel in the case of PNG images
        # Convert from greyscale to rgb as well
        # viewer = ImageViewer(self._image)
        # viewer.show()

        if file_name_and_path is None:
            # self._image =
            print("None")
        else:
            self._image = io.imread(file_name_and_path)

            if self._image.shape == 4:
                self._remove_alpha_channel()

            self._name = os.path.basename(file_name_and_path)
            while "." in self._name:
                self._name = os.path.splitext(self._name)[0]
            # TODO: what happens if the file has no extension?

    @property
    def image(self):
        return self._image

    @property
    def recoloured_image(self):
        return self._recoloured_image

    @recoloured_image.setter
    def recoloured_image(self, value):
        self._recoloured_image = value

    @property
    def colour_palette(self):
        return self._colour_palette

    @colour_palette.setter
    def colour_palette(self, value):
        self._colour_palette = value

    @staticmethod
    def get_image_as_q_image(image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        return QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)

    def _remove_alpha_channel(self):
        self._image = color.rgba2rgb(self._image)

    def _check_colour_space(self):
        print("Checking colour space")

        # rgb = io.imread(file_name_and_path)
        # (r, g, b) = rgb[0, 0]
        # print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))
        #
        # # Update pixel at [0, 0] to be blue to confirm the white point
        # rgb[0, 0] = (0, 0, 255)
        # (r, g, b) = rgb[0, 0]
        # print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))
        #
        # lab = color.rgb2lab(rgb, illuminant="D65")
        #
        # (r, g, b) = lab[0, 0]
        # print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))

        # print("Done!")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
