import time
from functools import partial  # Import partial to connect signals with methods that need to take extra arguments
from PySide2.QtCore import QFileInfo, QRunnable, QThreadPool
from PySide2.QtWidgets import QErrorMessage, QMessageBox

from colourpaletteextractor.controller.worker import ColourPaletteWorker, ReportGeneratorWorker
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

        # Creating thread pool
        self._thread_pool = QThreadPool()
        print("Multithreading with maximum %d threads" % self._thread_pool.maxThreadCount())

        # Assigning model and view
        self._view = view
        self._model = model

        # Connect signals and slots
        self._connect_signals()
        self._connect_algorithm_selector_signals()
        self._connect_output_directory_selector_signals()

        # Signal creation of instructions tab
        self._create_default_tab()

    def _connect_algorithm_selector_signals(self) -> None:
        algorithms, algorithm_buttons = self._view.preferences.get_algorithms_and_buttons()

        # Connecting each radio button to the correct command
        for algorithm, algorithm_button in zip(algorithms, algorithm_buttons):
            algorithm_button.toggled.connect(partial(self._set_algorithm, algorithm))

    def _connect_output_directory_selector_signals(self) -> None:
        pass

    def _set_algorithm(self, algorithm, pressed_status=None) -> None:
        self._model.set_algorithm(algorithm)

    def _connect_signals(self) -> None:
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
        self._view.save_action.triggered.connect(self._save_file)

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
                self._create_new_tab(new_image_data_id, new_image_data)

    def _save_file(self) -> None:
        """Save palette and image together."""
        print("Not implemented")

    def _update_progress_bar(self, tab: NewTab, percent: int) -> None:
        # Update progress status value
        tab.progress_bar_value = percent

        # Update progress bar on GUI
        if tab == self._view.tabs.currentWidget():
            self._view.status.update_progress_bar(percent)
            self._update_status_bar(tab)

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

        self._thread_pool.start(worker)
        print("Started worker to generate report...")

    def _generate_report(self, tab, progress_callback):
        print("Generating report...")

        if tab is None:
            tab = self._view.tabs.currentWidget()

        # Get image data
        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)

        # Temporarily disable buttons for the given tab
        self._toggle_tab_button_states(tab=tab, activate=False)

        # Set tab status bar state to generating colour palette report
        tab.status_bar_state = 3

        # Update state of tab buttons
        if self._view.tabs.currentWidget() == tab:
            self._update_state_of_tab_buttons(tab)

        # Refresh tab # TODO: why does this break everything??
        # self._reset_tab(tab=tab, remove_data=False)
        # self.current_tab_changed(-2)  # -2 does not correspond to any particular tab

        # Get temporary directory to store results
        temp_dir = self._model.get_temp_dir_path()

        # Generate report
        generatereport.generate_report(directory=temp_dir,
                                       tab=tab,
                                       image_data=image_data,
                                       progress_callback=progress_callback)

        # Set image_data status bar state to colour palette generated
        tab.status_bar_state = 2

        # Re-enable buttons for the given tab
        self._toggle_tab_button_states(tab=tab, activate=True)

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
        self._thread_pool.start(worker)
        print("Started worker to generate colour palette...")

        # TODO: add cancel button?

    def _generate_colour_palette(self, tab, progress_callback):
        """Generate colour palette for current open image."""

        if tab is None:
            # Get image data for the current tab
            tab = self._view.tabs.currentWidget()

        # Temporarily disable buttons for the given tab
        self._toggle_tab_button_states(tab=tab, activate=False)

        # Set tab status bar state to generating colour palette
        tab.status_bar_state = 1

        # Reset state of tab
        self._reset_tab(tab=tab, remove_data=True)

        progress_callback.emit(tab, 0)

        # Generate colour palette
        image_id = tab.image_id
        self._model.generate_palette(image_id, tab, progress_callback)

        # Set image_data status bar state to colour palette generated
        tab.status_bar_state = 2

        # TODO: add try block for status bar updates in case of failure

        # Re-enable buttons for the tab
        self._toggle_tab_button_states(tab=tab, activate=True)

        # Add colour palette to the GUI representation of the colour palette
        image_data = self._model.get_image_data(image_id)
        colour_palette = image_data.colour_palette

        # return colour_palette, image_id

    @staticmethod
    def _toggle_tab_button_states(tab: NewTab, activate: bool):

        # Enable/disable palette generation action for the given tab
        tab.generate_palette_available = activate

        # Enable/disable toggle button for showing recoloured image for the given tab
        tab.toggle_recoloured_image_available = activate

        # Enable/disable report generation action for the given tab
        tab.generate_report_available = activate


    def _reset_tab(self, tab, remove_data=False):

        if remove_data:
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

        # Refresh tab
        self.current_tab_changed(-2)  # -2 does not correspond to any particular tab



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
