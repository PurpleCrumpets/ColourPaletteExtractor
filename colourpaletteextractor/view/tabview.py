from __future__ import annotations

import darkdetect
import numpy as np
from PySide2 import QtCore

from PySide2.QtCore import QEvent, Qt, QPointF
from PySide2.QtGui import QPixmap, QColor, QPainter, QWheelEvent
from PySide2.QtWidgets import QScrollArea, QLabel, QWidget, QDockWidget, QApplication
from PySide2.examples.widgets.layouts import flowlayout

import colourpaletteextractor.model.imagedata as imagedata


class NewTab(QScrollArea):
    """Modified QScrollArea to display and manipulate an image (via the :class:`ImageDisplay` class).

    Args:
        image_id (str): The ID ('Tab_xx') associated with a tab and image.
        image_data (imagedata.ImageData): The ImageData object that hold the information associated with an image.
        parent: Parent object of the NewTab Defaults to None.

    Attributes:
        image_display (ImageDisplay): ImageDisplay used to show the QPixmap representation of the current image.

    """

    def __init__(self, image_id: str = None, image_data: imagedata.ImageData = None, parent=None):
        """Constructor."""
        super(NewTab, self).__init__(parent)

        self._image_id = image_id
        self._zoom_level = 1

        self.image_display = ImageDisplay(image_data, self)
        self.setWidget(self.image_display)

        self._toggle_recoloured_image_available = False  # Initially no recoloured image associated with tab
        self._toggle_recoloured_image_pressed = False  # Initially button is not pressed
        self._generate_palette_available = True
        self._generate_report_available = False  # Initially cannot generate report

        # Setting properties to allow scrolling of image
        self.setWidgetResizable(False)

        self._status_bar_state = 0  # Initially no colour palette present
        self._progress_bar_value = 0  # Initially zero % complete

    @property
    def generate_report_available(self) -> bool:
        """The ability to generate the colour palette report for the current NewTab object.

        Returns:
            (bool): Returns true if the colour palette report can be generated. Otherwise false.

        """

        return self._generate_report_available

    @generate_report_available.setter
    def generate_report_available(self, value: bool) -> None:
        self._generate_report_available = value

    @property
    def generate_palette_available(self) -> bool:
        """The ability to generate the colour palette for the current NewTab object.

        Returns:
            (bool): Returns true if the colour palette can be generated. Otherwise false.

        """

        return self._generate_palette_available

    @generate_palette_available.setter
    def generate_palette_available(self, value: bool) -> None:
        self._generate_palette_available = value

    @property
    def progress_bar_value(self) -> float:
        """The current level of progress shown by the status bar for the associated NewTab object.

        Returns:
            (float): The current level of progress shown by thr status bar.

        """
        return self._progress_bar_value

    @progress_bar_value.setter
    def progress_bar_value(self, value):
        self._progress_bar_value = value

    @property
    def status_bar_state(self) -> int:
        """The current status bar state, represented by an integer.

        See the :meth:`otherviews.StatusBar.set_status_bar` method for more information.

        Returns:
            (int): The current status bar state.

        """

        return self._status_bar_state

    @status_bar_state.setter
    def status_bar_state(self, value: int):

        if isinstance(value, int) and 0 <= value <= 3:
            self._status_bar_state = value
        else:
            raise ValueError(value, "is an invalid status bar state!")

    @property
    def zoom_level(self) -> float:
        """The degree of magnification for the currently displayed image.

        Returns:
            (float): The degree of magnification for the current image.

        """
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value: float):
        self._zoom_level = value

    @property
    def image_id(self) -> str:
        """The image ID of the images and its data that is linked to the current NewTab object

        Returns:
            (str): The ID ('Tab_xx') associated with a tab and image.

        """
        return self._image_id

    @property
    def toggle_recoloured_image_available(self) -> bool:
        """Stores the availability of the recoloured image (if it available to be displayed or not).

        Returns:
            (bool): True if the recoloured image is available. Otherwise false.

        """

        return self._toggle_recoloured_image_available

    @toggle_recoloured_image_available.setter
    def toggle_recoloured_image_available(self, value: bool):
        self._toggle_recoloured_image_available = value

    @property
    def toggle_recoloured_image_pressed(self) -> bool:
        """The status of the toggle button used to switch between the original image and the recoloured image.

        Returns:
            (bool): True if the recoloured image is displayed by the GUI. Otherwise false.

        """
        return self._toggle_recoloured_image_pressed

    @toggle_recoloured_image_pressed.setter
    def toggle_recoloured_image_pressed(self, value: bool):
        self._toggle_recoloured_image_pressed = value

    def change_toggle_recoloured_image_pressed(self) -> None:
        """Toggle the _toggle_recoloured_image_pressed attribute between true and false (its opposite)."""

        self._toggle_recoloured_image_pressed = not self._toggle_recoloured_image_pressed

    def get_slider_positions(self) -> QPointF:
        """Get the grip positions of the horizontal and vertical scrollbars.

        Returns:
                (QPointF): The position of the grip for the horizontal and veritcal scrollbars.

        """

        return QPointF(self.horizontalScrollBar().value(), self.verticalScrollBar().value())

    def set_slider_positions(self, x_position: float, y_position: float) -> None:
        """Set the position of the horizontal and vertical scrollbar's grip.

        Args:
            x_position (float): Position of the grip for the horizontal scrollbar.
            y_position (float): Position of the grip for the vertical scrollbar.

        """

        self.horizontalScrollBar().setValue(x_position)
        self.verticalScrollBar().setValue(y_position)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Intercepts the super class' wheelEvent to allow zooming into and out of an image using the mousewheel.

        Also calls the super class' wheelEvent handler at the end.

        Args:
            event (QWheelEvent): Mousewheel event

        """

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:

            if event.angleDelta().y() > 0:
                value = 0.1
            else:
                value = -0.1

            self.image_display.image_zoom(event.pos(), value)
        else:
            return super().wheelEvent(event)

    def _create_image_display(self, image_data: imagedata.ImageData) -> None:
        """Create and add an :class:`ImageDisplay` object to the NewTab.

        Args:
            image_data (imagedata.ImageData): The ImageData object that hold the information associated with an image.

        """

        self.image_display = ImageDisplay(image_data)

        # Add display to the general layout
        self._generalLayout.addWidget(self.image_display)


class ImageDisplay(QLabel):
    """A modified QLabel to display and manipulate the current image.

    Args:
        image_data (imagedata.ImageData): The ImageData object that hold the information associated with an image.
        parent: Parent object of the ImageDisplay. Defaults to None.

    """

    zoom_factor = 1.25
    """The zoom-in factor used when the user zoom's into the image via the zoom-in button."""

    zoom_out_factor = 0.8
    """The zoom-out factor used when the user zoom's out of the image via the zoom-out button."""

    _MINIMUM_SIZE = 100
    """The minimum size of the image display."""

    def __init__(self, image_data: imagedata.ImageData, parent=None):

        super(ImageDisplay, self).__init__(parent)

        self._parent = parent
        self._pixmap_width = 0
        self._pixmap_height = 0

        self.pixmap = image_data.get_image_as_q_image(image_data.image)
        self.pixmap = QPixmap(self.pixmap)
        self._set_pixmap(self.pixmap)

        # Set QLabel properties
        self._set_label_properties()

    def _set_label_properties(self) -> None:
        """Set the size and position properties of the ImageDisplay."""

        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(ImageDisplay._MINIMUM_SIZE, ImageDisplay._MINIMUM_SIZE)

    def update_image(self, image: np.array) -> None:
        """Update the image shown by the ImageDisplay.

        Args:
            image (np.array): Numpy array representing an image.

        """

        self.pixmap = imagedata.ImageData.get_image_as_q_image(image)
        self.pixmap = QPixmap(self.pixmap)
        self._set_pixmap(self.pixmap)

    def _set_pixmap(self, pixmap: QPixmap) -> None:
        """Set the new size of the QPixmap representation of the current image and update the GUI.

        Args:
            pixmap (QPixmap): The QPixmap representation of the current image.

        """

        self._pixmap_height = pixmap.height()
        self._pixmap_width = pixmap.width()

        return super().setPixmap(self.pixmap)

    def event(self, event: QEvent) -> bool:
        """Intercept the QLabel's event if it is a gesture to allow for zooming into and out of the current image.

        Also calls the super class' event handler at the end.

        Args:
            event (QEvent): An event.

        Returns:
            (bool): The result from the super class' event handler.

        """

        if event.type() == QEvent.NativeGesture:

            if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
                self.image_zoom(event.pos(), event.value())

        return super().event(event)

    def image_zoom(self, mouse_pos: QtCore.QPoint, value: float) -> None:
        """Zoom into or out of an image at the mouse pointer's current location.

        Args:
            mouse_pos (QtCore.QPoint): Current position of the mouse cursor.
            value (float): The degree of magnification of the image.

        """

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
        """Zoom into the current image.

        Args:
            zoom_factor (float): The new magnification factor for the image.

        """

        self._zoom(zoom_factor=zoom_factor)

    def zoom_out(self, zoom_factor: float = zoom_out_factor) -> None:
        """Zoom out of the current image.

        Args:
            zoom_factor (float): The new magnification factor for the image.

        """
        self._zoom(zoom_factor=zoom_factor)

    def _zoom(self, zoom_factor: float) -> None:
        """Zooming into the displayed image.

        Adapted from `ref1`_

        Accessed: 27/07/2021

        Args:
            zoom_factor (float): The magnification factor for the image.


        .. _ref1:
           https://stackoverflow.com/questions/53193010/how-to-resize-a-qlabel-with-pixmap-inside-a-qscrollarea

        """

        old_size = self.size()

        # Checking new size doesn't break the size limits
        new_size = zoom_factor * self.size()
        if new_size.width() >= ImageDisplay._MINIMUM_SIZE and new_size.height() >= ImageDisplay._MINIMUM_SIZE:
            self.resize(new_size)
            self._update_zoom_level(zoom_factor, old_size)

    def _update_zoom_level(self, zoom_factor: float, old_size: QtCore.QSize) -> None:
        """Update the degree of magnification for the current image.

        Args:
            zoom_factor (float): The new magnification factor for the image.
            old_size (QtCore.QSize): Current dimensions of the image

        """

        new_size = self.size()

        # Updating current zoom level of the image
        if old_size != new_size:
            self._parent.zoom_level = self._parent.zoom_level * zoom_factor


