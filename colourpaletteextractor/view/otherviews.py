import sys

from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QWidget, QProgressBar, \
    QStatusBar, QMessageBox

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

        self.showMessage("I am the status bar")  # TODO: save the version number somewhere


class ProgressBar(QProgressBar):

    def __init__(self, parent=None):
        """Constructor."""

        super(ProgressBar, self).__init__(parent)


class AboutBox(QMessageBox):

    def __init__(self, parent=None):
        """Constructor."""

        super(AboutBox, self).__init__(parent)

        # Set icon
        icon_name = ""
        if sys.platform == "win32":
            icon_name = MainView.app_icon + ".ico"

        elif sys.platform == "darwin":
            icon_name = MainView.app_icon + ".icns"
            print("Macos")

        self.setIconPixmap(QPixmap("icons:about-small.png"))
        # self.setIconPixmap(QPixmap(icon_name))

        # test_icon = QMessageBox.Cancel
        # test_icon.size()


        self.setWindowTitle("About ColourPaletteExtractor")
        self.setText("ColourPaletteExtractor is a simple tool to generate the colour palette of an image.")
        self.setInformativeText("Version 0.1")  # TODO: Get this from elsewhere

        # Show about box
        self.exec_()




