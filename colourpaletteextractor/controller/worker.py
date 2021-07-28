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


class Worker(QRunnable):
    """Worker thread used to generate the colour palette or report for an image.


    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    Adapted from: `ref`_

    Accessed: 01/08/21

    Args:
        fn:
        image_data:
        function_type:
        *args: Arguments to pass to the callback function
        *kwargs: Keywords to pass to the callback function


    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function


    .. _ref:
       https://www.mfitzp.com/tutorials/multithreading-pyqt-applications-qthreadpool/

    """

    def __init__(self, fn, image_data, function_type, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.image_data = image_data
        self.function_type = function_type
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress



    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        # Retrieve args/kwargs here; and fire processing using them
        colour_palette = None
        image_id = None
        try:
            # colour_palette, image_id = self.fn(*self.args, **self.kwargs)
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exc_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exc_type, value, traceback.format_exc()))
        else:
            self.signals.result.emit(None)  # Return the result of the processing
        finally:
            if self.function_type == "colour palette":
                self.signals.finished.emit(-2)  # Done
            elif self.function_type == "report":
                self.signals.finished.emit(-3)  # Done


class WorkerSignals(QObject):
    """Specify the signals available from a running :class:`Worker` thread.

    Adapted from: `ref`_

    Accessed: 01/08/21

    Supported signals are:

    finished
        Integer emitted upon finishing. When generating a colour palette, the value is -2.
        When generating a report, the value is -3. THis is ues to reload the tab displaying
        the image with the correct settings and colour palette.

    progress
        NewTab object for which the GUI is to be updated for and the percentage complete
        for the current task (generating the colour palette or generating the report).

    error
        tuple (exctype, value, traceback.format_exc() ) - Not in use

    result
        object data returned from processing, anything



    """
    # Data types for each signal
    finished = Signal(int)
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(object, int)
