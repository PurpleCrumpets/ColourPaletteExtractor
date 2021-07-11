from abc import ABC, abstractmethod


class PaletteAlgorithm(ABC):

    def __init__(self):
        """Constructor."""

        # Parameters used for progress callback
        self._tab = None
        self._progress_callback = None
        self._percent = 0

    # @property
    # def percent(self):
    #     return self._percent
    #
    # @percent.setter
    # def percent(self, increment):
    #     self._percent += increment
    #     # TODO: add checks for value

    @abstractmethod
    def generate_colour_palette(self, image):
        """From the given image, return its colour palette"""
        pass

    def set_progress_callback(self, progress_callback, tab):
        self._progress_callback = progress_callback
        self._tab = tab

    def _increment_progress(self, increment):
        self._percent += increment
        # TODO: throw exception if larger than 100%
        self._progress_callback.emit(self._tab, self._percent, False)

    def _get_increment_percent(self, final_percent, denominator):
        current_percent = self._percent
        return (final_percent - current_percent) / denominator

    def _set_progress(self, new_progress):
        self._percent = new_progress
        self._progress_callback.emit(self._tab, self._percent, False)


