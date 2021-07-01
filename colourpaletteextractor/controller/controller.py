# Import partial to connect signals with methods that need to take extra arguments
from functools import partial
import time

from PySide2.QtCore import QDir, QFileInfo, QRunnable, Slot, QThreadPool
# from PySide2.QtWidgets import QFileDialog
from colourpaletteextractor.controller.worker import Worker
from colourpaletteextractor.model import model as md
from colourpaletteextractor.view import mainview as vw, otherviews


class ColourPaletteExtractorController(QRunnable):
    """Colour Palette Extractor Controller Class."""

    def __init__(self, model, view):
        """Initialise controller."""
        super().__init__()

        # Creating thread pool
        self._thread_pool = QThreadPool()
        print("Multithreading with maximum %d threads" % self._thread_pool.maxThreadCount())

        # Assigning model and view
        self._view = view
        self._model = model

        # Connect signals and slots
        self._connect_signals()

        # Signal creation of instructions tab
        self._create_default_tab()

    def _connect_signals(self):
        """Connect signals and slots."""

        # Tabs
        self._view.tabs.tabBarDoubleClicked.connect(self._view.tab_open_doubleclick)
        self._view.tabs.currentChanged.connect(self.current_tab_changed)
        self._view.tabs.tabCloseRequested.connect(self._close_current_tab)

        # Menu items
        self._view.open_action.triggered.connect(self._open_file)
        self._view.save_action.triggered.connect(self._save_file)
        self._view.generate_palette_action.triggered.connect(self._generate_colour_palette_worker)
        self._view.toggle_recoloured_image_action.triggered.connect(self._toggle_recoloured_image)

    def _create_default_tab(self):

        # Get the default image
        default_file = vw.MainView.default_new_tab_image
        default_file = QFileInfo(default_file).absoluteFilePath()

        # Add image to the model
        new_image_data_id, new_image_data = self._model.add_image(default_file)

        # Set name of default tab
        new_image_data.name = "How to Extract Colour Palette"

        # Create new tab linked to the image
        if new_image_data is not None:
            self._create_new_tab(new_image_data_id, new_image_data)
            # TODO: This is effectively cheating...

    def _close_current_tab(self, tab_index):

        # Remove image_data from dictionary in model
        image_data_id = self._view.tabs.currentWidget().image_id
        self._model.remove_image_data(image_data_id)

        # Close currently selected tab in GUI
        self._view.close_current_tab(tab_index)

    def _create_new_tab(self, new_image_data_id, new_image_data):
        self._view.create_new_tab(image_id=new_image_data_id, image_data=new_image_data)

    def _open_file(self):
        """Add new image."""

        supported_files = self._model.supported_image_types
        file_name, _ = self._view.show_file_dialog_box(supported_files)

        new_image_data_id = None
        new_image_data = None

        if file_name != "":
            new_image_data_id, new_image_data = self._model.add_image(file_name)
        else:
            print("No image selected")

        if new_image_data is not None:
            # Create new tab linked to the image
            self._create_new_tab(new_image_data_id=new_image_data_id, new_image_data=new_image_data)

    def _save_file(self):
        """Save palette and image together."""
        print("Not implemented")








    def _generate_colour_palette_worker(self):

        worker = Worker(self._generate_colour_palette, test="Worlds")  # Execute main function
        # worker.signals.result.connect(self.print_output)  # Uses the result of the main function
        worker.signals.finished.connect(self._update_colour_palette_of_gui)  # Function called at the very end
        # worker.signals.progress.connect(self.progress_fn)  # Intermediate Progress
        self._thread_pool.start(worker)

        # TODO: lock button to generate palette until after it has finished
        # TODO: add cancel button?


    def _update_colour_palette_of_gui(self, colour_palette, image_id):
        self._view.colour_palette_dock.add_colour_palette(colour_palette, image_id)

        # Check if toggle button for the recoloured image should be enabled for the current tab
        tab = self._view.tabs.currentWidget()
        current_image_id = tab.image_id

        if image_id == current_image_id:
            self._view.toggle_recoloured_image_action.setDisabled(False)

    def _generate_colour_palette(self, test, progress_callback=None):
        """Generate colour palette for current open image."""

        print(test)

        # Get image data for the current tab
        tab = self._view.tabs.currentWidget()
        image_id = tab.image_id

        # Generate colour palette
        self._model.generate_palette(image_id)

        # Enable toggle button for showing recoloured image for the tab
        tab.enable_toggle_recoloured_image()

        # Add colour palette to the GUI representation of the colour palette
        image_data = self._model.get_image_data(image_id)
        colour_palette = image_data.colour_palette

        return colour_palette, image_id

        # self._view.colour_palette_dock.add_colour_palette(colour_palette, image_id)
        # TODO: check tab matched before showing the colour palette ^



        # TODO: prevent instructions page from showing the colour palette

    def _toggle_recoloured_image(self):

        tab = self._view.tabs.currentWidget()
        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)

        # Selecting new image
        if image_data.show_original_image:
            image = image_data.recoloured_image
        else:
            image = image_data.image

        image_data.toggle_show_original_image()
        tab = self._view.tabs.currentWidget()
        tab.image_display.update_image(image)
        tab.change_toggle_recoloured_image_pressed()
        tab.update()

    def _get_colour_palette(self, tab):
        """Finds the image data associated with the given tab and returns its colour palette."""

        image_data_id = tab.image_id
        image_data = self._model.get_image_data(image_data_id)

        return image_data.colour_palette


    def current_tab_changed(self, i):
        """Update current tab index."""
        print("Tab changed to:", i)

        # Create new default tab if all have been removed
        if i == -1:
            self._create_default_tab()

        # Enable/disable toggle button for displaying recoloured image
        tab = self._view.tabs.currentWidget()
        image_id = tab.image_id
        if tab.toggle_recoloured_image:
            self._view.toggle_recoloured_image_action.setDisabled(False)
        else:
            self._view.toggle_recoloured_image_action.setDisabled(True)

        # Load toggle button state (pressed/not pressed) for tab
        if tab.toggle_recoloured_image_pressed:
            self._view.toggle_recoloured_image_action.setChecked(True)
        else:
            self._view.toggle_recoloured_image_action.setChecked(False)

        # Reload colour palette
        colour_palette = self._get_colour_palette(tab)
        self._view.colour_palette_dock.add_colour_palette(colour_palette, image_id)

        # TODO: more things may need to change (ie highlight show map to show that it is on for that image)


    # def _calculate_result(self):
    #     """Evaluate expressions."""
    #     result = self._model.evaluate_expression(self._view.display_text())
    #     self._view.set_display_text(result)
    #
    # def _build_expression(self, sub_exp):
    #     """Build expression."""
    #     if self._view.display_text() == md.ColourPaletteExtractorModel.ERROR_MSG:
    #         self._view.clear_display()
    #
    #     _expression = self._view.display_text() + sub_exp
    #     self._view.set_display_text(_expression)
