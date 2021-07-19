# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import sys
from pathlib import Path

import darkdetect
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication

import qtmodern.styles
import qtmodern.windows

from view import mainview
from controller import controller
from model import model


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


if __name__ == '__main__':
    print("Opening ColourPaletteExtractor application...")

    # Setting path to style sheet
    root = Path()
    if getattr(sys, 'frozen', False):
        root = Path(sys._MEIPASS)
        qtmodern.styles._STYLESHEET = root / 'qtmodern/style.qss'
        qtmodern.windows._FL_STYLESHEET = root / 'qtmodern/frameless.qss'

    model = model.ColourPaletteExtractorModel()  # Model
    temp_path = model.output_dir.name  # Initial default directory

    # Create instance of QApplication
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)  # Disable QDialog's question mark button
    # app.setStyle('Macintosh')

    view = mainview.MainView(temp_path=temp_path)  # View
    controller = controller.ColourPaletteExtractorController(model=model, view=view)  # Controller

    # Setting up dark mode for Windows applications
    if sys.platform == "win32":
        pass
        # Setting light mode/dark mode specifically for Windows
        if darkdetect.isDark():
            qtmodern.styles.dark(app)
        else:
            qtmodern.styles.light(app)

    # Show application's GUI
    view.show()

    # Run application's event loop (or main loop)
    sys.exit(app.exec_())

# class ModifiedModernWindow(qtmodern.windows.ModernWindow):
#
#     def __init__(self, w):
#
#         super(ModifiedModernWindow, self).__init__(w)
#
#         icon_name = MainView.app_icon + ".ico"
#         self.setWindowIcon(QIcon(icon_name))
