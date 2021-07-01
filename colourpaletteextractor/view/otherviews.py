from PySide2.QtCore import QPoint
from PySide2.QtGui import QPixmap, Qt, QImage, QPainter, QColor
from PySide2.QtWidgets import QFileDialog, QWidget, QLabel, QSizePolicy, QVBoxLayout, QLineEdit, QProgressBar, \
    QStatusBar, QDockWidget, QScrollArea
from PySide2.examples.widgets.layouts import flowlayout

from colourpaletteextractor.model.imagedata import ImageData
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

    def __init__(self, image_id=None, image_data=None, parent=None):
        """Constructor."""
        super(NewTab, self).__init__(parent)

        self._image_id = image_id
        self._generalLayout = QVBoxLayout(self)
        self._create_image_display(image_data)  # Display Image
        # self._create_palette_display()  # Display colour palette

        self._toggle_recoloured_image = False  # Initially no recoloured image associated with tab
        self._toggle_recoloured_image_pressed = False



        # self.resize(165, 200)

    @property
    def image_id(self):
        return self._image_id

    def _create_image_display(self, image_data):
        """Create and add image display."""
        self.image_display = ImageDisplay(image_data)

        # Add display to the general layout
        self._generalLayout.addWidget(self.image_display)

    # def _create_palette_display(self):
    #     """Create and add the widget for displaying an image's colour palette."""
    #     # TODO: currently a placeholder
    #     self.display = QLineEdit()
    #
    #     # Set display properties
    #     self.display.setFixedHeight(35)
    #     self.display.setAlignment(Qt.AlignRight)
    #     self.display.setReadOnly(True)
    #
    #     # Add display to the general layout
    #     self._generalLayout.addWidget(self.display, alignment=Qt.AlignCenter)

    @property
    def toggle_recoloured_image(self):
        return self._toggle_recoloured_image

    def enable_toggle_recoloured_image(self):
        self._toggle_recoloured_image = True

    @property
    def toggle_recoloured_image_pressed(self):
        return self._toggle_recoloured_image_pressed

    def change_toggle_recoloured_image_pressed(self):
        self._toggle_recoloured_image_pressed = not self._toggle_recoloured_image_pressed


class ImageDisplay(QLabel):

    def __init__(self, image_data, parent=None):
        """Constructor."""
        super(ImageDisplay, self).__init__(parent)

        # Set QLabel properties
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(300, 300)

        # Add image to QLabel
        # if image_data is None:
        #     print("No image data")
        #     self.pixmap = QPixmap(vw.MainView.default_new_tab_image) # TODO - dummy image for now
        #     image = self.pixmap
        # else:
        #     self.pixmap = image_data.get_image_as_q_image(image_data.image)
        #     image = QPixmap(self.pixmap)
        #     image = self.pixmap

        self.pixmap = image_data.get_image_as_q_image(image_data.image)
        image = QPixmap(self.pixmap)
        # image = QPixmap(self.pixmap)
        self.setPixmap(image.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

        # Set image properties
        self._set_image_properties()
        # self.pixmap.scaledToHeight(self.height(), Qt.SmoothTransformation)



        # self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # self.setScaledContents(True)
        # self.resize(165, 100)

    def _set_image_properties(self):
        """Set the properties of the displayed image."""
        # self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)  # Aspect ration not maintained
        # self.setScaledContents(True)
        pass


    def update_image(self, image):
        self.pixmap = ImageData.get_image_as_q_image(image)
        self.setPixmap(QPixmap(self.pixmap))
        # self.resize(165, 100)

    # def paintEvent(self, paint_event):
    #     print("This is a paint event")
        # painter = QPainter(self)
        # painter.drawPixmap(self.rect(), self.pixmap)

    # def paintEvent(self, event):
    #     # Adapted from: https://robonobodojo.wordpress.com/2018/07/01/automatic-image-sizing-with-pyside/
    #     size = self.size()
    #     painter = QPainter(self)
    #     point = QPoint(0, 0)
    #     scaled_picture = self.pixmap.scaled(size, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
    #     point.setX((size.width() - scaled_picture.width()) / 2)
    #     point.setY(size.height() - scaled_picture.height() / 2)
    #     print(point.x() , " ", point.y())
    #     painter.drawPixmap(point, scaled_picture)


class StatusBar(QStatusBar):

    def __init__(self, parent=None):
        """Constructor."""

        super(StatusBar, self).__init__(parent)


class ProgressBar(QProgressBar):

    def __init__(self, parent=None):
        """Constructor."""

        super(ProgressBar, self).__init__(parent)


class ColourPaletteDock(QDockWidget):

    def __init__(self, parent=None):
        """Constructor."""

        super(ColourPaletteDock, self).__init__(parent)

        self._colour_palette = []

        self.setWindowTitle("Colour Palette")
        self.setMinimumWidth(85)
        self.setMinimumHeight(85)
        # self.resize(175, 175)

        self._help_label = QLabel()
        self._help_label.setText("The colours")

        # self._palette_widget = QWidget()

        self.setWidget(self._help_label)

        # Layout for adding colours in palette to
        self._colour_palette_layout = flowlayout.FlowLayout()


    def add_colour_palette(self, colour_palette):
        # self._colour_palette = colour_palette

        # Clear old palette
        # from: https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
        for i in reversed(range(self._colour_palette_layout.count())):
            self._colour_palette_layout.itemAt(i).widget().setParent(None)

        # Colour Palette Panel
        colour_palette_panel = QWidget()
        # colour_palette_layout = flowlayout.FlowLayout()
        self._colour_palette_layout.setContentsMargins(15, 15, 15, 15)
        colour_palette_panel.setLayout(self._colour_palette_layout)

        # Scroll Area (encompasses colour palette panel)
        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # scroll_area.setContentsMargins(50, 50, 50, 50)
        scroll_area.setWidget(colour_palette_panel)

        self.setWidget(scroll_area)

        # Adding colours to the colour palette panel
        for colour in colour_palette:
            # print(colour)
            red = colour[0]
            green = colour[1]
            blue = colour[2]
            # TODO: Add checks to make sure that colours are valid, only three channels etc.

            # print('add colours')
            pixmap = QPixmap(80, 80)
            pixmap.fill(QColor(red, green, blue))

            label = QLabel()
            label.setPixmap(QPixmap(pixmap))
            self._colour_palette_layout.addWidget(label)

            # self.resize(175, 175)
