from __future__ import annotations
from functools import partial  # Import partial to connect signals with methods that need to take extra arguments

from PySide2 import QtCore
from PySide2.QtCore import QFileInfo, QRunnable, QThreadPool


from colourpaletteextractor.controller.worker import Worker
from colourpaletteextractor.model import generatereport
from colourpaletteextractor.model.imagedata import ImageData
from colourpaletteextractor.model.model import ColourPaletteExtractorModel
from colourpaletteextractor.view import mainview as vw, otherviews
from colourpaletteextractor.view.mainview import MainView
from colourpaletteextractor.view.tabview import NewTab


class ColourPaletteExtractorController(QRunnable):
    """Colour Palette Extractor Controller Class."""

    def __init__(self, model: ColourPaletteExtractorModel, view: MainView) -> None:
        """Constructor."""
        super().__init__()

        # Assigning model and view
        self._view = view
        self._model = model

        # Connect signals and slots
        self._connect_main_window_signals()
        self._connect_preferences_signals()
        self._connect_batch_progress_signals()

        # Signal creation of instructions tab
        self._create_default_tab()

    def _connect_preferences_signals(self):
        self._view.preferences.reset_preferences_button.clicked.connect(self._reset_preferences)
        self._connect_algorithm_selector_signals()
        self._connect_output_directory_selector_signals()

    def _connect_batch_progress_signals(self):
        self._view.batch_progress_widget.cancel_batch_button.clicked.connect(self._send_stop_signals_to_batch_threads)

    def _send_stop_signals_to_batch_threads(self):
        self._view.batch_progress_widget.set_cancel_text()

        for image_data_id, image_data in self._model.image_data_id_dictionary.items():
            image_data.continue_thread = False

    def _reset_preferences(self):
        self._model.write_default_settings()  # Update settings file
        self._view.preferences.update_preferences()  # Update preferences panel

    def _connect_algorithm_selector_signals(self) -> None:
        algorithms, algorithm_buttons = self._view.preferences.get_algorithms_and_buttons()

        # Connecting each radio button to the correct command
        for algorithm, algorithm_button in zip(algorithms, algorithm_buttons):
            algorithm_button.clicked.connect(partial(self._set_algorithm, algorithm))

    def _connect_output_directory_selector_signals(self) -> None:
        self._view.preferences.default_path_button.clicked.connect(partial(self._set_output_path, use_user_dir=False))
        self._view.preferences.user_path_button.clicked.connect(partial(self._set_output_path, use_user_dir=True))
        self._view.preferences.browse_button.clicked.connect(self._get_output_path)

    def _get_output_path(self):
        current_path = self._view.preferences.user_path_selector.text()
        new_path = self._view.preferences.show_output_directory_dialog_box(current_path=current_path)

        if new_path != "":
            # Set new path
            self._view.preferences.user_path_selector.setText(new_path)
            self._model.change_output_directory(use_user_dir=True, new_user_directory=new_path)

    def _set_output_path(self, use_user_dir: bool) -> None:
        # if use_user_dir:
        new_user_directory = self._view.preferences.user_path_selector.text()
        print(new_user_directory)
        self._model.change_output_directory(use_user_dir=use_user_dir, new_user_directory=new_user_directory)

        # Update GUI
        self._view.preferences.user_path_selector.setEnabled(use_user_dir)
        self._view.preferences.browse_button.setEnabled(use_user_dir)

    def _set_algorithm(self, algorithm) -> None:
        self._model.set_algorithm(algorithm)

    def _connect_main_window_signals(self) -> None:
        """

        :return:
        """

        # Close event
        self._view.close_action.triggered.connect(self._close_application)

        # Tab events
        self._view.tabs.currentChanged.connect(self.current_tab_changed)
        self._view.tabs.tabCloseRequested.connect(self._close_current_tab)

        # About event
        self._view.about_menu_action.triggered.connect(otherviews.AboutBox)
        self._view.about_action.triggered.connect(otherviews.AboutBox)

        # Open event
        self._view.open_action.triggered.connect(self._open_file)

        # Generate report event
        self._view.generate_report_action.triggered.connect(partial(self._generate_worker, "report"))
        self._view.generate_all_report_action.triggered.connect(partial(self._generate_all, "report"))

        # Generate colour palette event
        self._view.generate_palette_action.triggered.connect(partial(self._generate_worker, "colour palette"))
        self._view.generate_all_palette_action.triggered.connect(partial(self._generate_all, "colour palette"))

        # Toggle recoloured image event
        self._view.toggle_recoloured_image_action.triggered.connect(self._toggle_recoloured_image)

        # Reopen toolbar and colour palette dock event
        self._view.show_toolbar_action.triggered.connect(self._view.tools.show)
        self._view.show_palette_dock_action.triggered.connect(self._view.colour_palette_dock.show)

        # Zooming in and out of image events
        self._view.zoom_in_action.triggered.connect(self._zoom_in)
        self._view.zoom_out_action.triggered.connect(self._zoom_out)

        # Preferences event
        self._view.preferences_menu_action.triggered.connect(self._view.preferences.show_preferences)
        self._view.preferences_action.triggered.connect(self._view.preferences.show_preferences)

        # Help event
        self._view.show_help_menu_action.triggered.connect(self._create_default_tab)
        self._view.show_help_action.triggered.connect(self._create_default_tab)

        # Stop event
        self._view.stop_action.triggered.connect(self._stop_current_thread)

    def _stop_current_thread(self):
        tab = self._view.tabs.currentWidget()

        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)
        image_data.continue_thread = False

    def _close_application(self):
        print("Removing temporary directory and its contents before closing application...")
        self._model.close_temporary_directory()

    def _zoom_in(self) -> None:
        tab = self._view.tabs.currentWidget()
        image_display = tab.image_display
        image_display.zoom_in()

    def _zoom_out(self) -> None:
        tab = self._view.tabs.currentWidget()
        image_display = tab.image_display
        image_display.zoom_out()

    def _create_default_tab(self) -> None:

        # Get the default image
        default_file = vw.MainView.default_new_tab_image
        default_file = QFileInfo(default_file).absoluteFilePath()

        # Add image to the model
        new_image_data_id, new_image_data = self._model.add_image(file_name_and_path=default_file)

        # Set the name of the default tab
        new_image_data.name = "Quick Start Guide"

        # Create new tab linked to the image
        if new_image_data is not None:
            self._create_new_tab(image_data_id=new_image_data_id, new_image_data=new_image_data)
            # TODO: This is effectively cheating...

    def _create_new_tab(self, image_data_id: str, new_image_data: ImageData) -> None:
        self._view.create_new_tab(image_id=image_data_id, image_data=new_image_data)

    def _close_current_tab(self, tab_index: int) -> None:

        # Get image data
        image_data_id = self._view.tabs.currentWidget().image_id
        image_data = self._model.get_image_data(image_data_id)

        image_data.continue_thread = False

        # Remove image_data from dictionary in model
        self._model.remove_image_data(image_data_id)

        # Close currently selected tab in GUI
        self._view.close_current_tab(tab_index)

    def _open_file(self) -> None:
        """Add new image."""

        supported_files = self._model.SUPPORTED_IMAGE_TYPES
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
                self._create_new_tab(new_image_data_id, new_image_data)

    def _update_progress_bar(self, tab: NewTab, percent: int):
        # Update progress status value
        tab.progress_bar_value = percent

        # Update progress bar on GUI
        if tab == self._view.tabs.currentWidget():
            self._view.status.update_progress_bar(percent)
            self._update_status_bar(tab)

            if percent == 0 or percent == 100:  # Start and end of progress - refresh the GUI

                if tab.status_bar_state == 1:
                    self.current_tab_changed(-2)
                else:
                    self.current_tab_changed(-3)



    def _generate_all(self, batch_type: str):

        # Disable batch actions
        self._view.generate_all_report_action.setDisabled(True)
        self._view.generate_all_palette_action.setDisabled(True)
        self._view.preferences_action.setDisabled(True)  # TODO: this does not disable preferences in the main menu for mac

        num_tabs = self._view.tabs.count()

        # Update model thread counter
        self._model.active_thread_counter = num_tabs

        # Generate worker for each tab
        for i in range(num_tabs):
            tab = self._view.tabs.widget(i)

            if batch_type == "colour palette":
                self._generate_worker(main_function="colour palette", tab=tab, batch_generation=True)

            elif batch_type == "report":

                # Check if tab has the necessary details to create a report
                count = 0
                if tab.generate_report_available:
                    count += 1
                    self._generate_worker(main_function="report", tab=tab, batch_generation=True)

                if count == 0:
                    # Letting the user know that they must generate colour palettes first before generating a report
                    message = "You need to generate the colour palette for at least one image " \
                              + "before you can generate a report!"
                    msg_box = otherviews.ErrorBox(box_type="information")
                    msg_box.setInformativeText(message)
                    msg_box.exec_()
                    return
            else:
                pass
                # TODO: throw exception

        # Show overall progress widget
        self._view.batch_progress_widget.show_widget(total_count=num_tabs, batch_type=batch_type)

    def _generate_worker(self, main_function: str, tab: NewTab = None, batch_generation: bool = False) -> None:

        # Get image data
        if tab is None:
            tab = self._view.tabs.currentWidget()
        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)


        # Select primary function
        worker = None
        if main_function == "colour palette":
            worker = Worker(self._generate_colour_palette, image_data=image_data, function_type=main_function, tab=tab)

        elif main_function == "report":
            worker = Worker(self._generate_report, image_data=image_data, function_type=main_function, tab=tab)
        else:
            pass
            # TODO: throw exception

        self._connect_worker_signals(worker=worker, batch_generation=batch_generation)
        QThreadPool.globalInstance().start(worker)

    def _connect_worker_signals(self, worker: Worker, batch_generation: bool):
        # Connect signals
        if batch_generation:
            worker.signals.finished.connect(self._finish_generation)  # Function called at the very end
        else:
            worker.signals.finished.connect(self.current_tab_changed)  # Function called at the very end

        # worker.signals.result.connect(self._update_tab)  # Uses the result of the main function
        worker.signals.progress.connect(self._update_progress_bar)  # Intermediate Progress

    def _finish_generation(self, i: int) -> None:

        self._view.batch_progress_widget.update_progress()


        self._model.active_thread_counter -= 1

        self.current_tab_changed(i=i)

        if self._model.active_thread_counter == 0:
            self._view.batch_progress_widget.close()

            # Re-enable batch actions
            self._view.generate_all_report_action.setEnabled(True)
            self._view.generate_all_palette_action.setEnabled(True)
            self._view.preferences_action.setEnabled(True)

    def _generate_report(self, tab, progress_callback: QtCore.SignalInstance):
        print("Generating report...")

        if tab is None:
            tab = self._view.tabs.currentWidget()

        # Get image data
        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)

        # Update tab properties and refresh GUI
        self._toggle_tab_button_states(tab=tab, activate=False)  # Disable buttons for the given tab
        tab.status_bar_state = 3  # Tab status to generating colour palette report
        progress_callback.emit(tab, 0)

        # Generate report
        generatereport.generate_report(tab=tab,
                                       image_data=image_data,
                                       progress_callback=progress_callback)

        # Update tab properties and refresh tab
        self._toggle_tab_button_states(tab=tab, activate=True)  # Re-enable buttons for the given tab
        tab.status_bar_state = 2  # Tab status to colour palette generated
        progress_callback.emit(tab, 100)

    def _generate_colour_palette(self, tab, progress_callback: QtCore.SignalInstance):
        """Generate colour palette for current open image."""

        if tab is None:
            # Get image data for the current tab
            tab = self._view.tabs.currentWidget()

        # Update tab properties and refresh GUI
        self._toggle_tab_button_states(tab=tab, activate=False)  # Disable buttons for the given tab
        tab.status_bar_state = 1  # Set tab status to generating colour palette
        self._reset_tab_image_properties(tab=tab)  # Remove recoloured image and colour palette
        progress_callback.emit(tab, 0)  # Update GUI

        # Generate colour palette
        image_id = tab.image_id
        self._model.generate_palette(image_id, tab, progress_callback)

        # Update tab properties and refresh tab if it still exists
        if image_id in self._model.image_data_id_dictionary:
            recoloured_image = self._model.get_image_data(image_id).recoloured_image
            if recoloured_image is None:
                palette_generated = False
                tab.status_bar_state = 0  # Colour palette ws not generated
            else:
                palette_generated = True
                tab.status_bar_state = 2  # Tab status to colour palette generated
            self._toggle_tab_button_states(tab=tab, activate=True, palette_generated=palette_generated)  # Re-enable buttons for the tab

            progress_callback.emit(tab, 100)  # Update GUI

        # TODO: add try block for status bar updates in case of failure

        # Add colour palette to the GUI representation of the colour palette
        # image_data = self._model.get_image_data(image_id)
        # colour_palette = image_data.colour_palette
        # return colour_palette, image_id

    @staticmethod
    def _toggle_tab_button_states(tab: NewTab, activate: bool, palette_generated: bool = True):
        """Turns off/on the three main buttons on the GUI that should not be interacted with
        when the particular tab is doing something."""

        tab.generate_palette_available = activate  # Palette generation

        if palette_generated:
            tab.toggle_recoloured_image_available = activate  # Toggle button for showing recoloured image
            tab.generate_report_available = activate  # Report generation


    def _reset_tab_image_properties(self, tab: NewTab) -> None:

        # Reset image data
        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)
        image_data.colour_palette = []  # Remove colour palette
        image_data.recoloured_image = None  # Removing recoloured image

        # Reset tab data
        image = image_data.image
        tab.image_display.update_image(image)

        # Reset tab buttons
        tab.toggle_recoloured_image_available = False
        tab.toggle_recoloured_image_pressed = False


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
        # TODO can occasionally get an error here - not sure why

        image_data = self._model.get_image_data(image_data_id)

        if image_data is None:
            return []
        else:
            return image_data.colour_palette

    def _get_relative_frequencies(self, tab):

        image_data_id = tab.image_id
        image_data = self._model.get_image_data(image_data_id)

        return image_data.colour_palette_relative_frequency

    def current_tab_changed(self, i):
        """Update current tab index."""
        print("Tab changed to:", i)

        # if i is -2 - dummy change
        # Create new default tab if all have been removed
        if i == -1:
            self._create_default_tab()

        # Enable/disable toggle button for displaying recoloured image
        tab = self._view.tabs.currentWidget()
        image_id = tab.image_id
        self._update_state_of_tab_buttons(tab=tab)

        # Reload colour palette
        if i != -3:  # This prevents the GUI from flickering when updating the colour palette needlessly
            colour_palette = self._get_colour_palette(tab)
            relative_frequencies = self._get_relative_frequencies(tab)

            if len(colour_palette) == 0:
                self._view.colour_palette_dock.remove_colour_palette()  # Reset colour palette dock
            else:
                self._view.colour_palette_dock.add_colour_palette(colour_palette, image_id, relative_frequencies)

        # Update status bar
        self._update_status_bar(tab)

    def _update_state_of_tab_buttons(self, tab: NewTab):
        if tab.toggle_recoloured_image_available:
            self._view.toggle_recoloured_image_action.setEnabled(True)
        else:
            self._view.toggle_recoloured_image_action.setDisabled(True)

        # Load toggle button state (pressed/not pressed) for tab
        if tab.toggle_recoloured_image_pressed:
            self._view.toggle_recoloured_image_action.setChecked(True)
        else:
            self._view.toggle_recoloured_image_action.setChecked(False)

        # Load colour palette generation button state (available/not available)
        if tab.generate_palette_available:
            self._view.generate_palette_action.setEnabled(True)
            self._view.stop_action.setDisabled(True)
        else:
            self._view.generate_palette_action.setDisabled(True)
            self._view.stop_action.setEnabled(True)

        # Load colour palette report generation button state (available/not available)
        if tab.generate_report_available:
            self._view.generate_report_action.setEnabled(True)
        else:
            self._view.generate_report_action.setDisabled(True)

    def _update_status_bar(self, tab: NewTab):
        status_bar_state = tab.status_bar_state
        self._view.status.set_status_bar(status_bar_state)
        percent = tab.progress_bar_value
        self._view.status.update_progress_bar(percent)
