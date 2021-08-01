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


__version__ = "0.5.5"
"""Version number of the application."""

__author__ = "Tim Churchfield"
"""Author of the application."""

__organisation__ = "The University of St Andrews"
"""Organisation associated with the application."""

__application_name__ = "ColourPaletteExtractor"
"""Name of the application."""

__VERBOSE__ = True
"""Turn on/off generation print statements to the terminal."""


def get_header() -> str:
    """Returns a brief description of the application, the copyright year, the author and the application' version.

    Returns:
        (str): System description.

    """
    header = __application_name__ + " is a simple tool to generate the colour palette of an image. \n \n" + \
              "    Copyright (C) 2021 " + __author__ + " \n \n" + \
              "    Version " + __version__ + "\n"

    return header


def get_licence() -> str:
    """Returns the short version of the licence associated with the application.

    Returns:
        (str): The licence.

    """
    licence = "This program is free software: you can redistribute it and/or modify it under the terms of the GNU " + \
              "General Public License as published by the Free Software Foundation, either version 3 of the " + \
              "License, or (at your option) any later version. \n \n" + \
              "This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without " + \
              "even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the " + \
              "GNU General Public License for more details. \n \n" + \
              "You should have received a copy of the GNU General Public License along with this program. " + \
              "If not, see <https://www.gnu.org/licenses/>."

    return licence


def print_version() -> None:
    """Prints the current version number of the application to the terminal."""
    print(__version__)


if __name__ == '__main__':
    """Prints the current version number of the application to the terminal."""
    print_version()
