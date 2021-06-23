import os.path
from PySide6.QtGui import QImage
from skimage import io, color
# from skimage.viewer import ImageViewer
# from cv2 import imread, imshow, waitKey, COLOR_BGR2GRAY, cvtColor, split, COLOR_BGR2LAB


class ImageData:

    def __init__(self, file_name_and_path):
        """Constructor."""

        # TODO: Need to check that the image has been saved using three colour channels (assuming RGB)
        # Otherwise - remove alpha channel in the case of PNG images
        # Convert from greyscale to rgb as well
        # viewer = ImageViewer(self._image)
        # viewer.show()

        self._image = io.imread(file_name_and_path)

        self._name = os.path.basename(file_name_and_path)
        while "." in self._name:
            self._name = os.path.splitext(self._name)[0]
        # TODO: what happens if the file has no extension?

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

    def get_image_as_q_image(self):
        height, width, channel = self._image.shape
        bytes_per_line = 3 * width
        return QImage(self._image.data, width, height, bytes_per_line, QImage.Format_RGB888)
