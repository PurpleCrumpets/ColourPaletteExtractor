from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QFileDialog, QWidget, QLabel, QSizePolicy, QVBoxLayout, QLineEdit

__version__ = "0.1"
__author__ = "Tim Churchfield"


class AlgorithmDialogBox(QWidget):

    def __init__(self, parent=None):
        """Constructor."""

        super(AlgorithmDialogBox, self).__init__(parent)

    # def file_dialog(directory="", for_open=True, fmt="", is_folder=False):
    #     options = QFileDialog.Options()


class TabWidget(QWidget):

    def __init__(self, parent=None):
        """Constructor."""
        super(TabWidget, self).__init__(parent)

        self._generalLayout = QVBoxLayout(self)
        self._create_image_display()  # Display Image
        self._create_palette_display()  # Display colour palette

        self.resize(165, 200)

    def _create_image_display(self):
        """Create and add image display."""
        self.image_display = ImageDisplay()

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

    def __init__(self, parent=None):
        """Constructor."""
        super(ImageDisplay, self).__init__(parent)

        self.pixmap = QPixmap("images:800px-University_of_St_Andrews_arms.svg.png")  # TODO - dummy image for now
        self.setPixmap(self.pixmap)
        # self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # self.setScaledContents(True)
        self.resize(165, 100)

    # def _create_actions(self):
