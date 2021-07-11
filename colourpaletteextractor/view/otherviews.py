import sys

from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QWidget, QProgressBar, \
    QStatusBar, QMessageBox, QLabel

__version__ = "0.1"
__author__ = "Tim Churchfield"

from colourpaletteextractor.view.mainview import MainView


class AlgorithmDialogBox(QWidget):

    def __init__(self, parent=None):
        """Constructor."""

        super(AlgorithmDialogBox, self).__init__(parent)

    # def file_dialog(directory="", for_open=True, fmt="", is_folder=False):
    #     options = QFileDialog.Options()


class StatusBar(QStatusBar):

    def __init__(self,parent=None):
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

        self.addPermanentWidget(QLabel("v0.1"))
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

        self._status_label.setText("Generate the colour palette using " + command + "...")

    def set_intra_palette_message(self):
        self._status_label.setText("Generating colour palette...")  # TODO: This will change with the progress bar
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
        self._status_label.setText("Toggle between the original and recoloured image using " + command + "...")

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
        self.setIconPixmap(QPixmap("icons:about-small.png"))

        # Set text
        self.setWindowTitle("About ColourPaletteExtractor")
        self.setText("ColourPaletteExtractor is a simple tool to generate the colour palette of an image.")
        self.setInformativeText("Version 0.1")  # TODO: Get this from elsewhere

        # Show about box
        self.exec_()
