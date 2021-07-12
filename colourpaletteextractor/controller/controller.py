# Import partial to connect signals with methods that need to take extra arguments
from functools import partial
import time

from PySide2.QtCore import QDir, QFileInfo, QRunnable, Slot, QThreadPool, QThread
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
        self._view.about_action.triggered.connect(self._about_box)
        self._view.open_action.triggered.connect(self._open_file)
        self._view.save_action.triggered.connect(self._save_file)
        self._view.generate_palette_action.triggered.connect(partial(self._generate_colour_palette_worker, None))
        self._view.generate_all_action.triggered.connect(self._generate_all_palettes)
        self._view.toggle_recoloured_image_action.triggered.connect(self._toggle_recoloured_image)

        # Reopen colour palette dock
        self._view.show_palette_dock_action.triggered.connect(self._show_colour_palette_dock)

        # Zooming in and out of image
        self._view.zoom_in_action.triggered.connect(self._zoom_in)
        self._view.zoom_out_action.triggered.connect(self._zoom_out)

        # Exit application
        self._view.exit_action.triggered.connect(self._close_app)

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

    def _show_colour_palette_dock(self):
        self._view.colour_palette_dock.show()

    def _zoom_in(self):
        tab = self._view.tabs.currentWidget()
        image_display = tab.image_display
        image_display.zoom_in()

    def _zoom_out(self):
        tab = self._view.tabs.currentWidget()
        image_display = tab.image_display
        image_display.zoom_out()

    def _about_box(self):
        otherviews.AboutBox()

    def _close_app(self):
        # TODO: add "do you wish to quit" dialog box here
        self._view.close()

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
        file_names, _ = self._view.show_file_dialog_box(supported_files)

        for file_name in file_names:

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

    def _generate_all_palettes(self):

        # TODO: Temporarily disable generate all palettes action


        num_tabs = self._view.tabs.count()
        for i in range(num_tabs):
            tab = self._view.tabs.widget(i)
            self._generate_colour_palette_worker(tab)

        # TODO: Re-enable generate all palettes action

    def _generate_colour_palette_worker(self, tab=None):

        if tab is None:
            worker = Worker(self._generate_colour_palette, tab=None)  # Execute main function
        else:
            worker = Worker(self._generate_colour_palette, tab=tab)  # Execute main function

        # worker.signals.result.connect(self._update_tab)  # Uses the result of the main function
        worker.signals.finished.connect(self.current_tab_changed)  # Function called at the very end
        worker.signals.progress.connect(self._update_progress_bar)  # Intermediate Progress
        self._thread_pool.start(worker)
        print("Started worker")

        # TODO: lock button to generate palette until after it has finished
        # TODO: add cancel button?

    def _update_progress_bar(self, tab, percent):
        # Update progress status value
        tab.progress_bar_value = percent

        # Update progress bar on GUI
        if tab == self._view.tabs.currentWidget():
            self._view.status.update_progress_bar(percent)

            if percent == 100:
                self._view.status.set_status_bar(2)

    def _reset_tab(self, tab):
        # Reset image data
        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)
        image_data.colour_palette = []  # Remove colour palette
        image_data.recoloured_image = None  # Removing recoloured image

        # Reset tab data
        tab.toggle_recoloured_image_available = False
        tab.toggle_recoloured_image_pressed = False
        image = image_data.image
        tab.image_display.update_image(image)

        # Refreshing tab
        self.current_tab_changed(-2)  # -2 does not correspond to any particular tab

    def _generate_colour_palette(self, tab, progress_callback):
        """Generate colour palette for current open image."""

        if tab is None:
            # Get image data for the current tab
            tab = self._view.tabs.currentWidget()

        # Temporarily disable palette generation action for given tab
        tab.generate_palette_available = False

        # Set image_data status bar state to generating colour palette
        tab.status_bar_state = 1

        # Reset state of tab
        self._reset_tab(tab)

        progress_callback.emit(tab, 0)

        # Generate colour palette
        image_id = tab.image_id
        self._model.generate_palette(image_id, tab, progress_callback)

        # Set image_data status bar state to colour palette generated
        tab.status_bar_state = 2

        # TODO: add try block for status bar updates in case of failure

        # Enable toggle button for showing recoloured image for the tab
        tab.toggle_recoloured_image_available = True

        # Re-enable palette generation button for the given tab
        tab.generate_palette_available = True

        # Add colour palette to the GUI representation of the colour palette
        image_data = self._model.get_image_data(image_id)
        colour_palette = image_data.colour_palette

        # TODO: prevent instructions page from showing the colour palette
        # return colour_palette, image_id

    def _toggle_recoloured_image(self):

        tab = self._view.tabs.currentWidget()

        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)

        # Selecting new image
        if tab.toggle_recoloured_image_available and not tab.toggle_recoloured_image_pressed:
            print("Showing recoloured image")
            image = image_data.recoloured_image
        else:
            image = image_data.image

        tab.image_display.update_image(image)
        tab.change_toggle_recoloured_image_pressed()
        tab.update()  # TODO: Not sure this is necessary?

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
        if tab.toggle_recoloured_image_available:
            self._view.toggle_recoloured_image_action.setDisabled(False)
        else:
            self._view.toggle_recoloured_image_action.setDisabled(True)

        # Load toggle button state (pressed/not pressed) for tab
        if tab.toggle_recoloured_image_pressed:
            self._view.toggle_recoloured_image_action.setChecked(True)
        else:
            self._view.toggle_recoloured_image_action.setChecked(False)

        # Load colour palette generation button state (available/not available)
        if tab.generate_palette_available:
            self._view.generate_palette_action.setDisabled(False)
        else:
            self._view.generate_palette_action.setDisabled(True)

        # Reload colour palette
        colour_palette = self._get_colour_palette(tab)

        if len(colour_palette) == 0:
            self._view.colour_palette_dock.remove_colour_palette()  # Reset colour palette dock
        else:
            self._view.colour_palette_dock.add_colour_palette(colour_palette, image_id)

        # Update status bar
        status_bar_state = tab.status_bar_state
        self._view.status.set_status_bar(status_bar_state)
        percent = tab.progress_bar_value
        self._view.status.update_progress_bar(percent)

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
