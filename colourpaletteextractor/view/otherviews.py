import sys

from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QWidget, QProgressBar, \
    QStatusBar, QMessageBox, QLabel, QTabWidget, QDialog, QVBoxLayout, QCheckBox, QRadioButton, QGridLayout

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
        self._status_label = QLabel("")
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

    def update_progress_bar(self, n):
        self._progress_bar.setValue(n)


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


    def _algorithm_properties_tab(self):
        self.algorithm_tab = QWidget()

        # Get default algorithm
        default_algorithm = model.ColourPaletteExtractorModel.DEFAULT_ALGORITHM

        # Create and populate layout of algorithm options
        layout = QGridLayout()
        layout.addWidget(QLabel("Select a colour palette algorithm:"), 0, 0)

        # Dynamically add algorithm options
        self._algorithms = list(palettealgorithm.get_implemented_algorithms())
        self._algorithm_buttons = []
        algorithm_labels = []


        # Create radio button and hyperlink for each algorithm
        count = 1
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

            # Increasing layout count
            count += 1

        # Reordering list of buttons and labels alphabetically by the algorithm name
        self._algorithms, self._algorithm_buttons, algorithm_labels =\
            self._reorder_algorithms(algorithms=self._algorithms,
                                     algorithm_buttons=self._algorithm_buttons,
                                     algorithm_labels=algorithm_labels)

        # Adding radio buttons and labels to the GUI
        count = 1
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
                            algorithm_labels: list[QLabel]) -> tuple[list[object], list[QRadioButton], list[QLabel]]:

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
