import sys
import traceback

from PySide2.QtCore import QRunnable, Slot, QObject, Signal


class ColourPaletteWorker(QRunnable):
    """
    Worker thread
    Adapted from: https://www.mfitzp.com/tutorials/multithreading-pyqt-applications-qthreadpool/
    Accessed: 01/08/21

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(ColourPaletteWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ColourPaletteWorkerSignals()

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
            # self.signals.finished.emit(colour_palette, image_id)  # Done
            self.signals.finished.emit(-2)  # Done


class ColourPaletteWorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        to add more details

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    """
    # Data types for each signal
    # finished = Signal(object, str)
    finished = Signal(int)
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(object, int)


class ReportGeneratorWorker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(ReportGeneratorWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ReportGeneratorWorkerSignals()

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
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exc_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exc_type, value, traceback.format_exc()))
        else:
            self.signals.result.emit(None)  # Return the result of the processing
        finally:
            # self.signals.finished.emit(colour_palette, image_id)  # Done
            self.signals.finished.emit(-2)  # Done


class ReportGeneratorWorkerSignals(QObject):

    # Data types for each signal
    # finished = Signal(object, str)
    finished = Signal(int)
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(object, int)
