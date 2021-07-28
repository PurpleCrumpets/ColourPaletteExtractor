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


import inspect
import sys

from PySide2 import QtCore
from PySide2.QtCore import Qt, QEvent
from PySide2.QtGui import QIcon, QPixmap, QPainter, QMovie
from PySide2.QtWidgets import QWidget, QProgressBar, \
    QStatusBar, QMessageBox, QLabel, QTabWidget, QDialog, QVBoxLayout, QRadioButton, QGridLayout, \
    QStyleOption, QPushButton, QLineEdit, QSizePolicy, QFileDialog, QHBoxLayout

from colourpaletteextractor import _version
from colourpaletteextractor._version import get_header, get_licence
from colourpaletteextractor.model.algorithms import palettealgorithm
from colourpaletteextractor.model.model import get_settings


class StatusBar(QStatusBar):
    """The status bar at the bottom of the main window.

    This holds the current shortcut tip for the given tab, as well as the progress bar for showing the
    current progress towards generating a report or the image's colour palette.

    Args:
        parent: Parent object of the StatusBar. Defaults to None.


    Attributes:
        _status_label (ElidedLabel): Primary status label.

        _progress_bar (QProgressBar): Progress bar used to track the progress of generating a colour palette or a
            report.

        _max_progress (int): Maximum value for the progress bar.

        _min_progress (int): Minimum value for the progress bar.

    """

    def __init__(self, parent=None):

        super(StatusBar, self).__init__(parent)

        self._max_progress = 100
        self._min_progress = 0

        self._add_status_bar_elements()
        self._set_pre_palette_message()

    def update_progress_bar(self, n: float) -> None:
        """Update the current level of progress for the status bar.

        Args:
            n (float): New level of progress for the progress bar.

        Raises:
            ValueError: If the new progress value exceeds the predefined limits of the progress bar.

        """

        if n > self._max_progress or n < self._min_progress:
            raise ValueError("The level of progress should be between " + str(self._min_progress) + " and "
                             + str(self._max_progress) + ". The progress value provided was: " + str(n) + ".")

        self._progress_bar.setValue(n)

    def set_status_bar(self, state: int) -> None:
        """Set the state of the status bar elements.

        Depending on the state, the primary status label will change to reflect what the application
        is currently processing.

        Args:
            state (int): The new state of the status bar.

        Raises:
            ValueError: If state is not a valid state.

        """

        if state == 0:
            # Show original status if no colour palette and it is not being generated
            self._set_pre_palette_message()
        elif state == 1:
            # Show toggle status if colour palette has been generated
            self._set_intra_palette_message()
        elif state == 2:
            # Show progress bar and associated top if colour palette is being generated
            self._set_post_palette_message()
        elif state == 3:
            # Show progress bar and associated tip while the report is being generated
            self._set_intra_report_message()
        else:
            raise ValueError(state, "is not a valid status bar state!")

    def _add_status_bar_elements(self) -> None:
        """Add the status bar elements to the status bar."""

        self._status_label = ElidedLabel(text="", width=100, parent=self)
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedWidth(250)
        self._progress_bar.setMinimum(self._min_progress)
        self._progress_bar.setMaximum(self._max_progress)

        # Spacers used to separate components out in the status bar
        spacer1 = QWidget()
        spacer1.setFixedWidth(5)
        spacer2 = QWidget()
        spacer2.setFixedWidth(5)
        spacer3 = QWidget()
        spacer3.setFixedWidth(5)

        # Add widgets and spacers to the status bar
        self.addWidget(spacer1, 1)
        self.addWidget(self._status_label, 1)
        self.addWidget(self._progress_bar, 1)
        self.addWidget(spacer2, 1)

        self.addPermanentWidget(QLabel("v" + _version.__version__))
        self.addPermanentWidget(spacer3)

    def _set_pre_palette_message(self) -> None:
        """Set the primary status label to the pre-palette generation message.

        Raises:
            RuntimeError: If the platform is not currently supported.
        """

        if sys.platform == "win32" or sys.platform == "linux":
            command = "Ctrl+G"
        elif sys.platform == "darwin":
            command = "⌘G"
        else:
            raise RuntimeError(sys.platform, "is not a supported platform!")

        self._status_label.setText("Generate the colour palette using " + command)

    def _set_intra_palette_message(self) -> None:
        """Set the primary status label to the message while generating a colour palette."""

        self._status_label.setText("Generating colour palette")

    def _set_post_palette_message(self) -> None:
        """Set the primary status label to the post-palette generation message.

        Raises:
            RuntimeError: If the platform is not currently supported.
        """

        if sys.platform == "win32" or sys.platform == "linux":
            command = "Ctrl+T"
        elif sys.platform == "darwin":
            command = "⌘T"
        else:
            raise RuntimeError(sys.platform, "is not a supported platform!")

        self._status_label.setText("Toggle between the original and recoloured image using " + command)

    def _set_intra_report_message(self) -> None:
        """Set the primary status label to the message while generating the colour palette report."""

        self._status_label.setText("Generating colour palette report")


