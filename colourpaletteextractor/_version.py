#     ColourPaletteExtractor is a simple tool to generate the colour palette of an image.
#     Copyright (C) 2020  Tim Churchfield
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

__version__ = "0.5.3"
__author__ = "Tim Churchfield"
__organisation__ = "The University of St Andrews"
__application_name__ = "ColourPaletteExtractor"


def get_header():
    header = __application_name__ + " is a simple tool to generate the colour palette of an image. \n \n" + \
              "    Copyright (C) 2021 " + __author__ + " \n \n" + \
              "    Version " + __version__ + "\n"

    return header


def get_licence():
    licence = "This program is free software: you can redistribute it and/or modify it under the terms of the GNU " + \
              "General Public License as published by the Free Software Foundation, either version 3 of the " + \
              "License, or (at your option) any later version. \n \n" + \
              "This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without " + \
              "even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the " + \
              "GNU General Public License for more details. \n \n" + \
              "You should have received a copy of the GNU General Public License along with this program. " + \
              "If not, see <https://www.gnu.org/licenses/>."

    return licence


def print_version():
    print(__version__)


if __name__ == '__main__':
    print_version()
