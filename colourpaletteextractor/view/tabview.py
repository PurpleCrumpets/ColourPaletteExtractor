from PySide2.QtCore import QEvent, Qt, QPointF
from PySide2.QtGui import QPixmap, QColor
from PySide2.QtWidgets import QScrollArea, QLabel, QWidget, QDockWidget

__version__ = "0.1"
__author__ = "Tim Churchfield"

# class NewTab(QWidget):
from PySide2.examples.widgets.layouts import flowlayout

from colourpaletteextractor.model.imagedata import ImageData


class NewTab(QScrollArea):

    def __init__(self, image_id=None, image_data=None, parent=None):
        """Constructor."""
        super(NewTab, self).__init__(parent)

        self._image_id = image_id
        # self._generalLayout = QVBoxLayout(self)
        self._zoom_level = 1

        # self._create_image_display(image_data)  # Display Image
        # self._create_palette_display()  # Display colour palette

        self.image_display = ImageDisplay(image_data, self)
        # self._generalLayout.addWidget(self.image_display)
        self.setWidget(self.image_display)

        self._toggle_recoloured_image = False  # Initially no recoloured image associated with tab
        self._toggle_recoloured_image_pressed = False

        # Setting properties to allow scrolling of image
        self.setWidgetResizable(False)

        self._status_bar_state = 0  # Initially no colour palette present
        self._progress_bar_value = 0  # Initially zero % complete

    @property
    def progress_bar_value(self):
        return self._progress_bar_value

    @progress_bar_value.setter
    def progress_bar_value(self, value):
        self._progress_bar_value = value

    @property
    def status_bar_state(self):
        return self._status_bar_state

    @status_bar_state.setter
    def status_bar_state(self, value):

        if isinstance(value, int) and 0 <= value <= 2:
            self._status_bar_state = value
        else:
            # TODO: throw exception if invalid status
            pass


    @property
    def zoom_level(self):
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value):
        self._zoom_level = value

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

    def get_slider_positions(self):
        return QPointF(self.horizontalScrollBar().value(), self.verticalScrollBar().value())

    def set_slider_positions(self, x_position, y_position):
        self.horizontalScrollBar().setValue(x_position)
        self.verticalScrollBar().setValue(y_position)


class ImageDisplay(QLabel):

    zoom_factor = 1.25
    zoom_out_factor = 0.8  # TODO: Not in use, see: https://doc.qt.io/qt-5/qtwidgets-widgets-imageviewer-example.html

    def __init__(self, image_data, parent=None):
        """Constructor."""
        super(ImageDisplay, self).__init__(parent)

        self._parent = parent

        # Set QLabel properties
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(300, 300)  # TODO: This breaks images that are zoomed out too far

        self.image_height = self.height()

        self.pixmap = image_data.get_image_as_q_image(image_data.image)
        self.image = QPixmap(self.pixmap)
        self.setPixmap(QPixmap(self.pixmap))
        self.setScaledContents(True)

        # Set image properties
        # self._set_image_properties()

    def event(self, event):
        if event.type() == QEvent.NativeGesture:
            # print(event.gestureType(), event.pos(), event.value())

            if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:

                mouse_pos = event.pos()  # Mouse position relative to QLabel
                widget = self._parent

                # Current scroll bar locations
                old_scroll_bar_pos = widget.get_slider_positions()

                # Mouse position relative to image
                old_image_pos = old_scroll_bar_pos + mouse_pos
                relative_image_pos_x = old_image_pos.x() / self.size().width()
                relative_image_pos_y = old_image_pos.y() / self.size().height()

                # Zooming Image
                new_zoom_factor = 1 + event.value()
                self.zoom_in(new_zoom_factor)

                # Updating position of the scroll bar
                new_x_scroll = (relative_image_pos_x * self.size().width()) - mouse_pos.x()
                new_y_scroll = (relative_image_pos_y * self.size().height()) - mouse_pos.y()

                widget.set_slider_positions(new_x_scroll, new_y_scroll)

        return super().event(event)

    # def mousePressEvent(self, event):
    #
    #     if event.buttons() == Qt.LeftButton:
    #         print(event.pos())
    #
    #     return super().event(event)

    def _set_image_properties(self):
        """Set the properties of the displayed image."""
        # self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)  # Aspect ration not maintained
        # self.setScaledContents(True)
        pass

    def zoom_in(self, zoom_factor=zoom_factor):
        # Adapted from: https://stackoverflow.com/questions/53193010/how-to-resize-a-qlabel-with-pixmap-inside-a-qscrollarea

        old_size = self.size()
        self.resize(zoom_factor * self.size())
        self._update_zoom_level(zoom_factor, old_size)

    def zoom_out(self, zoom_factor=zoom_out_factor):
        # Adapted from: https://stackoverflow.com/questions/53193010/how-to-resize-a-qlabel-with-pixmap-inside-a-qscrollarea
        old_size = self.size()
        self.resize(zoom_factor * self.size())
        self._update_zoom_level(zoom_factor, old_size)

    def _update_zoom_level(self, zoom_factor, old_size):

        new_size = self.size()

        # Updating current zoom level of the image
        if old_size != new_size:
            self._parent.zoom_level = self._parent.zoom_level * zoom_factor

    def update_image(self, image):
        self.pixmap = ImageData.get_image_as_q_image(image)
        self.setPixmap(QPixmap(self.pixmap))


class ColourPaletteDock(QDockWidget):

    def __init__(self, parent=None):
        """Constructor."""

        super(ColourPaletteDock, self).__init__(parent)

        self._parent = parent

        self._colour_palette = []

        self._set_colour_palette_dock_properties()

        # Initial Colour Palette Display
        self._help_label = QLabel()
        self._help_label.setText("The colours")
        self.setWidget(self._help_label)

        # Colour Palette Panel and Layout for adding the colours in the palette to
        self._set_colour_palette_panel()

        # Scroll Area (encompasses colour palette panel)
        self._set_scroll_area()

    def _set_colour_palette_dock_properties(self):
        self.setWindowTitle("Colour Palette")
        self.setMinimumWidth(85)
        self.setMinimumHeight(85)
        # self.resize(175, 175)

    def _set_colour_palette_panel(self):
        self._colour_palette_panel = QWidget()

        self._colour_palette_layout = flowlayout.FlowLayout()
        self._colour_palette_layout.setContentsMargins(15, 15, 15, 15)
        self._colour_palette_panel.setLayout(self._colour_palette_layout)

    def _set_scroll_area(self):
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # scroll_area.setContentsMargins(50, 50, 50, 50)
        self._scroll_area.setWidget(self._colour_palette_panel)



    def add_colour_palette(self, colour_palette, image_id):
        # self._colour_palette = colour_palette

        update_palette = self._check_given_image_id_matches_with_current_tab(image_id)
        print("Update colour palette for given tab:", update_palette)

        if update_palette:  # Updating GUI representation of colour palette

            # Clear old palette
            self.remove_colour_palette()



            self.setWidget(self._scroll_area)



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

    def remove_colour_palette(self):
        # from: https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
        for i in reversed(range(self._colour_palette_layout.count())):
            self._colour_palette_layout.itemAt(i).widget().setParent(None)

    def _check_given_image_id_matches_with_current_tab(self, image_id):

        if self._parent is not None:
            tab = self._parent.tabs.currentWidget()
            tab_image_id = tab.image_id

            if tab_image_id == image_id:
                return True

        return False