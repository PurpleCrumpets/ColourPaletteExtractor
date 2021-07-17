import darkdetect
from PySide2 import QtGui
from PySide2.QtCore import QEvent, Qt, QPointF
from PySide2.QtGui import QPixmap, QColor, QPainter, QWheelEvent
from PySide2.QtWidgets import QScrollArea, QLabel, QWidget, QDockWidget, QApplication

__author__ = "Tim Churchfield"

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
        self.setWidget(self.image_display)

        self._toggle_recoloured_image_available = False  # Initially no recoloured image associated with tab
        self._toggle_recoloured_image_pressed = False  # Initially button is not pressed
        self._generate_palette_available = True

        # Setting properties to allow scrolling of image
        self.setWidgetResizable(False)

        self._status_bar_state = 0  # Initially no colour palette present
        self._progress_bar_value = 0  # Initially zero % complete

    @property
    def generate_palette_available(self) -> bool:
        return self._generate_palette_available

    @generate_palette_available.setter
    def generate_palette_available(self, value: bool) -> None:
        self._generate_palette_available = value

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

    @property
    def toggle_recoloured_image_available(self):
        return self._toggle_recoloured_image_available

    @toggle_recoloured_image_available.setter
    def toggle_recoloured_image_available(self, value):
        # TODO: make sure value is a boolean
        self._toggle_recoloured_image_available = value

    @property
    def toggle_recoloured_image_pressed(self):
        return self._toggle_recoloured_image_pressed

    @toggle_recoloured_image_pressed.setter
    def toggle_recoloured_image_pressed(self, value):
        self._toggle_recoloured_image_pressed = value

    def change_toggle_recoloured_image_pressed(self):
        self._toggle_recoloured_image_pressed = not self._toggle_recoloured_image_pressed

    def get_slider_positions(self):
        return QPointF(self.horizontalScrollBar().value(), self.verticalScrollBar().value())

    def set_slider_positions(self, x_position, y_position):
        self.horizontalScrollBar().setValue(x_position)
        self.verticalScrollBar().setValue(y_position)

    def wheelEvent(self, event: QWheelEvent):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:

            # print(event.pos(), event.angleDelta().y())
            if event.angleDelta().y() > 0:
                value = 0.1
            else:
                value = -0.1

            self.image_display.image_zoom(event.pos(), value)
        else:
            return super().wheelEvent(event)


class ImageDisplay(QLabel):
    zoom_factor = 1.25
    zoom_out_factor = 0.8
    _MINIMUM_SIZE = 100
    # _MAXIMUM_SIZE = 400  # TODO: Might be necessary - max out zoom factor for image?

    def __init__(self, image_data, parent=None):
        """Constructor."""
        super(ImageDisplay, self).__init__(parent)

        self._parent = parent
        self._pixmap_width = 0
        self._pixmap_height = 0

        # self.image_height = self.height()

        # TODO: keep these properties for a per image basis - try on Windows as well with a different image



        self.pixmap = image_data.get_image_as_q_image(image_data.image)
        self.pixmap = QPixmap(self.pixmap)
        self._set_pixmap(self.pixmap)

        # Set QLabel properties
        self._set_label_properties()

    def _set_label_properties(self) -> None:
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(ImageDisplay._MINIMUM_SIZE, ImageDisplay._MINIMUM_SIZE)

    def update_image(self, image):

        self.pixmap = ImageData.get_image_as_q_image(image)
        self.pixmap = QPixmap(self.pixmap)
        self._set_pixmap(self.pixmap)

    def _set_pixmap(self, pixmap: QPixmap) -> None:
        self._pixmap_height = pixmap.height()
        self._pixmap_width = pixmap.width()

        return super().setPixmap(self.pixmap)

    def event(self, event):
        if event.type() == QEvent.NativeGesture:
            # print(event.gestureType(), event.pos(), event.value())

            if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
                self.image_zoom(event.pos(), event.value())

        return super().event(event)

    def image_zoom(self, mouse_pos, value):
        # Mouse position relative to QLabel
        widget = self._parent

        # Current scroll bar locations
        old_scroll_bar_pos = widget.get_slider_positions()

        # Mouse position relative to image
        old_image_pos = old_scroll_bar_pos + mouse_pos
        relative_image_pos_x = old_image_pos.x() / self.size().width()
        relative_image_pos_y = old_image_pos.y() / self.size().height()

        # Zooming Image
        new_zoom_factor = 1 + value
        self.zoom_in(zoom_factor=new_zoom_factor)

        # Updating position of the scroll bar
        new_x_scroll = (relative_image_pos_x * self.size().width()) - mouse_pos.x()
        new_y_scroll = (relative_image_pos_y * self.size().height()) - mouse_pos.y()

        widget.set_slider_positions(new_x_scroll, new_y_scroll)

    def zoom_in(self, zoom_factor: float = zoom_factor) -> None:
        self._zoom(zoom_factor=zoom_factor)

    def zoom_out(self, zoom_factor: float = zoom_out_factor) -> None:
        self._zoom(zoom_factor=zoom_factor)

    def _zoom(self, zoom_factor: float) -> None:
        # Adapted from: https://stackoverflow.com/questions/53193010/how-to-resize-a-qlabel-with-pixmap-inside-a-qscrollarea
        old_size = self.size()

        # Checking new size doesn't break the size limits
        new_size = zoom_factor * self.size()
        if new_size.width() >= ImageDisplay._MINIMUM_SIZE and new_size.height() >= ImageDisplay._MINIMUM_SIZE:
            self.resize(new_size)
            self._update_zoom_level(zoom_factor, old_size)

    def _update_zoom_level(self, zoom_factor, old_size):

        new_size = self.size()

        # Updating current zoom level of the image
        if old_size != new_size:
            self._parent.zoom_level = self._parent.zoom_level * zoom_factor

    # def mousePressEvent(self, event):
    #
    #     if event.buttons() == Qt.LeftButton:
    #         print(event.pos())
    #
    #     return super().event(event)


