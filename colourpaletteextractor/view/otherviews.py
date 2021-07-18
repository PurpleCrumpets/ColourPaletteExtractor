import sys
import ctypes.wintypes

from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPixmap, QPainter
from PySide2.QtWidgets import QWidget, QProgressBar, \
    QStatusBar, QMessageBox, QLabel, QTabWidget, QDialog, QVBoxLayout, QCheckBox, QRadioButton, QGridLayout, \
    QStyleOption, QPushButton, QLineEdit, QFrame, QSizePolicy

__author__ = "Tim Churchfield"

from colourpaletteextractor import _version
from colourpaletteextractor._version import get_header, get_licence
from colourpaletteextractor.model import model
from colourpaletteextractor.model.algorithms import palettealgorithm


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

    def __init__(self, temp_path: str, parent=None):

        super(PreferencesWidget, self).__init__(parent)

        self._temp_path = temp_path

        self._set_properties()

    def get_algorithms_and_buttons(self) -> tuple[list[object], list[QRadioButton]]:
        return self._algorithms, self._algorithm_buttons

    def show_preferences(self):
        self.exec_()

    def _set_properties(self):

        self.setWindowTitle("Preferences")
        self.setWindowIcon(QIcon("icons:about-medium.png"))

        layout = QVBoxLayout()  # Top-level layout
        self.setLayout(layout)

        tabs = QTabWidget()  # tab widget for holding preferences
        layout.addWidget(tabs)  # Add tabs to layout

        # Create and add tabs to widget
        self._algorithm_properties_tab()
        tabs.addTab(self.algorithm_tab, "Algorithm")

        self._output_properties_tab()
        tabs.addTab(self.output_tab, "Output Directory")

    def _output_properties_tab(self):
        self.output_tab = QWidget()

        # Get default path (from model)

        # Create and populate layout of algorithm options
        layout = QGridLayout()

        # Path requirements explanation
        layout.addWidget(QLabel("Select the output folder for the colour palette reports:"), 0, 0, 1, 2)

        line = self._create_horizontal_line()
        layout.addWidget(line, 1, 0, 1, 3)  # Horizontal line spacer

        # Default path
        default_path_button = QRadioButton()  # TODO: get the current temp path by triggering the button?
        default_path_button.setChecked(True)
        layout.addWidget(default_path_button, 2, 0)
        # default_path_label = QLabel("[DEFAULT] " + self._temp_path)

        default_path_label = QLabel("Temporary Output Folder "
                                    + "(all unsaved reports will be lost on closing the application).")

        layout.addWidget(default_path_label, 2, 1)

        # User-selected path
        user_path_button = QRadioButton()
        layout.addWidget(user_path_button, 3, 0)
        layout.addWidget(QLabel("Alternative Ouput Folder:"), 3, 1)

        documents_directory = self._get_default_documents_directory()
        print(documents_directory)
        user_path_selector = QLineEdit(documents_directory)  # TODO: Default to user's documents folder (ColourPaletteExtractor) - if it doesn't exist, it will be created
        user_path_selector.setReadOnly(True)
        user_path_selector.setDisabled(True)
        layout.addWidget(user_path_selector, 4, 1)



        browse_button = QPushButton("...")
        layout.addWidget(browse_button, 4, 2)



        # Setting layout of buttons
        self.output_tab.setLayout(layout)

    def _get_default_documents_directory(self) -> str:

        if sys.platform == "win32":

            CSIDL_PERSONAL = 5  # My Documents
            SHGFP_TYPE_CURRENT = 0  # Get current, not default value

            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

            print(buf.value)
            documents_path = buf.value + "\\ColourPaletteExtractor"
            return documents_path

        elif sys.platform == "darwin":
            return "~/Documents/ColourPaletteExtractor"

        else:  # Linux
            return "~/Desktop/ColourPaletteExtractor"



    def _algorithm_properties_tab(self):
        self.algorithm_tab = QWidget()

        # Get default algorithm
        default_algorithm = model.ColourPaletteExtractorModel.DEFAULT_ALGORITHM

        # Create and populate layout of algorithm options
        layout = QGridLayout()
        layout.addWidget(QLabel("Select a colour palette algorithm:"), 0, 0, 1, 2)

        line = self._create_horizontal_line()
        layout.addWidget(line, 1, 0, 1, 3)  # Horizontal line spacer

        # Dynamically add algorithm options
        self._algorithms = list(palettealgorithm.get_implemented_algorithms())
        self._algorithm_buttons = []
        algorithm_labels = []

        # Create radio button and hyperlink for each algorithm
        default_algorithm_found = False
        for algorithm_class in self._algorithms:

            algorithm = algorithm_class()
            name = algorithm.name
            url = algorithm.url

            # Adding algorithm button
            new_button = self._create_algorithm_radio_button(name)
            if algorithm_class == default_algorithm:  # Set default algorithm

                new_button.setChecked(True)
                default_algorithm_found = True
                new_button.setText("[DEFAULT] " + name)  # Updating the name of the default algorithm

            elif algorithm_class == default_algorithm and default_algorithm_found:
                # TODO: throw exception
                pass

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
