import inspect
import sys
import ctypes.wintypes
from abc import ABC

from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt, QSettings
from PySide2.QtGui import QIcon, QPixmap, QPainter, QMovie
from PySide2.QtWidgets import QWidget, QProgressBar, \
    QStatusBar, QMessageBox, QLabel, QTabWidget, QDialog, QVBoxLayout, QCheckBox, QRadioButton, QGridLayout, \
    QStyleOption, QPushButton, QLineEdit, QFrame, QSizePolicy, QFileDialog, QHBoxLayout

__author__ = "Tim Churchfield"

from colourpaletteextractor import _version
from colourpaletteextractor._version import get_header, get_licence
from colourpaletteextractor.model import model
from colourpaletteextractor.model.algorithms import palettealgorithm
from colourpaletteextractor.model.model import get_settings


class AlgorithmDialogBox(QWidget):

    def __init__(self, parent=None):
        """Constructor."""

        super(AlgorithmDialogBox, self).__init__(parent)

    # def file_dialog(directory="", for_open=True, fmt="", is_folder=False):
    #     options = QFileDialog.Options()


class StatusBar(QStatusBar):

    def __init__(self, parent=None):
        """Constructor."""

        super(StatusBar, self).__init__(parent)

        self._add_status_bar_elements()

        self.set_pre_palette_message()

    def _add_status_bar_elements(self):
        # self._status_label = QLabel("")
        self._status_label = ElidedLabel(text="", width=100, parent=self)
        self._progress_bar = ProgressBar()
        self._progress_bar.setFixedWidth(250)

        # Spacers
        self._spacer1 = QWidget()
        self._spacer1.setFixedWidth(5)
        self._spacer2 = QWidget()
        self._spacer2.setFixedWidth(5)
        self._spacer3 = QWidget()
        self._spacer3.setFixedWidth(5)

        self.addWidget(self._spacer1, 1)
        self.addWidget(self._status_label, 1)
        self.addWidget(self._progress_bar, 1)
        self.addWidget(self._spacer2, 1)

        # self.removeWidget(self._progress_bar)  # Temporarily removing the progress bar

        self.addPermanentWidget(QLabel("v" + _version.__version__))
        self.addPermanentWidget(self._spacer3)

    def set_status_bar(self, state):
        # TODO: add checks for the value

        if state == 0:
            # Show original status if no colour palette and it is not being generated
            self.set_pre_palette_message()
        elif state == 1:
            # Show toggle status if colour palette has been generated
            self.set_intra_palette_message()
        elif state == 2:
            # Show progress bar if colour palette is being generated
            self.set_post_palette_message()
        elif state == 3:
            self.set_intra_report_message()

    def set_pre_palette_message(self):

        if sys.platform == "win32" or sys.platform == "linux":
            command = "Ctrl+G"
        elif sys.platform == "darwin":
            command = "⌘G"
        else:
            # TODO: throw exception
            command = ""

        self._status_label.setText("Generate the colour palette using " + command)

    def set_intra_palette_message(self):
        self._status_label.setText("Generating colour palette")  # TODO: This will change with the progress bar
        # self.addWidget(self._progress_bar)

    def set_post_palette_message(self):

        if sys.platform == "win32" or sys.platform == "linux":
            command = "Ctrl+T"
        elif sys.platform == "darwin":
            command = "⌘T"
        else:
            # TODO: throw exception
            command = ""

        # self.removeWidget(self._progress_bar)
        self._status_label.setText("Toggle between the original and recoloured image using " + command)

    def set_intra_report_message(self):
        self._status_label.setText("Generating colour palette report")

    def update_progress_bar(self, n):
        self._progress_bar.setValue(n)


class ElidedLabel(QLabel):
    "Adapted from https://stackoverflow.com/questions/35080148/how-to-hide-or-cut-a-qwidget-text-when-i-change-main-window-size"
    "and: https://www.mimec.org/blog/status-bar-and-elided-label"
    "both accessed 18/07/2020"

    _width = _text = _elided = None

    def __init__(self, text='', width=40, parent=None):
        super(ElidedLabel, self).__init__(text, parent)
        self.setMinimumWidth(width if width > 0 else 1)

    def elided_text(self):
        return self._elided or ''

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawFrame(painter)
        margin = self.margin()
        rect = self.contentsRect()
        rect.adjust(margin, margin, -margin, -margin)
        text = self.text()
        width = rect.width()
        if text != self._text or width != self._width:
            self._text = text
            self._width = width
            self._elided = self.fontMetrics().elidedText(
                text, Qt.ElideRight, width)
        option = QStyleOption()
        option.initFrom(self)
        self.style().drawItemText(
            painter, rect, self.alignment(), option.palette,
            self.isEnabled(), self._elided, self.foregroundRole())


