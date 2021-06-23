# Import partial to conect signals with methods that need to take extra arguments
from functools import partial

from PySide6.QtWidgets import QFileDialog

from colourpaletteextractor.model import model as md


class ColourPaletteExtractorController:
    """Colour Palette Extractor Controller Class."""

    def __init__(self, model, view):
        """Initialise controller."""
        self._view = view
        self._model = model

        # Connect signals and slots
        self._connect_signals()

    def _calculate_result(self):
        """Evaluate expressions."""
        result = self._model.evaluate_expression(self._view.display_text())
        self._view.set_display_text(result)


    def _build_expression(self, sub_exp):
        """Build expression."""
        if self._view.display_text() == md.ColourPaletteExtractorModel.ERROR_MSG:
            self._view.clear_display()

        _expression = self._view.display_text() + sub_exp
        self._view.set_display_text(_expression)

    def _connect_signals(self):
        """Connect signals and slots."""

        # Buttons
        # for btn_text, btn in self._view.buttons.items():
        #     if btn_text not in {"=", "C"}:
        #         btn.clicked.connect(partial(self._build_expression, btn_text))
        #
        # self._view.buttons["="].clicked.connect(self._calculate_result)
        # self._view.display.returnPressed.connect(self._calculate_result)
        # self._view.buttons['C'].clicked.connect(self._view.clear_display)

        # Tabs
        self._view.tabs.tabBarDoubleClicked.connect(self._view.tab_open_doubleclick)
        self._view.tabs.currentChanged.connect(self._view.current_tab_changed)
        self._view.tabs.tabCloseRequested.connect(self._view.close_current_tab)


        # Menu items
        self._view.open_action.triggered.connect(self._open_file)
        self._view.save_action.triggered.connect(self._save_file)

    def _open_file(self):
        """Add new image."""
        supported_files = self._model.supported_image_types
        file_name, _ = self._view.show_file_dialog_box(supported_files)
        new_image_data = None
        if file_name != "":
            new_image_data = self._model.add_image(file_name)
        else:
            print("No image selected")

        if new_image_data is not None:
            # Create new tab linked to image
            self._view.create_new_tab(new_image_data)





    def _save_file(self):
        """Save palette and image together."""
        print("Not implemented")