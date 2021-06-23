# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import sys

from PySide2.QtWidgets import QApplication

from view import mainview
from controller import controller
from model import model


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# Create model
model = model.ColourPaletteExtractorModel()

# Creating instance of QApplication
app = QApplication(sys.argv)

# Create view
view = mainview.MainView()

# Create controller
controller = controller.ColourPaletteExtractorController(model=model, view=view)

# Show application's GUI
view.show()

# Run application's event loop (or main loop)
sys.exit(app.exec_())
