import errno
import sys
import os
import darkdetect
import qdarkstyle

from PySide2.QtCore import Qt, QDir, QEvent
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QMainWindow, QToolBar, QFileDialog, QTabWidget, QAction, QToolButton, QWidget, QSizePolicy

__version__ = "0.1"
__author__ = "Tim Churchfield"

from colourpaletteextractor.view import otherviews, tabview


resources_dir = "resources"



class MainView(QMainWindow):
    """The main window of the colour palette extractor tool"""

    if getattr(sys, "frozen", False):
        # If the application is run as a bundle, the PyInstaller bootloader extends the sys module
        # by a flag frozen=Truer and sets the app path into variable _MEIPASS'.
        # resources_path = sys._MEIPASS
        resources_path = os.path.join(sys._MEIPASS, resources_dir, )

    else:
        resources_path = os.path.join(os.path.dirname(__file__), resources_dir, )

    default_new_tab_image = "images:800px-University_of_St_Andrews_arms.jpg"
    app_icon = "app_icon"

    def __init__(self, parent=None):
        """Constructor."""

        # Show GUI when using a Mac:
        # https://www.loekvandenouweland.com/content/pyside2-big-sur-does-not-show-window.html
        os.environ['QT_MAC_WANTS_LAYER'] = '1'  # TODO: Check if this is necessary

        super(MainView, self).__init__(parent)

        # Setting icon path based on whether the system's dark mode/light mode is in use
        if darkdetect.isDark():
            icon_dir = "dark_mode"
        else:
            icon_dir = "light_mode"

        # Set Windows 10 specific settings
        if sys.platform == "win32":
            # Set application icon
            icon_name = MainView.app_icon + ".ico"
            self.setWindowIcon(QIcon(icon_name))

            # Set application theme
            dark_stylesheet = qdarkstyle.load_stylesheet_pyside2()
            self.setStyleSheet(dark_stylesheet)


        # Setting paths to resources
        QDir.setCurrent(MainView.resources_path)
        if not QDir.setCurrent(MainView.resources_path):
            print(FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), resources_dir))
            # TODO fix exception handling

        QDir.addSearchPath("icons", os.path.join(MainView.resources_path, "icons", icon_dir))
        QDir.addSearchPath("images", os.path.join(MainView.resources_path, "images"))

        self._create_gui()  # Generate GUI components



    def _create_gui(self):
        """Assemble the GUI components."""
        # Adapted from: https://realpython.com/python-pyqt-gui-calculator/

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

    def set_display_text(self, text):
        """Set display's text."""
        self.display.setText(text)
        self.display.setFocus()

    def display_text(self):
        """Get display's text."""
        return self.display.text()

    def clear_display(self):
        """Clear the display."""
        self.set_display_text(" ")

    def _set_main_window_properties(self):
        """Set the properties of the main window of the GUI."""
        self.setWindowTitle("Colour Palette Extractor")

    def _create_central_widget(self):
        """Create the central widget and add it to the main window."""

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)

        self.setCentralWidget(self.tabs)

    def _create_colour_palette_dock(self):
        self.colour_palette_dock = tabview.ColourPaletteDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colour_palette_dock)

    def _create_actions(self):
        """Define actions and keyboard shortcuts."""

        # Open
        self.open_action = QAction(QIcon("icons:folder-open-outline.svg"), "&Open Image(s)...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setStatusTip("Open new image") # TODO: currently doesn't do anything...

        # Save
        self.save_action = QAction(QIcon("icons:save-outline.svg"), "&Save Results...", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setDisabled(True)

        # Print
        self._print_action = QAction(QIcon("icons:print-outline.svg"), "&Print...", self)
        self._print_action.setShortcut(QKeySequence.Print)
        self._print_action.setDisabled(True)  # TODO: Needs to be implemented

        # Select Algorithm
        self._select_algorithm_action = QAction(QIcon("icons:settings-outline.svg"), "&Select Algorithm...", self)
        self._select_algorithm_action.setShortcut("Ctrl+A")
        self._select_algorithm_action.setDisabled(True)  # TODO: Needs to be implemented

        # Generate Colour Palette
        self.generate_palette_action = QAction(QIcon("icons:color-palette-outline.svg"), "&Generate Colour Palette", self)
        self.generate_palette_action.setShortcut("Ctrl+G")

        # Generate All Colour Palettes
        self.generate_all_action = QAction("&Generate All Colour Palettes", self)
        self.generate_all_action.setShortcut("Ctrl+Meta+G")

        # View Saliency Map
        self._view_map_action = QAction(QIcon("icons:layers-outline.svg"), "&Saliency Map...", self, checkable=True)
        self._view_map_action.setChecked(False)
        self._view_map_action.setDisabled(True)
        self._view_map_action.setShortcut("Ctrl+Meta+M")

        # Toggle original-recoloured image
        self.toggle_recoloured_image_action = QAction(QIcon("icons:eye-outline.svg"), "&Show Recoloured Image", self, checkable=True)
        self.toggle_recoloured_image_action.setChecked(False)
        self.toggle_recoloured_image_action.setDisabled(True)  # Initially disabled by default
        self.toggle_recoloured_image_action.setShortcut("Ctrl+T")

        # Exit GUI
        self.exit_action = QAction(QIcon("icons:exit-outline.svg"), "Quit Colour Palette Extractor", self)
        # TODO: Add a a dialog - are you sure you want to quit?

        # Zoom in and out
        self.zoom_in_action = QAction(QIcon("icons:add-circle-outline.svg"), "Zoom In", self)
        self.zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        self.zoom_out_action = QAction(QIcon("icons:remove-circle-outline.svg"), "Zoom Out", self)
        self.zoom_out_action.setShortcut(QKeySequence.ZoomOut)

        # TODO: Add button for fit to view and reset?
        #  from: https://doc.qt.io/qt-5/qtwidgets-widgets-imageviewer-example.html

        # About ColourPaletteExtractor
        self.about_action = QAction("About ColourPaletteExtractor", self)


    def _create_menu(self):
        """Add menu bar to the main window."""

        # Main Menu
        self.menu = self.menuBar().addMenu("&File")
        self.menu.addAction(self.about_action)
        self.menu.addSeparator()
        self.menu.addAction(self.open_action)
        self.menu.addSeparator()
        self.menu.addAction(self.save_action)
        self.menu.addSeparator()
        self.menu.addAction(self._print_action)

        # Edit Menu
        self.menu = self.menuBar().addMenu("&Edit")
        self.menu.addAction(self._select_algorithm_action)
        self.menu.addSeparator()
        self.menu.addAction(self.generate_palette_action)
        self.menu.addAction(self.generate_all_action)
        self.menu.addSeparator()

        # View Menu
        self.menu = self.menuBar().addMenu("&View")
        self.menu.addAction(self.zoom_in_action)
        self.menu.addAction(self.zoom_out_action)
        self.menu.addSeparator()
        self.menu.addAction(self._view_map_action)
        self.menu.addAction(self.toggle_recoloured_image_action)
        self.menu.addSeparator()


    def _create_toolbar(self):
        """Add toolbar to the main window."""
        tools = QToolBar()
        tools.setToolButtonStyle(Qt.ToolButtonIconOnly)

        # Left-aligned actions
        self.addToolBar(tools)
        tools.addAction(self.generate_palette_action)
        tools.addSeparator()

        toggle_recoloured_image_button = QToolButton(self)
        toggle_recoloured_image_button.setIcon(QIcon("icons:eye-outline.svg"))
        toggle_recoloured_image_button.setDefaultAction(self.toggle_recoloured_image_action)
        toggle_recoloured_image_button.setAutoRaise(True)
        tools.addWidget(toggle_recoloured_image_button)
        tools.addSeparator()

        zoom_in_button = QToolButton(self)
        zoom_in_button.setDefaultAction(self.zoom_in_action)
        tools.addWidget(zoom_in_button)

        zoom_out_button = QToolButton(self)
        zoom_out_button.setDefaultAction(self.zoom_out_action)
        tools.addWidget(zoom_out_button)

        # Adding spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tools.addWidget(spacer)

        # Right-aligned actions
        tools.addAction(self._select_algorithm_action)
        tools.addSeparator()

        exit_button = QToolButton(self)
        exit_button.setIcon(QIcon("icons:exit-outline.svg"))
        exit_button.setDefaultAction(self.exit_action)
        exit_button.setAutoRaise(True)
        tools.addWidget(exit_button)

    def _create_status_bar(self):
        """Add status bar to the main window."""
        self.status = otherviews.StatusBar()
        # status.showMessage("I am the status bar")  # TODO: save the version number somewhere
        self.setStatusBar(self.status)

    def show_file_dialog_box(self, supported_file_types):
        """Show dialog box for importing images."""

        # Creating string of support file types from provided list of file types
        string = "Images ("
        count = 0
        for file_type in supported_file_types:
            if count != 0:
                string = string + " "
            string = string + "*." + file_type
            count += 1
        string = string + ")"

        return QFileDialog.getOpenFileNames(self, "Open Image", "/", string)

    def tab_open_doubleclick(self, i):
        print("Double click")
        # Not in use!

    def close_current_tab(self, tab_index):
        self.tabs.removeTab(tab_index)

        return self.tabs.currentIndex()

    def create_new_tab(self, image_id, image_data):

        # if image_data is None:
        #     label = "How to Extract Colour Palette"
        # else:
        #     label = image_data.name

        label = image_data.name

        # Create and add new tab to GUI
        new_tab = tabview.NewTab(image_id=image_id, image_data=image_data)
        new_tab_index = self.tabs.addTab(new_tab, label)
        self.tabs.setCurrentIndex(new_tab_index)