class ColourPaletteDock(QDockWidget):
    """A modified QDockWidget to hold small images of each colour in an image's colour palette.

    Args:
        parent: Parent object of the ColourPaletteDock. Defaults to None.

    """
    _MINIMUM_SIZE = 115
    """The minimum width of the colour palette dock."""

    def __init__(self, parent=None):

        super(ColourPaletteDock, self).__init__(parent)

        self._parent = parent
        self._colour_palette = []

        self._set_colour_palette_dock_properties()

        # Colour Palette Panel and Layout for adding the colours in the palette to
        self._set_colour_palette_panel()

        # Scroll Area (encompasses colour palette panel)
        self._set_scroll_area()

    def add_colour_palette(self, colour_palette: list[np.array],
                           image_id: str,
                           relative_frequencies: list[float] = None) -> None:
        """Clear the colour palette dock and add a new image's colour palette to the dock.

        Args:
            colour_palette (list[np.array]): List of colours in the colour palette.
            image_id (str): The ID ('Tab_xx') associated with a tab and image.
            relative_frequencies (list[float]): The relative frequencies of each colour in the colour palette in the
                recoloured image.

        """

        update_palette = self._check_given_image_id_matches_with_current_tab(image_id)

        if update_palette:  # Updating GUI representation of colour palette

            # Clear old palette
            self.remove_colour_palette()

            self.setWidget(self._scroll_area)

            # Adding colours to the colour palette panel
            for colour, relative_frequency in zip(colour_palette, relative_frequencies):
                base_pixmap = self._create_colour_pixmap(colour)

                label = ColourBox()
                tool_tip = self._create_colour_tooltip(colour, relative_frequency)
                label.setToolTip(tool_tip)
                label.setPixmap(QPixmap(base_pixmap))
                self._colour_palette_layout.addWidget(label)

    def remove_colour_palette(self) -> None:
        """Remove all of the :class:`ColourBox` labels from the colour palette dock.

        Adapted from: `ref`_

        Accessed: 27/07/2021

        .. _ref:
           https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt

        """

        for i in reversed(range(self._colour_palette_layout.count())):
            self._colour_palette_layout.itemAt(i).widget().setParent(None)

    def _set_colour_palette_dock_properties(self) -> None:
        """Set the main properties of the colour palette dock."""

        self.setWindowTitle("Colour Palette")
        self.setMinimumWidth(ColourPaletteDock._MINIMUM_SIZE)
        self.setMinimumHeight(ColourPaletteDock._MINIMUM_SIZE)

    def _set_colour_palette_panel(self) -> None:
        """Set the widget and its properties that is used to hold each of the colours in the colour palette."""

        self._colour_palette_panel = QWidget()

        self._colour_palette_layout = flowlayout.FlowLayout()
        self._colour_palette_layout.setContentsMargins(15, 15, 15, 15)
        self._colour_palette_panel.setLayout(self._colour_palette_layout)

    def _set_scroll_area(self) -> None:
        """Set the scroll area and its properties used for viewing and navigating through an image's colour palette."""

        self._scroll_area = QScrollArea()

        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll_area.setWidget(self._colour_palette_panel)

    @staticmethod
    def _create_colour_pixmap(colour: np.array) -> QPixmap:
        """Create a coloured QPixmap to represent a colour in the colour palette.

        To help differentiate a colour that is similar to the application's background colour,
        a frame is added to the QPixmap. The colour of this frame will change with the system's
        current theme (dark mode or light mode).

        Args:
            colour (np.array): sRGB triplet representing a colour in the colour palette.

        Returns:
            (QPixmap): A coloured 'icon' to represent a colour in the :class:`ColourPaletteDock`.

        Raises:
            ValueError: If the provided colour does not have three colour channels.

        """

        if colour.shape[0] != 3:
            raise ValueError("The provided colour does not have 3 colour channels: ", colour.shape)

        red = colour[0]
        green = colour[1]
        blue = colour[2]

        # Selecting background colour depending on dark/light mode is selected
        base_pixmap = QPixmap(80, 80)
        if darkdetect.isDark():
            base_pixmap.fill(QColor(255, 255, 255))
        else:
            base_pixmap.fill(QColor(0, 0, 0))

        # Foreground colour
        colour_pixmap = QPixmap(72, 72)
        colour_pixmap.fill(QColor(red, green, blue))

        # Combining background with foreground
        painter = QPainter(base_pixmap)
        painter.drawPixmap(4, 4, colour_pixmap)
        painter.end()

        return base_pixmap

    @staticmethod
    def _create_colour_tooltip(colour: np.array, relative_frequency: float = None) -> str:
        """Create the tooltip for a colour in the colour palette.

        Args:
            colour (np.array): sRGB triplet representing a colour in the colour palette.
            relative_frequency (float): Relative frequency of the colour.

        Returns:
            (str): String formatted like: '[r, g, b] (xy.zq %)'

        Raises:
            ValueError: If the provided colour does not have three colour channels.

        """

        if colour.shape[0] != 3:
            raise ValueError("The provided colour does not have 3 colour channels: ", colour.shape)

        red = colour[0]
        green = colour[1]
        blue = colour[2]

        output = "[" + str(red) + ", " + str(green) + ", " + str(blue) + "]"

        if relative_frequency is not None:
            rounded_frequency = round((relative_frequency * 100), 2)
            output = output + " (" + str(rounded_frequency) + "%)"

        return output

    def _check_given_image_id_matches_with_current_tab(self, image_id: str) -> bool:
        """Check that the given image_id is associated with the current tab.

        Args:
            image_id (str): The ID ('Tab_xx') associated with a tab and image.

        Returns:
            (bool): True if the given image_id corresponds to the current tab. Otherwise returns false.

        """

        if self._parent is not None:
            tab = self._parent.tabs.currentWidget()
            tab_image_id = tab.image_id

            if tab_image_id == image_id:
                return True

        return False


class ColourBox(QLabel):
    """Modified QLabel to hold an individual colour in the colour palette.

    Args:
        parent: The parent object of the ColourBox. The default is None.

    """

    def __init__(self, parent=None):
        super(ColourBox, self).__init__(parent)

    def enterEvent(self, event: QEvent) -> None:
        """Intercept an enter event.

        In the future, this could be used to trigger the highlighting regions of the image that use this
        colour in the recoloured image.

        Args:
            event (QEvent): Enter event.

        """

        pass

    def leaveEvent(self, event: QEvent):
        """Intercept a leave event.

        In the future, this could be used to cancel the highlighting of regions of the image that use this
        colour in the recoloured image.

        Args:
            event (QEvent): Leave event.

        """
        pass