class ElidedLabel(QLabel):
    """Status bar message label that will become elided if there is not enough space to display the entire message.

        Adapted from: `ref1`_ and `ref2`_

        Accessed: 18/07/2021

        Args:
            text (str): The text to be shown in the label. The default is an empty string

            width (int): The minimum width of the label. The default is 40.

            parent: The parent object of the ElidedLabel. The default is None.


    .. _ref1:
       https://stackoverflow.com/questions/35080148/how-to-hide-or-cut-a-qwidget-text-when-i-change-main-window-size

    .. _ref2:
      https://www.mimec.org/blog/status-bar-and-elided-label

    """

    _width = _text = _elided = None

    def __init__(self, text='', width=40, parent=None):
        super(ElidedLabel, self).__init__(text, parent)
        self.setMinimumWidth(width if width > 0 else 1)

    def elided_text(self) -> str:
        """Get the elided text shown by the label.

        Returns:
            (str): The elided text

        """
        return self._elided or ''

    def paintEvent(self, event: QEvent.Type.Paint) -> None:
        """Update the text shown by the label on receiving a paint event.

        Args:
            event (QEvent.Type.Paint): A paint event

        """

        painter = QPainter(self)
        self.drawFrame(painter)
        margin = self.margin()
        rect = self.contentsRect()
        rect.adjust(margin, margin, -margin, -margin)
        text = self.text()
        width = rect.width()
        if text != self._text or width != self._width:
            self._text = text
            self._width = width
            self._elided = self.fontMetrics().elidedText(
                text, Qt.ElideRight, width)
        option = QStyleOption()
        option.initFrom(self)
        self.style().drawItemText(
            painter, rect, self.alignment(), option.palette,
            self.isEnabled(), self._elided, self.foregroundRole())


class AboutBox(QMessageBox):
    """Message box to show the basic information about the application.

    Args:
        parent: The parent object of the AboutBox. The default is None.

    """

    def __init__(self, parent=None):
        super(AboutBox, self).__init__(parent)

        # Set icon
        self.setIconPixmap(QPixmap("icons:about-medium.png"))
        self.setWindowIcon(QIcon("icons:about-medium.png"))

        # Set  window title
        self.setWindowTitle("About " + _version.__application_name__)

        # Set text
        header = get_header()
        licence = get_licence()
        self.setText(header + "\n \n" + licence)
        self.setInformativeText(" ")  # Used to increase the width of the about box

        # Show the about box
        self.exec_()


