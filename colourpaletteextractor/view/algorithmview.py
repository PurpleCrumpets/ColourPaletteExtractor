from PySide6.QtWidgets import QFileDialog, QWidget

__version__ = "0.1"
__author__ = "Tim Churchfield"


class AlgorithmDialogBox(QWidget):

    def __init__(self, parent=None):
        """Initializer."""

        super(AlgorithmDialogBox, self).__init__(parent)

    # def file_dialog(directory="", for_open=True, fmt="", is_folder=False):
    #     options = QFileDialog.Options()
