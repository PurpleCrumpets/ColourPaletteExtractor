from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from PySide2 import QtCore

import colourpaletteextractor.view.tabview as tabview
import colourpaletteextractor.model.imagedata as imagedata


def get_implemented_algorithms():
    """Recursively finds all subclasses of the :class:`.PaletteAlgorithm` class.

        Like Python's __class__.__subclasses__(), but recursive.
        Returns a list containing all subclasses of :class:`.PaletteAlgorithm`.


        Adapted from: `ref`_

        Accessed: 15/07/2020

        Returns:
            [object]: List of all subclasses of :class:`.PaletteAlgorithm`

    .. _ref:
       https://www.programcreek.com/python/?CodeExample=get+subclasses
    """

    cls = PaletteAlgorithm
    result = set()
    path = [cls]
    while path:
        parent = path.pop()
        for child in parent.__subclasses__():
            if inspect.isabstract(child):
                path.append(child)
                continue

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
    """Abstract class representing an algorithm used to obtain a colour palette from an image.

    Args:
        name (str): Name of the algorithm
        url (str): Link to a description of the algorithm
    """

    def __init__(self, name: str, url: str):

        self._name = name
        self._url = url

        # Parameters used for progress callback
        self._progress_callback: Optional[QtCore.SignalInstance] = None
        self._tab: Optional[tabview.NewTab] = None
        self._image_data: Optional[imagedata.ImageData] = None
        self._percent: int = 0  # Initially 0% complete

        # Execution status of algorithm
        self._continue_thread: bool = True

    @property
    def continue_thread(self) -> bool:
        """Get the execution status of the algorithm.

        A value of *false* would indicate that the algorithm should return without generation a colour palette when it
        next checks its execution status.

        Returns:
            bool: The execution status of the algorithm

        """
        return self._continue_thread

    @continue_thread.setter
    def continue_thread(self, value: bool):
        """Set the execution status of the algorithm

        Args:
            value (bool): New execution status of the algorithm

        """
        self._continue_thread = value

    @property
    def name(self) -> str:
        """Get the name of the algorithm.

        Returns:
            (str): The name of the algorithm

        """
        return self._name

    @property
    def url(self) -> str:
        """Get the link to the description of the algorithm.

        Returns:
            (str): The link to the description of the algorithm
        """
        return self._url

    @abstractmethod
    def generate_colour_palette(self, image: np.array) -> tuple[Optional[np.array], list, list]:
        """Generate the colour palette for the given image.

        Analyses the given image to obtain its colour palette. Returns the recoloured image using only the colours
        found in the colour palette, the colour palette of the image and finally the relative frequencies of each of
        those colours in the recoloured image.

        Args:
            image (np.array): A 3D array representing an image. It is assumed that the input image is

        Returns:
            recoloured__image (np.array): The recoloured image using only the colours found in the colour palette
            colour_palette (list): The list of colours (sRGB 8-bit values) in the colour palette
            relative_frequencies (list): The relative frequencies of each colour in the colour palette in the
             recoloured image

        Note:
            It is assumed that the input image has been encoded in the sRGB colour space.

        """

        pass

    def set_progress_callback(self,
                              progress_callback: QtCore.SignalInstance,
                              tab: tabview.NewTab,
                              image_data) -> None:
        """Set the signal function called by the algorithm at regular intervals to update the GUI thread.

        Args:
            progress_callback (QtCore.SignalInstance):
            tab (NewTab): The tab associated with the image being analysed (see :meth:`.generate_colour_palette`
            image_data (ImageData): `ImageData` object that holds the image being analysed

        """

        self._progress_callback = progress_callback
        self._tab = tab
        self._image_data = image_data

    def _increment_progress(self, increment) -> None:
        """Increase the algorithm's progress by the provided value.

        Args:
            increment (float): Percentage to increase by

        Raises:
            ValueError: If ``increment` increases self._percent over 100%

        """

        if self._percent + increment > 100:
            raise ValueError("Incrementing the algorithm's progress by " + str(increment) + "% has increased the "
                             + "algorithm's progress to over 100% (" + str(self._percent + increment) + "%)")

        self._percent += increment

        # Update GUI with new percentage completed
        if self._progress_callback is not None:
            self._progress_callback.emit(self._tab, self._percent)
            self._continue_thread = self._image_data.continue_thread

    def _get_increment_percent(self, final_percent: int, steps: int) -> float:
        """Calculates and returns the percentage increment to reach the`final_percent` in a certain number of `steps`.

        Args:
            final_percent (int): New final percentage
            steps (int): The number of steps to reach the final percentage

        Returns:
            float: The value of the necessary incremental size

        Raises:
            ValueError: If `final_percent' is greater than 100 or is greater than the current percentage

        """

        if final_percent > 100 or final_percent < self._percent:
            raise ValueError("The final percent (" + str(final_percent) + ") must be less than 100% but greater than "
                             + "the current percent (" + str(self._percent) + ")")

        current_percent = self._percent
        return (final_percent - current_percent) / steps

    def _set_progress(self, new_progress: float) -> None:
        """Set the algorithm progress to a new value and possibly notify the GUI of the change.

        Args:
            new_progress (float):

        Raises:
            ValueError: If the new progress is greater than 100%

        """

        if new_progress > 100:
            raise ValueError("Algorithm's progress cannot be larger than 100%.")

        self._percent = new_progress
        if self._progress_callback is not None:
            self._progress_callback.emit(self._tab, self._percent)
            self._continue_thread = self._image_data.continue_thread