class PreferencesWidget(QDialog):
    """The dialog box for setting a user's preferences.

    Currently, the user can change the algorithm used to generate the colour palette, as well as the
    output directory for any reports that are generated.

    Args:
        parent: The parent object of the PreferencesWidget. The default is None.

    Attributes:
        browse_button (QPushButton): Button used to open the operating system's file explorer to select a
            valid output directory.

        user_path_selector (QLineEdit): Text window used to show the user's currently selected output directory.

        default_path_button (QRadioButton): Button used to select the default output directory.

        user_path_button (QRadioButton): Button used to select the user's output directory.

        output_tab (QWidget): The output directory settings tab of the preferences dialog box.

        algorithm_tab (QWidget): The algorithm settings tab of the preferences dialog box.

    """

    def __init__(self, parent=None):

        super(PreferencesWidget, self).__init__(parent)

        self._read_settings()
        self._set_properties()

    def show_preferences(self) -> None:
        """Show the preferences widget."""
        self.exec_()

    def update_preferences(self) -> None:
        """Update the preferences dialog box with the correct settings."""

        self._read_settings()

        for button, algorithm in zip(self._algorithm_buttons, self._algorithms):
            if algorithm == self._default_algorithm:
                button.setChecked(True)
                break

        self.user_path_selector.setEnabled(self._use_user_dir)
        self.user_path_selector.setText(self._user_output_dir)
        self.browse_button.setEnabled(self._use_user_dir)
        self.default_path_button.setChecked(not self._use_user_dir)

    def show_output_directory_dialog_box(self, current_path: str):
        """Show the dialog box for selecting output directory for reports.

        Args:
            current_path (str): The path to open the system's file explorer to.

        Returns:
            (str): Path to the new output directory.

        """

        return QFileDialog.getExistingDirectory(self, "Select output folder", current_path, QFileDialog.ShowDirsOnly)

    def get_algorithms_and_buttons(self) -> tuple[list[palettealgorithm.PaletteAlgorithm], list[QRadioButton]]:
        """Get the list of algorithm classes and their associated buttons.

        Returns:
            (list[palettealgorithm.PaletteAlgorithm]): List of algorithm classes.
            (list[QRadioButton]]): List of buttons associated with the algorithm classes.

        """
        return self._algorithms, self._algorithm_buttons

    def _read_settings(self) -> None:
        """Look up the application's settings file and read-in the relevant settings for the preferences dialog box."""

        self._settings = get_settings()

        # Check if settings file exists
        if not self._settings.contains('output directory/user directory'):
            raise FileNotFoundError("Valid settings file not found...")

        # Load values from settings
        self._settings.beginGroup("output directory")
        self._temp_dir = self._settings.value('temporary directory')
        self._user_output_dir = self._settings.value('user directory')
        self._use_user_dir = self._settings.value('use user directory')
        self._settings.endGroup()

        self._settings.beginGroup("algorithm")
        self._default_algorithm = self._settings.value('default algorithm')
        self._selected_algorithm = self._settings.value('selected algorithm')
        self._settings.endGroup()

    def _set_properties(self) -> None:
        """Set the properties of the preferences dialog box."""

        self.setWindowTitle("Preferences")
        self.setWindowIcon(QIcon("icons:about-medium.png"))

        layout = QVBoxLayout()  # Top-level layout
        tabs = QTabWidget()  # tab widget for holding preferences
        layout.addWidget(tabs)  # Add tabs to layout

        # Create and add tabs to widget
        self._algorithm_properties_tab()
        tabs.addTab(self.algorithm_tab, "Algorithm")

        self._output_properties_tab()
        tabs.addTab(self.output_tab, "Output Directory")

        # Add reset preferences button
        self.reset_preferences_button = QPushButton("Reset Preferences")
        self.reset_preferences_button.setAutoDefault(False)
        self.reset_preferences_button.setDefault(False)
        layout.addWidget(self.reset_preferences_button, alignment=QtCore.Qt.AlignRight)

        # Set layout
        self.setLayout(layout)

    def _algorithm_properties_tab(self) -> None:
        """Set the properties and layout of the algorithm preferences tab."""

        self.algorithm_tab = QWidget()

        # Create and populate layout of algorithm options
        layout = QGridLayout()
        layout.addWidget(QLabel("Select a colour palette algorithm:"), 0, 0, 1, 2)

        line = self._create_horizontal_line()
        layout.addWidget(line, 1, 0, 1, 2)  # Horizontal line spacer

        # Dynamically add algorithm options
        self._algorithms = list(palettealgorithm.get_implemented_algorithms())
        self._algorithm_buttons = []
        algorithm_labels = []

        # Create radio button and hyperlink for each algorithm
        default_algorithm_found = False
        for algorithm_class in self._algorithms:

            # Check if class has abstract method - hence should not be added as a selectable algorithm
            if inspect.isabstract(algorithm_class):
                self._algorithms.remove(algorithm_class)
                continue

            algorithm = algorithm_class()
            name = algorithm.name
            url = algorithm.url

            # Adding algorithm button
            new_button = self._create_algorithm_radio_button(name)
            if algorithm_class == self._default_algorithm:  # Set default algorithm

                # new_button.setChecked(True)
                default_algorithm_found = True
                new_button.setText("[DEFAULT] " + name)  # Updating the name of the default algorithm

            elif algorithm_class == self._default_algorithm and default_algorithm_found:
                raise ValueError("Two algorithm classes have been selected as the default algorithm.")

            # Set selected algorithm
            if algorithm_class == self._selected_algorithm:
                new_button.setChecked(True)

            self._algorithm_buttons.append(new_button)

            # Adding algorithm url hyperlink label
            new_label = self._create_algorithm_link_label(url)
            algorithm_labels.append(new_label)

        # Reordering list of buttons and labels alphabetically by the algorithm name
        self._algorithms, self._algorithm_buttons, algorithm_labels = \
            self._reorder_algorithms(algorithms=self._algorithms,
                                     algorithm_buttons=self._algorithm_buttons,
                                     algorithm_labels=algorithm_labels)

        # Adding radio buttons and labels to the GUI
        count = 2
        for button, label in zip(self._algorithm_buttons, algorithm_labels):
            layout.addWidget(button, count, 0)
            layout.addWidget(label, count, 1)
            count += 1

        # Setting layout of buttons
        self.algorithm_tab.setLayout(layout)

        # Checking if default algorithm found
        if not default_algorithm_found:
            ValueError("No default algorithm has been specified!")

    def _output_properties_tab(self):
        """Set the properties and layout of the output directory preferences tab."""

        self.output_tab = QWidget()
        layout = QGridLayout()

        # Path requirements explanation
        layout.addWidget(QLabel("Select the output folder for the colour palette reports:"), 0, 0, 1, 2)

        # Horizontal line spacer
        line = self._create_horizontal_line()
        layout.addWidget(line, 1, 0, 1, 3)

        # Default path button and label
        self.default_path_button = QRadioButton()
        layout.addWidget(self.default_path_button, 2, 0)

        default_path_label = QLabel("Temporary Output Folder "
                                    + "(all unsaved reports will be lost upon closing the application).")
        layout.addWidget(default_path_label, 2, 1)

        # User-selected path
        self.user_path_button = QRadioButton()
        layout.addWidget(self.user_path_button, 3, 0)
        layout.addWidget(QLabel("Alternative Output Folder:"), 3, 1)

        self.user_path_selector = QLineEdit(self._user_output_dir)
        self.user_path_selector.setReadOnly(True)
        layout.addWidget(self.user_path_selector, 4, 1)

        # Browse button for a user to select their desired output directory
        self.browse_button = QPushButton("...")
        self.browse_button.setAutoDefault(False)
        self.browse_button.setDefault(False)

        layout.addWidget(self.browse_button, 4, 2)

        # Selecting temporary or user selected radio button
        if int(self._use_user_dir) == 1:
            self.user_path_button.setChecked(True)
            self.user_path_selector.setEnabled(True)
            self.browse_button.setEnabled(True)

        else:
            self.default_path_button.setChecked(True)
            self.user_path_selector.setDisabled(True)
            self.browse_button.setDisabled(True)

        # Sett layout of buttons
        self.output_tab.setLayout(layout)

    @staticmethod
    def _create_algorithm_radio_button(name: str) -> QRadioButton:
        """Create and return a radio button with the given name that is used to select the corresponding algorithm.

        If the name provided is None, the default label for the button is used.

        Args:
            name (str): The text to be shown next to the QRadioButton

        Returns:
            (QRadioButton): The appropriately labeled QRadioButton.

        """

        # Adding algorithm name if provided
        if name is not None:
            button = QRadioButton(name)
        else:
            button = QRadioButton("Algorithm name not provided!")

        return button

    @staticmethod
    def _create_algorithm_link_label(url: str) -> QLabel:
        """Given a url, create a hyperlinked QLabel.

        If the url is None, the text shown by the label is simply '-'.

        Args:
            url (str): The url.

        Returns:
            (QLabel): Hyperlinked label for the given url.

        """

        # Add url as a hyperlink if provided
        if url is not None:
            text = '<a href="' + url + '">Ref</a>'

        else:
            text = "-"

        label = QLabel()
        label.setText(text)
        label.setOpenExternalLinks(True)

        return label

    @staticmethod
    def _reorder_algorithms(algorithms: list[palettealgorithm.PaletteAlgorithm],
                            algorithm_buttons: list[QRadioButton],
                            algorithm_labels: list[QLabel]) -> tuple[list[palettealgorithm.PaletteAlgorithm],
                                                                     list[QRadioButton],
                                                                     list[QLabel]]:
        """Reorder the list of algorithms, their buttons, and their labels alphabetically by the algorithm's name.

        Args:
            algorithms (list[palettealgorithm.PaletteAlgorithm]): List of algorithm classes.
            algorithm_buttons (list[QRadioButton]): List of the buttons associated with each algorithm
            algorithm_labels (list[QLabel])): List of the labels associated with each algorithm

        Returns:
            (list[palettealgorithm.PaletteAlgorithm]): Re-ordered list of algorithm classes
            (list[QRadioButton]): Re-ordered list of the buttons associated with each algorithm
            (list[QLabel]]): Re-ordered list of the labels associated with each algorithm

        """

        # Reordering list of labels alphabetically by the algorithm name
        algorithm_labels = [x for _, x in sorted(zip(algorithm_buttons, algorithm_labels),
                                                 key=lambda pair: pair[0].text(),
                                                 reverse=True)]

        # Reordering list of algorithms alphabetically by the algorithm name
        algorithms = [x for _, x in sorted(zip(algorithm_buttons, algorithms),
                                           key=lambda pair: pair[0].text(),
                                           reverse=True)]

        # Reordering list of algorithm buttons alphabetically by the algorithm name
        algorithm_buttons.sort(key=lambda x: x.text(), reverse=True)

        return algorithms, algorithm_buttons, algorithm_labels

    @staticmethod
    def _create_horizontal_line() -> QWidget:
        """Create and return a horizontal line widget.

        Adapted from: :`ref3`_
        Accessed: 26/07/2021

        Returns:
            (QWidget): QWidget consisting of a horizontal line.

        .. _ref3:
           https://stackoverflow.com/questions/10053839/how-does-designer-create-a-line-widget

        """

        line = QWidget()
        line.setFixedHeight(2)
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line.setStyleSheet("background-color: #c0c0c0;")
        return line


