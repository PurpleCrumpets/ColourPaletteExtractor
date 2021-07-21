import time
from functools import partial  # Import partial to connect signals with methods that need to take extra arguments
from PySide2.QtCore import QFileInfo, QRunnable, QThreadPool
from PySide2.QtWidgets import QErrorMessage, QMessageBox

from colourpaletteextractor.controller.worker import ColourPaletteWorker, ReportGeneratorWorker
from colourpaletteextractor.model import generatereport
from colourpaletteextractor.model.imagedata import ImageData
from colourpaletteextractor.model.model import ColourPaletteExtractorModel, get_settings
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

        # Signal creation of instructions tab
        self._create_default_tab()

    def _connect_preferences_signals(self):
        self._view.preferences.reset_preferences_button.clicked.connect(self._reset_preferences)
        self._connect_algorithm_selector_signals()
        self._connect_output_directory_selector_signals()


    def _reset_preferences(self):
        self._model.write_default_settings()  # Update settings file
        self._view.preferences.update_preferences()
        # Update preferences panel


    def _connect_algorithm_selector_signals(self) -> None:
        algorithms, algorithm_buttons = self._view.preferences.get_algorithms_and_buttons()

        # Connecting each radio button to the correct command
        for algorithm, algorithm_button in zip(algorithms, algorithm_buttons):
            algorithm_button.clicked.connect(partial(self._set_algorithm, algorithm))

    def _connect_output_directory_selector_signals(self) -> None:

        # TODO:
        # Get default path as string
        # create fake button for updating the paths
        # get info from text box

        self._view.preferences.default_path_button.clicked.connect(partial(self._set_output_path, use_user_dir=False))
        self._view.preferences.user_path_button.clicked.connect(partial(self._set_output_path, use_user_dir=True))
        self._view.preferences.browse_button.clicked.connect(self._get_output_path)

    def _get_output_path(self):
        current_path = self._view.preferences.user_path_selector.text()
        new_path = self._view.preferences.show_output_directory_dialog_box(current_path=current_path)

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
        self._view.tabs.tabBarDoubleClicked.connect(self._view.tab_open_doubleclick)
        self._view.tabs.currentChanged.connect(self.current_tab_changed)
        self._view.tabs.tabCloseRequested.connect(self._close_current_tab)

        # About event
        self._view.about_menu_action.triggered.connect(otherviews.AboutBox)
        self._view.about_action.triggered.connect(otherviews.AboutBox)

        # Open event
        self._view.open_action.triggered.connect(self._open_file)

        # Generate report event
        self._view.generate_report_action.triggered.connect(partial(self._generate_report_worker, None))
        self._view.generate_all_report_action.triggered.connect(self._generate_all_reports)

        # Generate colour palette event
        self._view.generate_palette_action.triggered.connect(partial(self._generate_colour_palette_worker, None))
        self._view.generate_all_palette_action.triggered.connect(self._generate_all_palettes)

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

        # Save event
        # self._view.save_action.triggered.connect(self._save_file)

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
        new_image_data.name = "How to Extract the Colour Palette"

        # Create new tab linked to the image
        if new_image_data is not None:
            self._create_new_tab(image_data_id=new_image_data_id, new_image_data=new_image_data)
            # TODO: This is effectively cheating...

    def _create_new_tab(self, image_data_id: str, new_image_data: ImageData) -> None:
        self._view.create_new_tab(image_id=image_data_id, image_data=new_image_data)

    def _close_current_tab(self, tab_index: int) -> None:

        # Remove image_data from dictionary in model
        image_data_id = self._view.tabs.currentWidget().image_id
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

    # def _save_file(self) -> None:
    #     """Save palette and image together."""
    #     print("Not implemented")

    def _update_progress_bar(self, tab: NewTab, percent: int) -> None:
        # Update progress status value
        tab.progress_bar_value = percent

        # Update progress bar on GUI
        if tab == self._view.tabs.currentWidget():
            self._view.status.update_progress_bar(percent)
            self._update_status_bar(tab)

            if percent == 0 or percent == 100:  # Start and end of progress - refresh the GUI
                self.current_tab_changed(-2)
            # if percent == 100:
            #     self._view.status.set_status_bar(2)

    def _generate_all_reports(self) -> None:

        # TODO: Temporarily disable generate all palettes action

        num_tabs = self._view.tabs.count()
        for i in range(num_tabs):
            tab = self._view.tabs.widget(i)

            # Check if tab has the necessary details to create a report
            count = 0
            if tab.generate_report_available:
                count += 1
                self._generate_report_worker(tab)

            if count == 0:
                # Letting the user know that they must generate colour palettes first before generating a report
                message = "You need to generate the colour palette for at least one image " \
                          + "before you can generate a report!"
                msg_box = otherviews.ErrorBox(box_type="information")
                msg_box.setInformativeText(message)
                msg_box.exec_()

        # TODO: Re-enable generate all palettes action

    def _generate_report_worker(self, tab: NewTab = None) -> None:

        worker = ReportGeneratorWorker(self._generate_report, tab=tab)  # Execute main function
        worker.signals.finished.connect(self.current_tab_changed)  # Function called at the very end
        worker.signals.progress.connect(self._update_progress_bar)  # Intermediate Progress

        QThreadPool.globalInstance().start(worker)
        print("Started worker to generate report...")

    def _generate_report(self, tab, progress_callback):
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

    def _generate_all_palettes(self) -> None:

        # TODO: Temporarily disable then enable generate all palettes action
        #  probably need to wait until all processes have finished - is this possible?

        num_tabs = self._view.tabs.count()
        for i in range(num_tabs):
            tab = self._view.tabs.widget(i)
            self._generate_colour_palette_worker(tab)

    def _generate_colour_palette_worker(self, tab: NewTab = None) -> None:
        worker = ColourPaletteWorker(self._generate_colour_palette, tab=tab)  # Execute main function

        # Connecting signals
        # worker.signals.result.connect(self._update_tab)  # Uses the result of the main function
        worker.signals.finished.connect(self.current_tab_changed)  # Function called at the very end
        worker.signals.progress.connect(self._update_progress_bar)  # Intermediate Progress
        QThreadPool.globalInstance().start(worker)
        # self._thread_pool.start(worker)
        print("Started worker to generate colour palette...")

        # TODO: add cancel button?

    def _generate_colour_palette(self, tab, progress_callback):
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

        # Update tab properties and refresh tab
        self._toggle_tab_button_states(tab=tab, activate=True)  # Re-enable buttons for the tab
        tab.status_bar_state = 2  # Tab status to colour palette generated
        progress_callback.emit(tab, 100)  # Update GUI

        # TODO: add try block for status bar updates in case of failure

        # Add colour palette to the GUI representation of the colour palette
        # image_data = self._model.get_image_data(image_id)
        # colour_palette = image_data.colour_palette
        # return colour_palette, image_id

    @staticmethod
    def _toggle_tab_button_states(tab: NewTab, activate: bool):
        """Turns off/on the three main buttons on the GUI that should not be interacted with
        when the particular tab is doing something."""

        tab.generate_palette_available = activate  # Palette generation
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
        image_data = self._model.get_image_data(image_data_id)

        return image_data.colour_palette

    def _get_relative_frequencies(self, tab):

        image_data_id = tab.image_id
        image_data = self._model.get_image_data(image_data_id)

        return image_data.colour_palette_relative_frequency

    def current_tab_changed(self, i):
        """Update current tab index."""
        print("Tab changed to:", i)

        # Create new default tab if all have been removed
        if i == -1:
            self._create_default_tab()

        # Enable/disable toggle button for displaying recoloured image
        tab = self._view.tabs.currentWidget()
        image_id = tab.image_id
        self._update_state_of_tab_buttons(tab=tab)


        # Reload colour palette
        colour_palette = self._get_colour_palette(tab)
        relative_frequencies = self._get_relative_frequencies(tab)

        if len(colour_palette) == 0:
            print("There is no colour palette")
            self._view.colour_palette_dock.remove_colour_palette()  # Reset colour palette dock
        else:
            self._view.colour_palette_dock.add_colour_palette(colour_palette, image_id, relative_frequencies)


        # Update status bar
        self._update_status_bar(tab)


        # TODO: more things may need to change (ie highlight show map to show that it is on for that image)

    def _update_state_of_tab_buttons(self, tab: NewTab):
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

        # Load colour palette report generation button state (available/not available)
        if tab.generate_report_available:
            self._view.generate_report_action.setDisabled(False)
        else:
            self._view.generate_report_action.setDisabled(True)

    def _update_status_bar(self, tab: NewTab):
        status_bar_state = tab.status_bar_state
        self._view.status.set_status_bar(status_bar_state)
        percent = tab.progress_bar_value
        self._view.status.update_progress_bar(percent)



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
