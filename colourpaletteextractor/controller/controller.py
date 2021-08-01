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


from __future__ import annotations
from functools import partial  # Import partial to connect signals with methods that need to take extra arguments

import numpy as np
from PySide2 import QtCore
from PySide2.QtCore import QFileInfo, QRunnable, QThreadPool

from colourpaletteextractor.controller.worker import Worker
from colourpaletteextractor.model import generatereport
from colourpaletteextractor.model.algorithms.palettealgorithm import PaletteAlgorithm
from colourpaletteextractor.model.imagedata import ImageData
from colourpaletteextractor.model.model import ColourPaletteExtractorModel
from colourpaletteextractor.view import mainview as vw, otherviews
from colourpaletteextractor.view.mainview import MainView
from colourpaletteextractor.view.tabview import NewTab


class ColourPaletteExtractorController(QRunnable):
    """ColourPaletteExtractor Controller.

    Used to connect the ColourPaletteExtractor GUI signals with the appropriate slot to be able to manipulate the
    associated model.

    Args:
        model (ColourPaletteExtractorModel): The main model of ColourPaletteExtractor.
        view (MainView): The main window of ColourPaletteExtractor.

    """

    def __init__(self, model: ColourPaletteExtractorModel, view: MainView) -> None:

        super().__init__()

        # Assign model and view
        self._view = view
        self._model = model

        # Connect signals and slots
        self._connect_main_window_signals()
        self._connect_tab_signals()
        self._connect_preferences_signals()
        self._connect_batch_progress_signals()

        # Signal creation of instructions tab
        self._create_default_tab()

    def current_tab_changed(self, i: int):
        """Update the current tab index and update the view with the tab's properties.

        In most cases, i >= 0, however a value of i = -2 or -3 is also valid for performing a 'dummy' tab change to
        update the current view shown to the user. A value of -1 will lead to the creation of the default tab
        (the quick start guide).

        Args:
            i (int): Index of the current tab.

        Raises:
            ValueError: If the value of i is less than -3.

        """

        if i < -3:
            raise ValueError("The current tab index should be equal to or greater than -3 (value of "
                             + str(i) + " provided)!")

        # Create new default tab if all have been removed
        if i == -1:
            self._create_default_tab()

        # Enable/disable toggle button for displaying recoloured image
        tab = self._view.tabs.currentWidget()
        image_id = tab.image_id
        self._update_state_of_tab_buttons(tab=tab)

        # Reload colour palette
        if i != -3:  # This prevents the GUI from flickering that occurs when needlessly updating the colour palette
            colour_palette = self._get_colour_palette(tab)
            relative_frequencies = self._get_relative_frequencies(tab)

            if len(colour_palette) == 0:
                self._view.colour_palette_dock.remove_colour_palette()  # Reset colour palette dock
            else:
                self._view.colour_palette_dock.add_colour_palette(colour_palette, image_id, relative_frequencies)

        # Update status bar
        self._update_status_bar(tab)

    def _connect_main_window_signals(self) -> None:
        """Connect the main window signals to the appropriate slots."""

        # Close event
        self._view.close_action.triggered.connect(self._close_application)

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

    def _connect_tab_signals(self) -> None:
        """Connect the :class:`tabview.NewTab` signals to the appropriate slots."""

        # Tab events
        self._view.tabs.currentChanged.connect(self.current_tab_changed)
        self._view.tabs.tabCloseRequested.connect(self._close_current_tab)

    def _connect_preferences_signals(self) -> None:
        """Connect the preferences dialog box signals to the appropriate slots."""

        self._view.preferences.reset_preferences_button.clicked.connect(self._reset_preferences)
        self._connect_algorithm_selector_signals()
        self._connect_output_directory_selector_signals()

    def _connect_algorithm_selector_signals(self) -> None:
        """Connect the algorithm selector signals from the preferences dialog box to the appropriate slots."""

        algorithms, algorithm_buttons = self._view.preferences.get_algorithms_and_buttons()

        # Connect each radio button to the correct slot
        for algorithm, algorithm_button in zip(algorithms, algorithm_buttons):
            algorithm_button.clicked.connect(partial(self._set_algorithm, algorithm))

    def _connect_output_directory_selector_signals(self) -> None:
        """Connect the output directory selector signals from the preferences dialog box to the appropriate slots."""

        self._view.preferences.default_path_button.clicked.connect(partial(self._set_output_path, use_user_dir=False))
        self._view.preferences.user_path_button.clicked.connect(partial(self._set_output_path, use_user_dir=True))
        self._view.preferences.browse_button.clicked.connect(self._get_output_path)

    def _connect_batch_progress_signals(self) -> None:
        """Connect the batch progress dialog box signals to the appropriate slot."""

        self._view.batch_progress_widget.cancel_batch_button.clicked.connect(self._send_stop_signals_to_batch_threads)

    def _close_application(self) -> None:
        """Remove the application's temporary directory and its contents."""

        print("Removing temporary directory and its contents...")
        self._model.close_temporary_directory()

    def _open_file(self) -> None:
        """Open the file dialog box and create a :class:`tabview.NewTab` object for each newly imported image."""

        supported_files = self._model.SUPPORTED_IMAGE_TYPES
        file_names, _ = self._view.show_file_dialog_box(supported_files)

        for file_name in file_names:
            new_image_data_id = None
            new_image_data = None

            if file_name != "":
                new_image_data_id, new_image_data = self._model.add_image(file_name)
            else:
                print("No image selected...")

            if new_image_data is not None:
                # Create new tab linked to the image
                self._create_new_tab(new_image_data_id, new_image_data)

    def _generate_all(self, batch_type: str) -> None:
        """Generate the colour palette or colour palette report for all possible images.

        Any image can have its colour palette generated at all times. The colour palette report can only be generated
        if the image already has a colour palette generated.

        Args:
            batch_type (str): The action to be run as a batch. This can either be 'colour palette' or 'report'.

        Raises:
            ValueError: For an invalid batch_type.

        """

        # Disable batch actions
        self._view.generate_all_report_action.setDisabled(True)
        self._view.generate_all_palette_action.setDisabled(True)
        self._view.preferences_action.setDisabled(True)

        num_tabs = self._view.tabs.count()  # Number of tabs to process

        # Update model thread counter
        self._model.active_thread_counter = num_tabs

        thread_count = 0  # Used for keeping track of the number of reports being generated

        # Generate worker for each tab
        for i in range(num_tabs):
            tab = self._view.tabs.widget(i)

            # Generate the colour palette for the given tab
            if batch_type == "colour palette":
                self._generate_worker(main_function=batch_type, tab=tab, batch_generation=True)
                thread_count += 1

            # Generate the colour palette report for the given tab
            elif batch_type == "report":

                # Check if tab has the necessary details to create a report
                if tab.generate_report_available:
                    thread_count += 1
                    self._generate_worker(main_function=batch_type, tab=tab, batch_generation=True)
                else:
                    self._model.active_thread_counter -= 1

            else:
                raise ValueError("The batch_type should either be 'colour palette' or 'report'. "
                                 + "The provided string was: " + batch_type + "...")

        # Let the user know that the colour palette needs to be generated before generating the report
        if batch_type == "report" and thread_count == 0:
            message = "You need to generate the colour palette for at least one image " \
                      + "before you can generate a report!"
            msg_box = otherviews.ErrorBox(box_type="information")
            msg_box.setInformativeText(message)
            msg_box.exec_()

            # Re-enable batch actions
            self._view.generate_all_report_action.setEnabled(True)
            self._view.generate_all_palette_action.setEnabled(True)
            self._view.preferences_action.setEnabled(True)
            return

        # Show overall progress widget
        self._view.batch_progress_widget.show_widget(total_count=thread_count, batch_type=batch_type)

    def _generate_worker(self, main_function: str, tab: NewTab = None, batch_generation: bool = False) -> None:
        """Generate a new thread to either generate the colour palette or the colour palette report for the given tab.

        Args:
            main_function (str): The action to be run. This can either be 'colour palette' or 'report'.
            tab (NewTab): The tab to perform the main_function on.
            batch_generation (bool): True if the worker is being generated as part of a batch. Otherwise False.

        Raises:
            ValueError: For an invalid main_function.
        """

        # Get tab
        if tab is None:
            tab = self._view.tabs.currentWidget()

        # Select primary function
        if main_function == "colour palette":
            worker = Worker(self._generate_colour_palette, function_type=main_function, tab=tab)
        elif main_function == "report":
            worker = Worker(self._generate_report, function_type=main_function, tab=tab)
        else:
            raise ValueError("The main_function should either be 'colour palette' or 'report'. "
                             + "The provided string was: " + main_function + "...")

        # Connect additional worker signals and start the thread
        self._connect_worker_signals(worker=worker, batch_generation=batch_generation)
        QThreadPool.globalInstance().start(worker)

    def _connect_worker_signals(self, worker: Worker, batch_generation: bool) -> None:
        """Connect the additional worker signals for generating a colour palette or a colour palette report.

        Args:
            worker (Worker): Worker thread used to generate the colour palette or the colour palette report.
            batch_generation (bool): True if worker is being run as part of a batch process. Otherwise False.

        """

        # Connect signals
        if batch_generation:
            worker.signals.finished.connect(self._finish_generation)  # Function called at the very end
        else:
            worker.signals.finished.connect(self.current_tab_changed)  # Function called at the very end

        worker.signals.progress.connect(self._update_progress_bar)  # Intermediate Progress
        worker.signals.error.connect(self._show_error_generation_dialog_box)
        # worker.signals.result.connect(self._update_tab)  # Uses the result of the main function (NOT IN USE)

    def _show_error_generation_dialog_box(self, tab: NewTab, error_type: int,
                                          error_info: tuple[type[Exception], Exception, str]) -> None:
        """Display a message box for the given exception.

        Used when a thread fails for some reason. Resets the GUI components for the :class:`tabview.NewTab` object
        associated with the thread.

        Args:
            tab (NewTab): The tab for which the error occurred.
            error_type (int): Specify if no error occurred during generation (0), an error occurred during the
                colour palette generation (1) or an error occurred during the colour palette report generation (2).
            error_info(tuple[type[Exception], Exception, str]): THe exception type, the exception and the stack trace
                associated with the error.

        Raises:
            ValueError: If the provided error_type is invalid.

        """

        # exc_type = error_info[0]  # Not used
        value = error_info[1]
        traceback = error_info[2]

        error_msg_box = otherviews.ErrorBox(box_type="error")
        error_msg_box.append_title(value)
        error_msg_box.setInformativeText(traceback)
        error_msg_box.exec_()

        # Re-enable correct buttons for the given tab upon an error and update the status bar
        if error_type == 0:  # Palette generation error
            self._toggle_tab_button_states(tab=tab, activate=True, palette_generated=False)
            tab.status_bar_state = 0  # Tab status to generate colour palette

        elif error_type == 1:  # Report generation error
            self._toggle_tab_button_states(tab=tab, activate=True)
            tab.status_bar_state = 2  # Tab status to colour palette generated

        else:
            raise ValueError("The error_occurred value must be either "
                             + "0 (colour palette generation error), "
                             + "or 1 (colour palette report generation error. The value provided was: "
                             + str(error_type) + "...")

        # Update GUI and progress bar
        self._update_progress_bar(tab, 0)

    def _send_stop_signals_to_batch_threads(self) -> None:
        """Send stop signals to all threads being run as part of a batch."""

        # Update batch progress widget to let user know the threads are being stopped
        self._view.batch_progress_widget.set_cancel_text()

        # Update stop preferences
        for _, image_data in self._model.image_data_id_dictionary.items():
            image_data.continue_thread = False

    def _reset_preferences(self) -> None:
        """Reset the preferences back to the default settings."""

        self._model.write_default_settings()  # Update settings file
        self._view.preferences.update_preferences()  # Update preferences panel

    def _get_output_path(self) -> None:
        """Display a file dialog box to select the new output directory and update the view and the model with it."""
        current_path = self._view.preferences.user_path_selector.text()
        new_path = self._view.preferences.show_output_directory_dialog_box(current_path=current_path)

        # If new path selected, update the view and model with the new path
        if new_path != "":
            self._view.preferences.user_path_selector.setText(new_path)
            self._model.change_output_directory(use_user_dir=True, new_user_directory=new_path)

    def _set_output_path(self, use_user_dir: bool) -> None:
        """Toggle between the user's output director for colour palette reports and the default, temporary directory.

        Args:
            use_user_dir (bool): If True, use the user's output directory. If False, use the default, temporary
                directory.

        """

        # Set the new output directory
        new_user_directory = self._view.preferences.user_path_selector.text()
        self._model.change_output_directory(use_user_dir=use_user_dir, new_user_directory=new_user_directory)

        # Update the GUI
        self._view.preferences.user_path_selector.setEnabled(use_user_dir)
        self._view.preferences.browse_button.setEnabled(use_user_dir)

    def _set_algorithm(self, algorithm: type[PaletteAlgorithm]) -> None:
        """Set the algorithm used to generate an image's colour palette.

        Args:
            algorithm (type[PaletteAlgorithm]): The colour palette algorithm class (not object).

        """
        self._model.set_algorithm(algorithm)

    def _stop_current_thread(self) -> None:
        """Stop the thread generating a colour palette or report for the image shown by the current tab."""
        tab = self._view.tabs.currentWidget()

        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)
        image_data.continue_thread = False

    def _zoom_in(self) -> None:
        """Zoom into the current image."""

        tab = self._view.tabs.currentWidget()
        image_display = tab.image_display
        image_display.zoom_in()

    def _zoom_out(self) -> None:
        """Zoom out of the current image."""

        tab = self._view.tabs.currentWidget()
        image_display = tab.image_display
        image_display.zoom_out()

    def _create_default_tab(self) -> None:
        """Create and display the default :class:`tabview.NewTab` in the main window."""

        # Get the default image
        default_file = vw.MainView.default_new_tab_image
        default_file = QFileInfo(default_file).absoluteFilePath()

        # Add image to the model
        new_image_data_id, new_image_data = self._model.add_image(file_name_and_path=default_file)

        # Set the name of the default tab
        new_image_data.name = "Quick Start Guide"

        # Create new tab linked to the image
        self._create_new_tab(image_data_id=new_image_data_id, new_image_data=new_image_data)

    def _create_new_tab(self, image_data_id: str, new_image_data: ImageData) -> None:
        """Create and display a new :class:`tabview.NewTab` in the main window."""

        self._view.create_new_tab(image_id=image_data_id, image_data=new_image_data)

    def _close_current_tab(self, tab_index: int) -> None:
        """Close the :class:`tabview.NewTab` with the index number tab_index.

        Args:
            tab_index (int): The index of the tab to be closed.

        """

        # Get image data
        image_data_id = self._view.tabs.currentWidget().image_id
        image_data = self._model.get_image_data(image_data_id)

        image_data.continue_thread = False

        # Remove image_data from dictionary in model
        self._model.remove_image_data(image_data_id)

        # Close currently selected tab in GUI
        self._view.close_current_tab(tab_index)

    def _update_progress_bar(self, tab: NewTab, percent: int) -> None:
        """Update the progress bar for the given tab.

        Args:
            tab (NewTab): Tab to update the progress bar for.
            percent (int): New percentage progress for the given tab.

        Raises:
            ValueError: If an invalid error_occurred value is provided
        """

        # Update progress status value
        tab.progress_bar_value = percent

        # Update progress bar on GUI
        if tab == self._view.tabs.currentWidget():
            self._view.status.update_progress_bar(percent)
            self._update_status_bar(tab)

            # Refresh the GUI at the start and end of the thread
            if percent == 0 or percent == 100:

                if tab.status_bar_state == 1:
                    self.current_tab_changed(-2)  # Generating colour palette
                else:
                    self.current_tab_changed(-3)  # Generating colour palette report

    def _finish_generation(self, i: int) -> None:
        """Update tab with the given tab index i and the GUI actions after generation of the colour palette or report.

        Only used when the thread has been run as part of a batch operation.

        Args:
            i (int): Tab index

        """

        # Update number of active threads
        self._view.batch_progress_widget.update_progress()
        self._model.active_thread_counter -= 1

        self.current_tab_changed(i=i)  # Update GUI view

        # If no more active threads
        if self._model.active_thread_counter == 0:
            self._view.batch_progress_widget.close()  # Close the batch progress dialog box

            # Re-enable batch actions
            self._view.generate_all_report_action.setEnabled(True)
            self._view.generate_all_palette_action.setEnabled(True)
            self._view.preferences_action.setEnabled(True)

    def _generate_report(self, tab: NewTab, progress_callback: QtCore.SignalInstance) -> None:
        """Generate the colour palette report for the image linked to the given tab.

        Args:
            tab (NewTab): Tab linked to the image that is to have its colour palette report generated.
            progress_callback (QtCore.SignalInstance): Signal that when emitted, is used to update the GUI.

        """

        if tab is None:
            tab = self._view.tabs.currentWidget()  # Get image data for the current tab

        # Get image data
        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)

        print("Generating PDF colour palette report for image: " + image_id + "...")

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
        progress_callback.emit(tab, 100)  # Update GUI
        print("Generated PDF colour palette report for image: " + image_id + "...")

    def _generate_colour_palette(self, tab: NewTab, progress_callback: QtCore.SignalInstance):
        """Generate the colour palette for the image linked to the given tab.

        Args:
            tab (NewTab): Tab linked to the image that is to have its colour palette generated.
            progress_callback (QtCore.SignalInstance): Signal that when emitted, is used to update the GUI.
        """

        if tab is None:
            tab = self._view.tabs.currentWidget()  # Get image data for the current tab

        # Update tab properties and refresh GUI
        self._toggle_tab_button_states(tab=tab, activate=False)  # Disable buttons for the given tab
        tab.status_bar_state = 1  # Set tab status to generating colour palette
        self._reset_tab_image_properties(tab=tab)  # Remove recoloured image and colour palette
        progress_callback.emit(tab, 0)  # Update GUI

        # Generate colour palette
        image_id = tab.image_id
        print("Generating colour palette for image: " + image_id + "...")
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

            # Re-enable buttons for the tab
            self._toggle_tab_button_states(tab=tab, activate=True, palette_generated=palette_generated)

            # Update GUI
            progress_callback.emit(tab, 100)
            print("Generated colour palette for image: " + image_id + "...")

    @staticmethod
    def _toggle_tab_button_states(tab: NewTab, activate: bool, palette_generated: bool = True) -> None:
        """Turn on/off the actions for generating a colour palette, report and showing the recoloured image for the tab.

        Args:
            tab (NewTab):
            activate (bool): True to enable the three actions. False to disable them.
            palette_generated (bool): If True, changes the availability of the report generation and toggling between
                the original and recoloured image actions. If False, these actions are not changed.

        """

        tab.generate_palette_available = activate  # Palette generation

        if palette_generated:
            tab.toggle_recoloured_image_available = activate  # Toggle button for showing recoloured image
            tab.generate_report_available = activate  # Report generation

    def _reset_tab_image_properties(self, tab: NewTab) -> None:
        """Reset the properties for given tab and the :class:`ImageData` object it is associated with.

        Reset the buttons for the tab, remove the recoloured image and colour palette for the associated
            :class:`ImageData` object.

        Args:
            tab (NewTab): The tab to reset

        """

        # Reset image data
        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)
        image_data.colour_palette = []  # Remove colour palette
        image_data.recoloured_image = None  # Remove recoloured image

        # Reset tab data
        image = image_data.image
        tab.image_display.update_image(image)

        # Reset tab buttons
        tab.toggle_recoloured_image_available = False
        tab.toggle_recoloured_image_pressed = False

    def _toggle_recoloured_image(self) -> None:
        """Switch between the original and recoloured image for the current tab."""

        # Get the image data for the current tab
        tab = self._view.tabs.currentWidget()
        image_id = tab.image_id
        image_data = self._model.get_image_data(image_id)

        # Select the new image to show
        if tab.toggle_recoloured_image_available and not tab.toggle_recoloured_image_pressed:
            image = image_data.recoloured_image
        else:
            image = image_data.image

        # Update the GUI buttons and show the new image
        tab.image_display.update_image(image)
        tab.change_toggle_recoloured_image_pressed()
        tab.update()

    def _get_colour_palette(self, tab: NewTab):
        """Finds the ImageData object associated with the given tab and returns its colour palette.

        Will return an empty list if the tab doesn't have a :class:`ImageData` object associated with it.

        Args:
            tab (NewTab): Tab linked to the :class:`ImageData` object with the colour palette of interest.

        Returns:
            (list[np.array]): The colours in the colour palette as a list of the sRGB triplets.

        """

        image_data_id = tab.image_id
        image_data = self._model.get_image_data(image_data_id)

        if image_data is None:
            return []
        else:
            return image_data.colour_palette

    def _get_relative_frequencies(self, tab: NewTab) -> list[np.array]:
        """Finds the ImageData object associated with the given tab and returns the relative frequencies of each colour.

        Will return an empty list if the tab doesn't have a :class:`ImageData` object associated with it.

        Args:
            tab (NewTab): Tab linked to the :class:`ImageData` object with the relative frequencies of interest.

        Returns:
            (list[np.array]): List of the relative frequencies of each colour in the colour palette.

        """

        image_data_id = tab.image_id
        image_data = self._model.get_image_data(image_data_id)

        if image_data is None:
            return []
        else:
            return image_data.colour_palette_relative_frequency

    def _update_state_of_tab_buttons(self, tab: NewTab):
        """Update the state of the GUI buttons according to the given :class:`tabview.NewTab`.

        Args:
            tab (NewTab): Tab to take the status of the GUI buttons from.

        """

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

    def _update_status_bar(self, tab: NewTab) -> None:
        """Update the status bar according to the given :class:`tabview.NewTab`.

        Args:
            tab (NewTab): Tab to take the status bar properties from.

        """
        # Update the status bar text
        status_bar_state = tab.status_bar_state
        self._view.status.set_status_bar(status_bar_state)

        # Update the progress bar percentage in the status bar
        percent = tab.progress_bar_value
        self._view.status.update_progress_bar(percent)
