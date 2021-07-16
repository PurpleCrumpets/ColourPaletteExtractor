# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys
from pathlib import Path

import darkdetect
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPalette, QColor
from PySide2.QtWidgets import QApplication, QStyleFactory

import qtmodern.styles
import qtmodern.windows

from colourpaletteextractor.view.mainview import MainView
from view import mainview
from controller import controller
from model import model


root = Path()
if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
    qtmodern.styles._STYLESHEET = root / 'qtmodern/style.qss'
    qtmodern.windows._FL_STYLESHEET = root / 'qtmodern/frameless.qss'


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')


# class ModifiedModernWindow(qtmodern.windows.ModernWindow):
#
#     def __init__(self, w):
#
#         super(ModifiedModernWindow, self).__init__(w)
#
#         icon_name = MainView.app_icon + ".ico"
#         self.setWindowIcon(QIcon(icon_name))



# Create model
model = model.ColourPaletteExtractorModel()

# Create instance of QApplication
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DisableWindowContextHelpButton)  # Disable QDialog's question mark button
# app.setStyle('Macintosh')
# app.setStyle('Fusion')

# Create view
view = mainview.MainView()

# Create controller
controller = controller.ColourPaletteExtractorController(model=model, view=view)

# Show application's GUI
if sys.platform == "win32":
    pass
    # Setting light mode/dark mode specifically for Windows
    if darkdetect.isDark():
        qtmodern.styles.dark(app)
    else:
        qtmodern.styles.light(app)

view.show()

# Run application's event loop (or main loop)
sys.exit(app.exec_())
