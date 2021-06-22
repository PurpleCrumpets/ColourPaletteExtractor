import cv2


class ImageData:

    def __init__(self, file_name_and_path):
        """Constructor."""
        self._image = cv2.imread(file_name_and_path)
        gray_img = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Greyscale Image", gray_img)
        cv2.waitKey(0)  # Press any key to exit (doesn't work??)
