import errno
# import sys
import os

from PySide2.QtCore import Qt, QDir
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QMainWindow, QToolBar, QStatusBar, QFileDialog, QTabWidget, QAction
# from PySide2.QtWidgets import QLabel
# from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QLineEdit
# from PySide2.QtWidgets import QComboBox
# from PySide2.QtWidgets import QRadioButton
# from PySide2.QtWidgets import QSpinBox

# Layouts
# from PySide2.QtWidgets import QHBoxLayout
# from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QGridLayout
# from PySide2.QtWidgets import QFormLayout

__version__ = "0.1"
__author__ = "Tim Churchfield"

from colourpaletteextractor import model
from colourpaletteextractor.view import otherviews

resources_dir = "resources"


class MainView(QMainWindow):
    """The main window of the colour palette extractor tool"""



    resources_path = os.path.join(os.path.dirname(__file__), resources_dir,)

    # QDir.setCurrent(resources_path)
    # if not QDir.setCurrent(resources_path):
    #     print(FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), resources_dir))
    #     # TODO fix exception handling
    # QDir.addSearchPath("icons", os.path.join(resources_path, "icons"))
    # QDir.addSearchPath("images", os.path.join(resources_path, "images"))

    default_new_tab_image = "images:800px-University_of_St_Andrews_arms.svg.png"

    def __init__(self, parent=None):
        """Initializer."""

        # Show GUI when using a Mac: https://www.loekvandenouweland.com/content/pyside2-big-sur-does-not-show-window
        # .html
        #
        os.environ['QT_MAC_WANTS_LAYER'] = '1'

        super(MainView, self).__init__(parent)

        QDir.setCurrent(MainView.resources_path)
        if not QDir.setCurrent(MainView.resources_path):
            print(FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), resources_dir))
            # TODO fix exception handling
        QDir.addSearchPath("icons", os.path.join(MainView.resources_path, "icons"))
        QDir.addSearchPath("images", os.path.join(MainView.resources_path, "images"))

        self._i = None

        # test = QDir.addSearchPath("icons", ".view/resources/icons")
        # print(test)

        self._create_gui()

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

    def _set_main_window_properties(self):
        """Set the properties of the main window of the GUI."""
        self.setWindowTitle("Colour Palette Extractor")
        # self.setFixedSize(235, 235)
        self.adjustSize()

    def _create_central_widget(self):
        """Create the central widget and add it to the main window."""

        # self._generalLayout = QVBoxLayout()
        # self._central_widget = QWidget(self)
        # self.setCentralWidget(self._central_widget)
        # self._central_widget.setLayout(self._generalLayout)

        # self._generalLayout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        # self.tabs.setLayout(self._generalLayout)

        self.setCentralWidget(self.tabs)

        # self._generalLayout.addWidget(self.tabs)

        # Create new tab to greet user
        # Add widgets to central widget

        # self._create_display()
        # self._create_buttons()

    def _create_actions(self):
        """Define actions and keyboard shortcuts."""

        # Open
        self.open_action = QAction(QIcon("icons:folder-open-outline.svg"), "&Open Image...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setStatusTip("Open new image") # TODO: currently doesn't do anything...

        # Save
        self.save_action = QAction(QIcon("icons:save-outline.svg"), "&Save Image with Palette...", self)
        self.save_action.setShortcut("Ctrl+S")

        # Print
        self._print_action = QAction(QIcon("icons:print-outline.svg"), "&Print...", self)
        self._print_action.setShortcut(QKeySequence.Print)

        # Select Algorithm
        self._select_algorithm_action = QAction(QIcon("icons:color-palette-outline.svg"), "&Select Algorithm...", self)
        self._select_algorithm_action.setShortcut("Ctrl+A")

        # Generate Colour Palette
        self.generate_palette_action = QAction(QIcon("icons:reload-outline.svg"), "&Generate Colour Palette", self)
        self.generate_palette_action.setShortcut("Ctrl+G")

        # View Saliency Map
        self._view_map_action = QAction(QIcon("icons:layers-outline.svg"), "&Saliency Map...", self, checkable=True)
        self._view_map_action.setChecked(False)
        self._view_map_action.setShortcut("Ctrl+Meta+M")

    def _create_menu(self):
        """Add menu bar to the main window."""

        # Main Menu
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction(self.open_action)
        self.menu.addSeparator()
        self.menu.addAction(self.save_action)
        self.menu.addSeparator()
        self.menu.addAction(self._print_action)

        # Edit Menu
        self.menu = self.menuBar().addMenu("&Edit")
        self.menu.addAction(self._select_algorithm_action)
        self.menu.addAction(self.generate_palette_action)

        # View Menu
        self.menu = self.menuBar().addMenu("&View")
        self.menu.addAction(self._view_map_action)

    def _create_toolbar(self):
        """Add toolbar to the main window."""
        tools = QToolBar()
        tools.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.addToolBar(tools)
        tools.addAction("Exit") # TODO: Doesn't currently do anything!
        tools.addSeparator()
        tools.addAction(self._select_algorithm_action)
        tools.addSeparator()
        tools.addAction(self.generate_palette_action)
        tools.addSeparator()

    def _create_status_bar(self):
        """Add status bar to the main window."""
        status = QStatusBar()
        status.showMessage("I am the status bar")  # TODO: save the version number somewhere
        self.setStatusBar(status)

    def show_file_dialog_box(self, supported_file_types):
        """Show dialog box for importing images."""

        # Creating string of support file types
        string = "Images ("
        count = 0
        for file_type in supported_file_types:
            if count != 0:
                string = string + " "
            string = string + "*." + file_type
            count += 1
        string = string + ")"

        return QFileDialog.getOpenFileName(self, "Open Image", "/", string)

    def tab_open_doubleclick(self, i):
        print("Double click")

    def current_tab_changed(self, i):
        """Update current tab index."""
        print("tab changed")
        self._i = self.tabs.currentIndex()
        # print("Current index: ", i)
        # TODO: more things may need to change (ie highlight show map to show that it is on for that image)


    def close_current_tab(self, i):
        # print("close current tab")
        # if self.tabs.count() < 2:
        #     return
        # TODO: set background to be something with instructions in case there are no tabs

        self.tabs.removeTab(i)
        self._i = self.tabs.currentIndex()
        return self._i

    def create_new_tab(self, image_data=None, label="Blank"):

        if image_data is None:
            label = "Blank"
        else:
            label = image_data.name

        self._i = self.tabs.addTab(otherviews.NewTab(image_data), label)
        self.tabs.setCurrentIndex(self._i)

    @property
    def i(self):
        """Getter for tab index number."""
        return self._i

    def _create_display(self):
        """Create and add the display for the calculator."""
        self.display = QLineEdit()

        # Set display properties
        self.display.setFixedHeight(35)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)

        # Add display to the general layout
        self._generalLayout.addWidget(self.display)

    def _create_buttons(self):
        """Create and add the buttons for the calculator."""
        self.buttons = {}
        _button_layout = QGridLayout()

        # Button text | position in the QGridLayout
        _buttons = {"7": (0, 0),
                    "8": (0, 1),
                    "9": (0, 2),
                    "/": (0, 3),
                    "C": (0, 4),
                    "4": (1, 0),
                    "5": (1, 1),
                    "6": (1, 2),
                    "*": (1, 3),
                    "(": (1, 4),
                    "1": (2, 0),
                    "2": (2, 1),
                    "3": (2, 2),
                    "-": (2, 3),
                    ")": (2, 4),
                    "0": (3, 0),
                    "00": (3, 1),
                    ".": (3, 2),
                    "+": (3, 3),
                    "=": (3, 4),
                    }

        # Create buttons and add them to the QGridLayout
        for btn_text, pos in _buttons.items():
            self.buttons[btn_text] = QPushButton(btn_text)
            self.buttons[btn_text].setFixedSize(40, 40)
            _button_layout.addWidget(self.buttons[btn_text], pos[0], pos[1])

        # Add buttons to the general layout
        self._generalLayout.addLayout(_button_layout)