class ErrorBox(QMessageBox):
    """Message box to show warnings and errors.

    Args:
        box_type (str): The error box type. Used to customise the icon and main text show.

        parent: Parent object of the ErrorBox. Defaults to None.
    """

    def __init__(self, box_type: str = None, parent=None):

        super(ErrorBox, self).__init__(parent)

        header = None

        # Set icon
        self.setWindowIcon(QIcon("icons:about-medium.png"))  # Window icon

        if box_type == "warning":
            self.setIcon(QMessageBox.Warning)  # Icon
            header = "Warning!"
        elif box_type == "information":
            self.setIcon(QMessageBox.Information)  # Icon
            header = "Heads-Up!"

        else:
            self.setIconPixmap(QPixmap("icons:about-medium.png"))

        self.setWindowTitle(header)  # Window title
        self.setText(header)  # Main text


class BatchGenerationProgressWidget(QDialog):
    """Custom dialog box shown when multiple colour palette or reports are being generated.

    Shows the number of threads to be run and the number of threads completed. Is also has a simple animation
    attached to it so the user knows that the application has not frozen and is still processing their
    images.

    Attributes:
        label (QLabel): Label used to show the number of threads to be run and the number completed.

        cancel_batch_button (QPushButton): The button used to notify the controller object that the user wishes to
            cancel the current batch processing.
    """

    def __init__(self):
        super().__init__()

        self._cancel_text = "Cancelling..."

        self._batch_type = ""
        self._total_count = 0
        self._current_count = 0

        self._set_properties()

    def show_widget(self, total_count: int, batch_type: str) -> None:
        """Reset and show the widget.

        Args:
            total_count (int): The total number of threads to be processed.

            batch_type (str): The text clarifying what task is being carried out as a batch process.

        """

        # Reset widget
        self._total_count = total_count
        self._current_count = 0
        self._batch_type = batch_type
        self.label.setText("")
        self._set_label_text()
        self._progress_bar.setValue(self._current_count)
        self._progress_bar.setMaximum(self._total_count)

        # Show the widget
        self.show()

    def update_progress(self) -> None:
        """Update the batch progress bar by increasing the number of completed threads by one."""

        self._current_count += 1

        self._progress_bar.setValue(self._current_count)
        self._set_label_text()

    def set_cancel_text(self) -> None:
        """Set the text shown to cancelling to let the user know that any incomplete threads are to be cancelled."""

        self.label.setText(self._cancel_text)

    def _set_label_text(self) -> None:
        """Update the text shown by the dialog box, depending on its current status."""

        if self.label.text() != self._cancel_text:
            self.label.setText("Generated " + self._batch_type + " for "
                               + str(self._current_count) + "/"
                               + str(self._total_count) + " images")

    def _set_properties(self):
        """Set the properties of the BatchGenerationProgressWidget."""

        self.setWindowTitle("Progress")
        self.setWindowIcon(QIcon("icons:about-medium.png"))

        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        # self.setWindowModality(Qt.NonModal)

        main_layout = QVBoxLayout()  # Top-level layout
        self.setLayout(main_layout)

        # Text label
        secondary_layout = QHBoxLayout()
        main_layout.addLayout(secondary_layout)
        self.label = QLabel()
        self._set_label_text()
        secondary_layout.addWidget(self.label)

        # Animated progress gif
        self._progress_gif = QMovie("images:animated-colour-palette.gif")
        self._progress_gif.setScaledSize(QtCore.QSize(40, 40))
        self._progress_label = QLabel()
        self._progress_label.setMovie(self._progress_gif)
        self._progress_gif.start()
        secondary_layout.addWidget(self._progress_label, alignment=QtCore.Qt.AlignRight)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(self._total_count)
        main_layout.addWidget(self._progress_bar)

        # Cancel button
        self.cancel_batch_button = QPushButton("Cancel")
        self.cancel_batch_button.setAutoDefault(False)
        self.cancel_batch_button.setDefault(False)
        main_layout.addWidget(self.cancel_batch_button, alignment=QtCore.Qt.AlignRight)
