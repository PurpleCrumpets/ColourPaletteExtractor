# Import partial to conect signals with methods that need to take extra arguments
# from functools import partial

from PySide2.QtCore import QDir, QFileInfo
# from PySide2.QtWidgets import QFileDialog

from colourpaletteextractor.model import model as md
from colourpaletteextractor.view import mainview as vw


class ColourPaletteExtractorController:
    """Colour Palette Extractor Controller Class."""

    def __init__(self, model, view):
        """Initialise controller."""
        self._view = view
        self._model = model

        # Connect signals and slots
        self._connect_signals()

        # Signal creation of instructions tab
        # self._open_file(True)
        self._create_default_tab()

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
        self._view.tabs.tabCloseRequested.connect(self._close_current_tab)

        # Menu items
        self._view.open_action.triggered.connect(self._open_file)
        self._view.save_action.triggered.connect(self._save_file)
        self._view.generate_palette_action.triggered.connect(self._generate_colour_palette)
        self._view.toggle_recoloured_image_action.triggered.connect(self._toggle_recoloured_image)

    def _create_default_tab(self):
        default_file = vw.MainView.default_new_tab_image
        default_file = QFileInfo(default_file).absoluteFilePath()
        new_image_data = self._model.add_image(default_file)

        if new_image_data is not None:
            # Create new tab linked to image
            self._view.create_new_tab()
            # TODO: This is effectively cheating...

    def _close_current_tab(self, i):

        # Remove image and resources from list save in model
        self._model.remove_image_data(i)

        # Close selected tab in GUI
        i = self._view.close_current_tab(i)

        # Create new default tab if all removed
        if i == -1:
            self._create_default_tab()


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

    def _generate_colour_palette(self):
        """Generate colour palette for current open image."""
        i = self._view.i
        self._model.generate_palette(i)

        # Enable toggle button for showing recoloured image
        tab = self._view.tabs.currentWidget()
        tab.enable_toggle_recoloured_image()
        self._view.toggle_recoloured_image_action.setDisabled(False)


        # TODO: prevent instructions page from showing the colour palette
        # Get image associated with selected tab
        # self._model

    def _toggle_recoloured_image(self):
        # TODO: grey button out until palette has been generated
        i = self._view.i

        image_data = self._model.images[i]

        if image_data.show_original_image:
            image = image_data.recoloured_image
        else:
            image = image_data.image

        image_data.toggle_show_original_image()
        tab = self._view.tabs.currentWidget()
        tab.image_display.update_image(image)
        tab.update()



