from abc import ABC, abstractmethod

from colourpaletteextractor.model.algorithms.cielabcube import CielabCube


def get_implemented_algorithms():
    """
        Recursively finds all subclasses of the current class.
        Like Python's __class__.__subclasses__(), but recursive.
        Returns a list containing all subclasses.

        Adapted from: https://www.programcreek.com/python/?CodeExample=get+subclasses
        Accessed: 15/07/2020


        @type cls: object
        @param cls: A Python class.
        @rtype: list(object)
        @return: A list containing all subclasses.
    """
    # TODO: modify above text
    cls = PaletteAlgorithm
    result = set()
    path = [cls]
    while path:
        parent = path.pop()
        for child in parent.__subclasses__():
            if not '.' in str(child):
                # In a multi inheritance scenario, __subclasses__()
                # also returns interim-classes that don't have all the
                # methods. With this hack, we skip them.
                continue
            if child not in result:
                result.add(child)
                path.append(child)
    return result


class PaletteAlgorithm(ABC):

    def __init__(self, name, url):
        """Constructor."""

        self._name = name
        self._url = url

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

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

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
        if self._progress_callback is not None:
            self._progress_callback.emit(self._tab, self._percent)

    def _get_increment_percent(self, final_percent, denominator):
        current_percent = self._percent
        return (final_percent - current_percent) / denominator

    def _set_progress(self, new_progress):
        self._percent = new_progress
        if self._progress_callback is not None:
            self._progress_callback.emit(self._tab, self._percent)

    @staticmethod
    def _get_relative_frequencies(relevant_cubes: list[CielabCube], total_pixels: int) -> list[float]:

        frequencies = []
        for cube in relevant_cubes:
            frequency = cube.pixel_count_after_reassignment / total_pixels
            frequencies.append(frequency)

        return frequencies