class ColourPaletteDock(QDockWidget):

    _MINIMUM_SIZE = 100

    def __init__(self, parent=None):
        """Constructor."""

        super(ColourPaletteDock, self).__init__(parent)

        self._parent = parent
        self._colour_palette = []

        self._set_colour_palette_dock_properties()

        # Colour Palette Panel and Layout for adding the colours in the palette to
        self._set_colour_palette_panel()

        # Scroll Area (encompasses colour palette panel)
        self._set_scroll_area()

    def _set_colour_palette_dock_properties(self):
        self.setWindowTitle("Colour Palette")
        self.setMinimumWidth(ColourPaletteDock._MINIMUM_SIZE)
        self.setMinimumHeight(ColourPaletteDock._MINIMUM_SIZE)
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

    def add_colour_palette(self, colour_palette, image_id, relative_frequencies=None):
        # self._colour_palette = colour_palette

        update_palette = self._check_given_image_id_matches_with_current_tab(image_id)


        if update_palette:  # Updating GUI representation of colour palette
            print("Update colour palette for given tab")

            # Clear old palette
            self.remove_colour_palette()

            self.setWidget(self._scroll_area)

            # colour_palette_frequency =

            # Adding colours to the colour palette panel
            for colour, relative_frequency in zip(colour_palette, relative_frequencies):
                base_pixmap = self._create_colour_pixmap(colour)

                # label = QLabel()
                label = ColourBox()
                tool_tip = self._create_colour_tooltip(colour, relative_frequency)
                label.setToolTip(tool_tip)
                label.setPixmap(QPixmap(base_pixmap))
                self._colour_palette_layout.addWidget(label)

                # self.resize(175, 175)

    def _create_colour_pixmap(self, colour):
        # print(colour)
        red = colour[0]
        green = colour[1]
        blue = colour[2]
        # TODO: Add checks to make sure that colours are valid, only three channels etc.

        # Selecting background colour depending on dark/light mode is selected
        base_pixmap = QPixmap(80, 80)
        if darkdetect.isDark():
            base_pixmap.fill(QColor(255, 255, 255))
            # base_pixmap.fill(QColorConstants.White)
        else:
            # base_pixmap.fill(QColorConstants.Black)
            base_pixmap.fill(QColor(0, 0, 0))

        # Foreground colour
        colour_pixmap = QPixmap(72, 72)
        colour_pixmap.fill(QColor(red, green, blue))

        # Combining background with foreground
        painter = QPainter(base_pixmap)
        painter.drawPixmap(4, 4, colour_pixmap)
        painter.end()

        return base_pixmap

    def _create_colour_tooltip(self, colour, relative_frequency=None):
        red = colour[0]
        green = colour[1]
        blue = colour[2]
        # TODO: Add checks to make sure that colours are valid, only three channels etc.

        output = "[" + str(red) + ", " + str(green) + ", " + str(blue) + "]"

        if relative_frequency is not None:
            rounded_frequency = round((relative_frequency * 100), 2)
            output = output + " (" + str(rounded_frequency) + "%)"


        return output

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


class ColourBox(QLabel):

    def __init__(self, parent=None):
        """Constructor."""

        super(ColourBox, self).__init__(parent)

    def enterEvent(self, event: QEvent):
        pass
        # print("entered!")

    def leaveEvent(self, event: QEvent):
        pass
        # print("left!")
