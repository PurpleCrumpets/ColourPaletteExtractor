from PySide2.QtCore import QRunnable, Slot


class Worker(QRunnable):
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
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):

        print("Code goes here")
        self.fn(*self.args, **self.kwargs)
