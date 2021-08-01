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


import sys
import traceback

from PySide2.QtCore import QRunnable, Slot, QObject, Signal

from colourpaletteextractor.view.tabview import NewTab


class Worker(QRunnable):
    """Worker thread used to generate the colour palette or report for an image.


    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    Adapted from: `ref`_

    Accessed: 01/08/21

    Args:
        fn: The function or method to be run as a new thread (generating an image's colour palette or its colour palette
            report.
        tab (NewTab): :class:`tabview.NewTab` object associated with the image to be processed.
        function_type (str): The action to be run. This can either be 'colour palette' or 'report'.
        *args: Arguments to pass to the callback function
        *kwargs: Keywords to pass to the callback function


    Attributes:

    :param progress_callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function

    Raises:
        ValueError: If the provided function_type is invalid.


    .. _ref:
       https://www.mfitzp.com/tutorials/multithreading-pyqt-applications-qthreadpool/

    """

    def __init__(self, fn, function_type: str, tab: NewTab, *args, **kwargs):
        super(Worker, self).__init__()

        if function_type != "colour palette" and function_type != "report":
            raise ValueError("The batch_type should either be 'colour palette' or 'report'. "
                             + "The provided string was: " + function_type + "...")

        # Store constructor arguments (re-used for processing)
        self._fn = fn
        self._function_type = function_type
        self._tab = tab
        self._args = args
        self._kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self._kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self._fn(self._tab, *self._args, **self._kwargs)
        except:  # Catching all exceptions
            traceback.print_exc()
            exc_type, value = sys.exc_info()[:2]

            # Show error message dialog box and update GUI properties
            if self._function_type == "colour palette":
                self.signals.error.emit(self._tab, 0, (exc_type, value, traceback.format_exc()))
            elif self._function_type == "report":
                self.signals.error.emit(self._tab, 1, (exc_type, value, traceback.format_exc()))

        else:
            self.signals.result.emit(None)  # Return the result of the processing (NOT IN USE)
        finally:
            if self._function_type == "colour palette":
                self.signals.finished.emit(-2)  # Done
            elif self._function_type == "report":
                self.signals.finished.emit(-3)  # Done


class WorkerSignals(QObject):
    """Specify the signals available from a running :class:`Worker` thread.

    Adapted from: `ref`_

    Accessed: 01/08/21

    Supported signals are:

    """

    # Data types for each signal
    finished = Signal(int)
    """Integer emitted upon finishing.
    
     When generating a colour palette, the value is -2. When generating a report, the value is -3. 
     This is used to reload the tab displaying the image with the correct settings and colour palette.
    
    """

    error = Signal(object, int, tuple)
    """Tuple (exc_type, value, traceback.format_exc())."""

    result = Signal(object)
    """Object data returned from processing, anything - NOT IN USE."""

    progress = Signal(object, int)
    """NewTab object for which the GUI is to be updated for and the percentage complete for the current task.
    
    The current task is either generating the colour palette for an image or generating the colour palette report for
    the image.
    
    """
