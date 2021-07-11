from PySide2.QtWidgets import QWidget, QProgressBar, \
    QStatusBar


__version__ = "0.1"
__author__ = "Tim Churchfield"


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
