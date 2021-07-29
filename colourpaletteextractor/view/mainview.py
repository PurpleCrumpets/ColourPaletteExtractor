# ColourPaletteExtractor is a simple tool to generate the colour palette of an image.
# Copyright (C) 2021  Tim Churchfield
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import errno
import sys
import os

import darkdetect

from PySide2 import QtGui
from PySide2.QtCore import Qt, QDir
from PySide2.QtGui import QIcon, QKeySequence, QPixmap
from PySide2.QtWidgets import QMainWindow, QToolBar, QFileDialog, QTabWidget, QAction, QToolButton, QWidget, \
    QSizePolicy, QMessageBox, QApplication

import colourpaletteextractor.view.otherviews as otherviews
import colourpaletteextractor.view.tabview as tabview

from colourpaletteextractor import _version
from colourpaletteextractor.model.model import get_settings


class MainView(QMainWindow):
    """The main window of the ColourPaletteExtractor application.

    Args:
        parent: Parent object of the MainWindow. Defaults to None.


    Attributes:

        tabs (QTabWidget): tabbed widget for displaying and managing imported images.

        colour_palette_dock (tabview.ColourPaletteDock)

        _close_request_action (QAction): Action for closing the application

        open_action (QAction): Action for opening a new image

        generate_report_action (QAction): Action for generating a report for an image

        generate_all_report_action (QAction): Action for generating a report for all images with a colour palette

        generate_palette_action (QAction): Action for generating the colour palette for an image

        generate_all_palette_action (QAction): Action for generating the colour palette for all images

        stop_action (QAction): Action for stopping the report or colour palette being generated for an image

        preferences_menu_action (QAction): Action for opening the preferences menu

        show_help_action (QAction): Action for showing the quick start guide

        toggle_recoloured_image_action (QAction): Action for toggling between the original and the recoloured image

        zoom_in_action (QAction): Action for zooming into an image

        zoom_out_action (QAction): Action for zooming out of an image

        about_menu_action (QAction): Action for showing the about information widget

        show_palette_dock_action (QAction): Action for showing the colour palette dock

        show_toolbar_action (QAction): Action for showing the toolbar

        tools: (QToolBar): Toolbar for holding QToolButtons used in the GUI

        status (otherviews.StatusBar): Status bar for holding hints, the progress bar and the current version of the
            application

    """

    app_icon = "app_icon"
    """str: The name of the file used as the application's icon."""

    RESOURCES_DIR = "resources"
    """str: The name of the directory containing the icons and images used for the GUI."""

    resources_path = ""
    """str: The path to the resources used for the GUI. 
    
    This will vary depending on whether the code has been compiled into an application or is been run from the command 
    line."""

    default_new_tab_image = ""
    """str: The name of the file used as the default new tab (the quick start guide)."""

    # Set the correct path to resources depending on whether the application is been run from a Python script or as
    # a dedicated application/bundle.
    if getattr(sys, "frozen", False):  # Running as a bundle
        resources_path = os.path.join(sys._MEIPASS, RESOURCES_DIR, )
    else:
        resources_path = os.path.join(os.path.dirname(__file__), RESOURCES_DIR, )

    # Select the appropriate quick start guide depending on the system's theme (dark/light mode)
    if darkdetect.isDark():
        default_new_tab_image = "images:how-to-dark-mode.png"
    else:
        default_new_tab_image = "images:how-to-light-mode.png"

    def __init__(self, parent=None):

        # Show GUI when using a Mac:
        # See: https://www.loekvandenouweland.com/content/pyside2-big-sur-does-not-show-window.html
        # Accessed 23/07/2021
        os.environ['QT_MAC_WANTS_LAYER'] = '1'

        super(MainView, self).__init__(parent)

        # Sett the icon path based on the system's theme (dark/light mode)
        if darkdetect.isDark():
            icon_dir = "dark-mode"
        else:
            icon_dir = "light-mode"

        # Set Windows 10 specific application icon
        if sys.platform == "win32":
            icon_name = MainView.app_icon + ".ico"
            self.setWindowIcon(QIcon(icon_name))

        # Set paths to resources
        QDir.setCurrent(MainView.resources_path)
        if not QDir.setCurrent(MainView.resources_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), MainView.RESOURCES_DIR)

        QDir.addSearchPath("icons", os.path.join(MainView.resources_path, "icons", icon_dir))
        QDir.addSearchPath("images", os.path.join(MainView.resources_path, "images"))

        self._create_gui()  # Generate main GUI components
        self._set_size_and_shape()  # Set size/shape of GUI

    def show_file_dialog_box(self, supported_file_types: set[str]) -> tuple[list[str], str]:
        """Show the dialog box for importing images.

        Args:
            supported_file_types (set[str]): The supported file types (e.g., '.png')

        Returns:
            list(str): The list of the absolute paths to the images to be loaded into the application

            str: The filter used when selecting the images to import

        """

        # Create string of support file types from provided list of file types
        string = "Images ("
        count = 0
        for file_type in supported_file_types:
            if count != 0:
                string = string + " "
            string = string + "*." + file_type
            count += 1
        string = string + ")"

        return QFileDialog.getOpenFileNames(self, "Open Image", "", string)

    def close_current_tab(self, tab_index: int) -> int:
        """Close the tab with the given index.

        Args:
            tab_index (int): The index of the tab to close

        Returns:
            (int): The index of the tab that is now visible after closing the selected tab

        """

        self.tabs.removeTab(tab_index)

        return self.tabs.currentIndex()

    def create_new_tab(self, image_id, image_data) -> None:
        """Create a new image tab for the main window.

        Args:
            image_id (str): ID of the image to be used for the new tab (e.g., 'Tab_1')
            image_data (model.imagedata.ImageData): Object containing tab and image properties and state

        """
        label = image_data.name

        # Create and add new tab to GUI
        new_tab = tabview.NewTab(image_id=image_id, image_data=image_data)
        new_tab_index = self.tabs.addTab(new_tab, label)
        self.tabs.setCurrentIndex(new_tab_index)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Intercept GUI close event to check if the user wishes to close the GUI.

        Args:
            event (QtGui.QCloseEvent): Close event

        """

        # Message box to ask for permission to close the GUI
        close_box = QMessageBox()
        close_box.setIconPixmap(QPixmap("icons:about-small.png"))
        close_box.setWindowIcon(QIcon("icons:about-small.png"))
        close_box.setText("Are you sure you want to quit?")
        close_box.setInformativeText("Any unsaved progress will be lost.")
        close_box.setStandardButtons(QMessageBox.Close | QMessageBox.Cancel)
        close_box.setDefaultButton(QMessageBox.Cancel)

        reply = close_box.exec_()  # Create the permission box

        # Analyse user's response
        if reply == QMessageBox.Close:
            self.close_action.trigger()

            # Save main window size and position to settings
            self._write_settings()
            print("Closing " + _version.__application_name__ + "...")
            event.accept()
        else:
            # Ignore the close event
            event.ignore()

    def _set_size_and_shape(self) -> None:
        """Set the size and shape of the main window of the GUI."""
        settings = get_settings()

        settings.beginGroup("main window")

        # Resize main window
        if settings.contains('size'):
            size = settings.value("size")
            self.resize(size)

        # Reposition main window
        if settings.contains('position'):
            position = settings.value("position")
            self.move(position)
        else:
            # Centre screen based on its current size
            # Adapted from:
            # https: //stackoverflow.com/questions/9357944/how-to-make-a-widget-in-the-center-of-the-screen-in-pyside-pyqt
            # Accessed: 25/07/21
            center_point = QtGui.QScreen.availableGeometry(QApplication.primaryScreen()).center()
            fg = self.frameGeometry()
            fg.moveCenter(center_point)
            self.move(fg.topLeft())

        settings.endGroup()

    def _create_gui(self) -> None:
        """Assemble the GUI components.

        Adapted from: `ref1`_

        Accessed: 25/07/21

        .. _ref1:
           https://realpython.com/python-pyqt-gui-calculator/

        """

        # Create instance of application's GUI
        self._set_main_window_properties()

        # Create actions
        self._create_actions()

        # Add features to main window
        self._create_central_widget()
        self._create_menu()
        self._create_toolbar()
        self._create_status_bar()
        self._create_colour_palette_dock()

        self.preferences = otherviews.PreferencesWidget()  # Create preferences panel
        self.batch_progress_widget = otherviews.BatchGenerationProgressWidget()  # Create batch generation progress box

    def _write_settings(self) -> None:
        """Write the main window's size and shape to the settings file."""

        settings = get_settings()

        settings.beginGroup("main window")
        settings.setValue("position", self.pos())
        settings.setValue("size", self.size())
        settings.endGroup()

        settings.sync()

    def _set_main_window_properties(self):
        """Set the properties of the main window of the GUI."""

        self.setWindowTitle(_version.__application_name__)

    def _create_central_widget(self):
        """Create the central widget and add it to the main window."""

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setUsesScrollButtons(True)

        self.setCentralWidget(self.tabs)

    def _create_colour_palette_dock(self):
        """Create the colour palette dock for displaying the colours in the colour palette."""

        self.colour_palette_dock = tabview.ColourPaletteDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colour_palette_dock)

    def _create_actions(self):
        """Define actions and keyboard shortcuts."""

        # Select operating system-specific modifier button
        if sys.platform == "darwin":
            meta_key = "Meta"
        else:
            meta_key = "Alt"

        # Close application
        self._close_request_action = QAction("E&xit", self)
        if sys.platform != "darwin":
            self._close_request_action.setShortcut("Ctrl+w")
        self._close_request_action.triggered.connect(self.close)
        self.close_action = QAction(self)

        # Open image
        self.open_action = QAction(QIcon("icons:folder-open-outline.svg"), "&Open Image(s)...", self)
        self.open_action.setShortcut("Ctrl+O")

        # Generate report
        self.generate_report_action = QAction(QIcon("icons:document-text-outline.svg"), "Generate &Report...", self)
        self.generate_report_action.setShortcut("Ctrl+R")

        # Generate all reports
        self.generate_all_report_action = QAction("Generate All Re&ports...", self)
        self.generate_all_report_action.setShortcut("Ctrl+" + meta_key + "+R")

        # Generate Colour Palette
        self.generate_palette_action = QAction(QIcon("icons:color-palette-outline.svg"),
                                               "&Generate Colour Palette", self)
        self.generate_palette_action.setShortcut("Ctrl+G")
        # self.generate_palette_action.setStatusTip("Generate the colour palette...")

        # Generate All Colour Palettes
        self.generate_all_palette_action = QAction("Generate &All Colour Palettes", self)
        self.generate_all_palette_action.setShortcut("Ctrl+" + meta_key + "+G")

        # Stop action
        self.stop_action = QAction(QIcon("icons:stop-circle-outline.svg"), "&Stop Current Tab", self)
        self.stop_action.setShortcut("Ctrl+s")
        self.stop_action.setDisabled(True)

        # Preferences
        if sys.platform == "darwin":
            self.preferences_menu_action = QAction("&Preferences", self)
            self.preferences_menu_action.setShortcut("Ctrl+,")
        else:
            self.preferences_menu_action = QAction(QIcon("icons:settings-outline.svg"), "Se&ttings", self)
            self.preferences_menu_action.setShortcut("Ctrl+" + meta_key + "+S")
        self.preferences_action = QAction(QIcon("icons:settings-outline.svg"), "Se&ttings", self)

        # Help
        self.show_help_action = QAction(QIcon("icons:help-circle-outline.svg"), "&Help", self)
        self.show_help_menu_action = QAction(QIcon("icons:help.svg"), "&Help", self)

        # Toggle original-recoloured image
        self.toggle_recoloured_image_action = QAction(QIcon("icons:eye-outline.svg"),
                                                      "Toggle &Recoloured Image", self, checkable=True)
        self.toggle_recoloured_image_action.setChecked(False)
        self.toggle_recoloured_image_action.setDisabled(True)  # Initially disabled by default
        self.toggle_recoloured_image_action.setShortcut("Ctrl+T")

        # Zoom in and out
        self.zoom_in_action = QAction(QIcon("icons:add-circle-outline.svg"), "Zoom &In", self)
        self.zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        self.zoom_out_action = QAction(QIcon("icons:remove-circle-outline.svg"), "Zoom &Out", self)
        self.zoom_out_action.setShortcut(QKeySequence.ZoomOut)

        # About ColourPaletteExtractor
        if sys.platform == "darwin":
            self.about_menu_action = QAction("&About ColourPaletteExtractor", self)
        else:
            self.about_menu_action = QAction("&About", self)

        self.about_action = QAction(QIcon("icons:information-circle-outline.svg"),
                                    "&About", self)

        # Show colour palette dock widget
        self.show_palette_dock_action = QAction("Show &Colour Palette Dock", self)

        # Show tool bar widget
        self.show_toolbar_action = QAction("Show &Toolbar", self)

    def _create_menu(self):
        """Create and add the menu bar to the main window."""

        # Main Menu
        self._menu = self.menuBar().addMenu("&File")
        if sys.platform == "darwin":
            self._menu.addAction(self.about_menu_action)
            self._menu.addSeparator()
        self._menu.addAction(self.preferences_menu_action)
        self._menu.addSeparator()
        self._menu.addAction(self.open_action)

        if sys.platform != "darwin":
            self._menu.addSeparator()
            self._menu.addAction(self._close_request_action)

        # Edit Menu
        self._menu = self.menuBar().addMenu("&Edit")
        self._menu.addAction(self.generate_palette_action)
        self._menu.addAction(self.generate_all_palette_action)
        self._menu.addSeparator()
        self._menu.addAction(self.generate_report_action)
        self._menu.addAction(self.generate_all_report_action)
        self._menu.addSeparator()
        self._menu.addAction(self.stop_action)

        # View Menu
        self._menu = self.menuBar().addMenu("&View")
        self._menu.addAction(self.zoom_in_action)
        self._menu.addAction(self.zoom_out_action)
        self._menu.addSeparator()
        self._menu.addAction(self.toggle_recoloured_image_action)
        self._menu.addSeparator()
        self._menu.addAction(self.show_toolbar_action)
        self._menu.addAction(self.show_palette_dock_action)
        self._menu.addSeparator()

        # Help Menu
        self._menu = self.menuBar().addMenu("&Help")
        self._menu.addAction(self.show_help_menu_action)

        if sys.platform != "darwin":
            self._menu.addSeparator()
            self._menu.addAction(self.about_menu_action)

    def _create_toolbar(self):
        """Create and add the toolbar to the main window."""
        self.tools = QToolBar("Toolbar")
        self.tools.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.tools.setMovable(False)

        # Left-aligned actions
        self.addToolBar(self.tools)
        self.tools.addSeparator()

        # Open button
        open_button = QToolButton(self)
        open_button.setDefaultAction(self.open_action)
        self.tools.addWidget(open_button)
        self.tools.addSeparator()

        # Generate colour palette button
        generate_palette_button = QToolButton(self)
        generate_palette_button.setDefaultAction(self.generate_palette_action)
        self.tools.addWidget(generate_palette_button)
        self.tools.addSeparator()

        # Generate report button
        generate_report_button = QToolButton()
        generate_report_button.setDefaultAction(self.generate_report_action)
        self.tools.addWidget(generate_report_button)
        self.tools.addSeparator()

        # Toggle recoloured image button
        toggle_recoloured_image_button = QToolButton(self)
        toggle_recoloured_image_button.setIcon(QIcon("icons:eye-outline.svg"))
        toggle_recoloured_image_button.setDefaultAction(self.toggle_recoloured_image_action)
        toggle_recoloured_image_button.setAutoRaise(True)
        self.tools.addWidget(toggle_recoloured_image_button)
        self.tools.addSeparator()

        # Zoom-in button
        zoom_in_button = QToolButton(self)
        zoom_in_button.setDefaultAction(self.zoom_in_action)
        self.tools.addWidget(zoom_in_button)
        self.tools.addSeparator()

        # Zoom-out button
        zoom_out_button = QToolButton(self)
        zoom_out_button.setDefaultAction(self.zoom_out_action)
        self.tools.addWidget(zoom_out_button)

        # Adding spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.tools.addWidget(spacer)

        # Right-aligned actions

        # Stop button
        stop_button = QToolButton(self)
        stop_button.setDefaultAction(self.stop_action)
        self.tools.addWidget(stop_button)
        self.tools.addSeparator()

        # Preferences button
        preferences_button = QToolButton(self)
        preferences_button.setDefaultAction(self.preferences_action)
        self.tools.addWidget(preferences_button)
        self.tools.addSeparator()

        # Help button
        help_button = QToolButton(self)
        help_button.setDefaultAction(self.show_help_action)
        self.tools.addWidget(help_button)
        self.tools.addSeparator()

        # About button
        about_button = QToolButton(self)
        about_button.setIcon(QIcon("icons:information-circle-outline.svg"))
        about_button.setDefaultAction(self.about_action)
        about_button.setAutoRaise(True)
        self.tools.addWidget(about_button)
        self.tools.addSeparator()

    def _create_status_bar(self):
        """Create and add the status bar to the main window."""

        self.status = otherviews.StatusBar()
        self.setStatusBar(self.status)