class ProgressBar(QProgressBar):

    def __init__(self, parent=None):
        """Constructor."""

        super(ProgressBar, self).__init__(parent)

        self.setMinimum(0)
        self.setMaximum(100)


class AboutBox(QMessageBox):

    def __init__(self, parent=None):
        """Constructor."""

        super(AboutBox, self).__init__(parent)

        # Set icon
        self.setIconPixmap(QPixmap("icons:about-medium.png"))
        self.setWindowIcon(QIcon("icons:about-medium.png"))

        # Set text
        self.setWindowTitle("About ColourPaletteExtractor")

        header = get_header()
        licence = get_licence()

        self.setText(header + "\n \n" + licence)
        self.setInformativeText(" ")  # Used to increase the width of the about box

        # Show about box
        self.exec_()


class PreferencesWidget(QDialog):

    def __init__(self, parent=None):

        super(PreferencesWidget, self).__init__(parent)

        self._read_settings()
        self._set_properties()

    def show_preferences(self):
        self.exec_()

    def update_preferences(self):
        self._read_settings()

        for button, algorithm in zip(self._algorithm_buttons, self._algorithms):
            if algorithm == self._default_algorithm:
                button.setChecked(True)
                break

        self.user_path_selector.setEnabled(self._use_user_dir)
        self.user_path_selector.setText(self._user_output_dir)
        self.browse_button.setEnabled(self._use_user_dir)
        self.default_path_button.setChecked(not self._use_user_dir)

    def show_output_directory_dialog_box(self, current_path: str):
        """Show dialog box for selecting output directory for reports."""

        return QFileDialog.getExistingDirectory(self, "Select output folder", current_path, QFileDialog.ShowDirsOnly)

    def get_algorithms_and_buttons(self) -> tuple[list[object], list[QRadioButton]]:
        return self._algorithms, self._algorithm_buttons

    def _read_settings(self):
        self._settings = get_settings()

        # Check if settings file exists
        if not self._settings.contains('output directory/user directory'):
            print("Settings file not found...")
            # TODO: throw exception

        # Load values from settings
        self._settings.beginGroup("output directory")
        self._temp_dir = self._settings.value('temporary directory')
        self._user_output_dir = self._settings.value('user directory')
        self._use_user_dir = self._settings.value('use user directory')
        self._settings.endGroup()

        self._settings.beginGroup("algorithm")
        self._default_algorithm = self._settings.value('default algorithm')
        self._selected_algorithm = self._settings.value('selected algorithm')
        self._settings.endGroup()

    def _set_properties(self):

        self.setWindowTitle("Preferences")
        self.setWindowIcon(QIcon("icons:about-medium.png"))

        layout = QVBoxLayout()  # Top-level layout
        tabs = QTabWidget()  # tab widget for holding preferences
        layout.addWidget(tabs)  # Add tabs to layout

        # Create and add tabs to widget
        self._algorithm_properties_tab()
        tabs.addTab(self.algorithm_tab, "Algorithm")

        self._output_properties_tab()
        tabs.addTab(self.output_tab, "Output Directory")

        # Add reset preferences button
        self.reset_preferences_button = QPushButton("Reset Preferences")
        self.reset_preferences_button.setAutoDefault(False)
        self.reset_preferences_button.setDefault(False)
        layout.addWidget(self.reset_preferences_button, alignment=QtCore.Qt.AlignRight)

        # Set layout
        self.setLayout(layout)

    def _output_properties_tab(self):
        self.output_tab = QWidget()
        layout = QGridLayout()

        # Path requirements explanation
        layout.addWidget(QLabel("Select the output folder for the colour palette reports:"), 0, 0, 1, 2)

        # Horizontal line spacer
        line = self._create_horizontal_line()
        layout.addWidget(line, 1, 0, 1, 3)

        # Default path button and label
        self.default_path_button = QRadioButton()  # TODO: get the current temp path by triggering the button?
        layout.addWidget(self.default_path_button, 2, 0)

        default_path_label = QLabel("Temporary Output Folder "
                                    + "(all unsaved reports will be lost upon closing the application).")
        layout.addWidget(default_path_label, 2, 1)

        # User-selected path
        self.user_path_button = QRadioButton()
        layout.addWidget(self.user_path_button, 3, 0)
        layout.addWidget(QLabel("Alternative Output Folder:"), 3, 1)

        self.user_path_selector = QLineEdit(
            self._user_output_dir)  # TODO: Default to user's documents folder (ColourPaletteExtractor) - if it doesn't exist, it will be created
        self.user_path_selector.setReadOnly(True)
        layout.addWidget(self.user_path_selector, 4, 1)

        # Browse button for a user to select their desired output directory
        self.browse_button = QPushButton("...")
        self.browse_button.setAutoDefault(False)
        self.browse_button.setDefault(False)

        layout.addWidget(self.browse_button, 4, 2)

        # Selecting temporary or user selected radio button
        if int(self._use_user_dir) == 1:
            self.user_path_button.setChecked(True)
            self.user_path_selector.setEnabled(True)
            self.browse_button.setEnabled(True)

        else:
            self.default_path_button.setChecked(True)
            self.user_path_selector.setDisabled(True)
            self.browse_button.setDisabled(True)  # TODO: not sure this is working

        # Setting layout of buttons
        self.output_tab.setLayout(layout)

    def _algorithm_properties_tab(self):
        self.algorithm_tab = QWidget()

        # Create and populate layout of algorithm options
        layout = QGridLayout()
        layout.addWidget(QLabel("Select a colour palette algorithm:"), 0, 0, 1, 2)

        line = self._create_horizontal_line()
        layout.addWidget(line, 1, 0, 1, 3)  # Horizontal line spacer

        # Dynamically add algorithm options
        self._algorithms = list(palettealgorithm.get_implemented_algorithms())
        self._algorithm_buttons = []
        algorithm_labels = []

        # print(self._algorithms)

        # Create radio button and hyperlink for each algorithm
        default_algorithm_found = False
        for algorithm_class in self._algorithms:

            # Check if class has abstract method - hence should not be added as a selectable algorithm
            if inspect.isabstract(algorithm_class):
                self._algorithms.remove(algorithm_class)
                continue

            algorithm = algorithm_class()
            name = algorithm.name
            url = algorithm.url

            # Adding algorithm button
            new_button = self._create_algorithm_radio_button(name)
            if algorithm_class == self._default_algorithm:  # Set default algorithm

                # new_button.setChecked(True)
                default_algorithm_found = True
                new_button.setText("[DEFAULT] " + name)  # Updating the name of the default algorithm

            elif algorithm_class == self._default_algorithm and default_algorithm_found:
                # TODO: throw exception
                pass

            # Set selected algorithm
            if algorithm_class == self._selected_algorithm:
                print("Setting checked")  # TODO: this did not appear to work on Windows???
                new_button.setChecked(True)

            self._algorithm_buttons.append(new_button)

            # Adding algorithm url hyperlink label
            new_label = self._create_algorithm_link_label(url)
            algorithm_labels.append(new_label)

        # Reordering list of buttons and labels alphabetically by the algorithm name
        self._algorithms, self._algorithm_buttons, algorithm_labels = \
            self._reorder_algorithms(algorithms=self._algorithms,
                                     algorithm_buttons=self._algorithm_buttons,
                                     algorithm_labels=algorithm_labels)

        # Adding radio buttons and labels to the GUI
        count = 2
        for button, label in zip(self._algorithm_buttons, algorithm_labels):
            layout.addWidget(button, count, 0)
            layout.addWidget(label, count, 1)
            count += 1

        # Setting layout of buttons
        self.algorithm_tab.setLayout(layout)

        # Checking if default algorithm found
        if not default_algorithm_found:
            # TODO: throw exception
            pass

    def _my_isabstract(self, obj) -> bool:
        """Get if ABC is in the object's __bases__ attribute."""
        try:
            return ABC in obj.__bases__
        except AttributeError:
            return False

    def _create_algorithm_radio_button(self, name: str) -> QRadioButton:

        # Adding algorithm name if provided
        if name is not None:
            button = QRadioButton(name)
        else:
            button = QRadioButton("Algorithm name not provided!")

        return button

    def _create_algorithm_link_label(self, url) -> QLabel:
        # Adding url as a hyperlink if provided
        if url is not None:
            text = '<a href="' + url + '">Ref</a>'

        else:
            text = "-"

        label = QLabel()
        label.setText(text)
        label.setOpenExternalLinks(True)

        return label

    def _reorder_algorithms(self, algorithms: list[object],
                            algorithm_buttons: list[QRadioButton],
                            algorithm_labels: list[QLabel]) -> tuple[list[object],
                                                                     list[QRadioButton],
                                                                     list[QLabel]]:

        # Reordering list of labels alphabetically by the algorithm name
        algorithm_labels = [x for _, x in sorted(zip(algorithm_buttons, algorithm_labels),
                                                 key=lambda pair: pair[0].text(),
                                                 reverse=True)]

        # Reordering list of algorithms alphabetically by the algorithm name
        algorithms = [x for _, x in sorted(zip(algorithm_buttons, algorithms),
                                           key=lambda pair: pair[0].text(),
                                           reverse=True)]

        # Reordering list of algorithm buttons alphabetically by the algorithm name
        algorithm_buttons.sort(key=lambda x: x.text(), reverse=True)

        return algorithms, algorithm_buttons, algorithm_labels

    def _create_horizontal_line(self) -> QWidget:
        line = QWidget()  # https://stackoverflow.com/questions/10053839/how-does-designer-create-a-line-widget"
        line.setFixedHeight(2)
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line.setStyleSheet("background-color: #c0c0c0;")
        return line

    # def _get_default_documents_directory(self) -> str:
    #
    #     if sys.platform == "win32":
    #
    #         CSIDL_PERSONAL = 5  # My Documents
    #         SHGFP_TYPE_CURRENT = 0  # Get current, not default value
    #
    #         buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    #         ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    #
    #         print(buf.value)
    #         documents_path = buf.value + "\\ColourPaletteExtractor"
    #         return documents_path
    #
    #     elif sys.platform == "darwin":
    #         return "~/Documents/ColourPaletteExtractor"
    #
    #     else:  # Linux
    #         return "~/Desktop/ColourPaletteExtractor"


