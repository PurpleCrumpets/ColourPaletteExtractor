from PySide2.QtGui import QPixmap, Qt, QImage
from PySide2.QtWidgets import QFileDialog, QWidget, QLabel, QSizePolicy, QVBoxLayout, QLineEdit
from colourpaletteextractor.view import mainview as vw


__version__ = "0.1"
__author__ = "Tim Churchfield"


class AlgorithmDialogBox(QWidget):

    def __init__(self, parent=None):
        """Constructor."""

        super(AlgorithmDialogBox, self).__init__(parent)

    # def file_dialog(directory="", for_open=True, fmt="", is_folder=False):
    #     options = QFileDialog.Options()


class NewTab(QWidget):

    def __init__(self, image_data=None, parent=None):
        """Constructor."""
        super(NewTab, self).__init__(parent)

        self._generalLayout = QVBoxLayout(self)
        self._create_image_display(image_data)  # Display Image
        self._create_palette_display()  # Display colour palette

        self.resize(165, 200)

    def _create_image_display(self, image_data):
        """Create and add image display."""
        self.image_display = ImageDisplay(image_data)

        # Add display to the general layout
        self._generalLayout.addWidget(self.image_display)

    def _create_palette_display(self):
        """Create and add the widget for displaying an image's colour palette."""
        # TODO: currently a placeholder
        self.display = QLineEdit()

        # Set display properties
        self.display.setFixedHeight(35)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)

        # Add display to the general layout
        self._generalLayout.addWidget(self.display)


class ImageDisplay(QLabel):

    def __init__(self, image_data=None, parent=None):
        """Constructor."""
        super(ImageDisplay, self).__init__(parent)

        if image_data is None:
            self.pixmap = QPixmap(vw.MainView.default_new_tab_image) # TODO - dummy image for now
        else:
            self.pixmap = image_data.get_image_as_q_image()

        self.setPixmap(QPixmap(self.pixmap))
        # self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # self.setScaledContents(True)
        self.resize(165, 100)

    # def _create_actions(self):
