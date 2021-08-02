# ColourPaletteExtractor is a simple tool to generate the colour palette of an image.
# Copyright (C) 2021  Tim Churchfield
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import sys
from pathlib import Path

import darkdetect
from PySide2.QtCore import Qt, QThreadPool
from PySide2.QtWidgets import QApplication

import qtmodern.styles
import qtmodern.windows

from colourpaletteextractor import _settings
from colourpaletteextractor.view import mainview
from colourpaletteextractor.controller import controller
from colourpaletteextractor.model import model


if __name__ == '__main__':
    """Run an instance of the ColourPaletteExtractor application."""

    print("***************************************************************************************")
    if _settings.__VERBOSE__:
        print("The verbose output to the terminal during the generation of the colour palette and the \n" +
              "colour palette report can be turned off by changing the '__VERBOSE__' variable in \n"
              + "the '_version.py' module from 'True' to 'False'...")
    else:
        print("Verbose output to the terminal during the generation of the colour palette and the \n" +
              "colour palette report can be turned on by changing the '__VERBOSE__' variable in \n"
              + "the '_version.py' module from 'False' to 'True'...")
    print("***************************************************************************************\n")

    print("Opening ColourPaletteExtractor application...")
    print("Multithreading enabled with maximum %d threads..." % QThreadPool.globalInstance().maxThreadCount())

    # Setting path to style sheet
    root = Path()
    if getattr(sys, 'frozen', False):
        root = Path(sys._MEIPASS)
        qtmodern.styles._STYLESHEET = root / 'qtmodern/style.qss'
        qtmodern.windows._FL_STYLESHEET = root / 'qtmodern/frameless.qss'

    model = model.ColourPaletteExtractorModel()  # Model

    # Create instance of QApplication
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)  # Disable QDialog's question mark button

    view = mainview.MainView()  # View
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