class ErrorBox(QMessageBox):

    def __init__(self, box_type: str = None, parent=None):
        """Constructor."""

        super(ErrorBox, self).__init__(parent)

        header = None

        # Set icon
        self.setWindowIcon(QIcon("icons:about-medium.png"))  # Window icon

        if box_type == "warning":
            self.setIcon(QMessageBox.Warning)  # Icon
            header = "Warning!"
        elif box_type == "information":
            self.setIcon(QMessageBox.Information)  # Icon
            header = "Heads-Up!"

        else:
            self.setIconPixmap(QPixmap("icons:about-medium.png"))

        self.setWindowTitle(header)  # Window title
        self.setText(header)  # Main text


class BatchGenerationProgressWidget(QDialog):

    def __init__(self):
        super().__init__()

        self._cancel_text = "Cancelling..."

        self._batch_type = ""
        self._total_count = 0
        self._current_count = 0

        self._set_properties()

    def show_widget(self, total_count: int, batch_type: str):
        self._total_count = total_count
        self._current_count = 0
        self._batch_type = batch_type
        self.label.setText("")
        self._set_label_text()
        self._progress_bar.setValue(self._current_count)
        self._progress_bar.setMaximum(self._total_count)
        self.show()

    def _set_properties(self):
        self.setWindowTitle("Progress")
        self.setWindowIcon(QIcon("icons:about-medium.png"))

        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        # self.setWindowModality(Qt.NonModal)

        main_layout = QVBoxLayout()  # Top-level layout
        self.setLayout(main_layout)

        # Text label
        secondary_layout = QHBoxLayout()
        main_layout.addLayout(secondary_layout)
        self.label = QLabel()
        self._set_label_text()
        secondary_layout.addWidget(self.label)

        # Animated progress gif
        self._progress_gif = QMovie("images:animated-colour-palette.gif")
        self._progress_gif.setScaledSize(QtCore.QSize(40, 40))
        self._progress_label = QLabel()
        self._progress_label.setMovie(self._progress_gif)
        self._progress_gif.start()
        secondary_layout.addWidget(self._progress_label, alignment=QtCore.Qt.AlignRight)

        # Progress bar
        self._progress_bar = ProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(self._total_count)
        main_layout.addWidget(self._progress_bar)

        # Cancel button
        self.cancel_batch_button = QPushButton("Cancel")
        self.cancel_batch_button.setAutoDefault(False)
        self.cancel_batch_button.setDefault(False)
        main_layout.addWidget(self.cancel_batch_button, alignment=QtCore.Qt.AlignRight)

    def update_progress(self):
        self._current_count += 1

        self._progress_bar.setValue(self._current_count)
        self._set_label_text()

    def set_cancel_text(self):
        self.label.setText(self._cancel_text)

    def _set_label_text(self) -> None:
        if self.label.text() != self._cancel_text:
            self.label.setText("Generated " + self._batch_type + " for "
                                + str(self._current_count) + "/"
                                + str(self._total_count) + " images")
