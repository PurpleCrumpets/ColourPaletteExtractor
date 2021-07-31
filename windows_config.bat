@echo off

REM ColourPaletteExtractor is a simple tool to generate the colour palette of an image.
REM Copyright (C) 2021  Tim Churchfield
REM
REM This program is free software: you can redistribute it and/or modify
REM it under the terms of the GNU General Public License as published by
REM the Free Software Foundation, either version 3 of the License, or
REM (at your option) any later version.
REM
REM This program is distributed in the hope that it will be useful,
REM but WITHOUT ANY WARRANTY; without even the implied warranty of
REM MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM GNU General Public License for more details.
REM
REM You should have received a copy of the GNU General Public License
REM along with this program.  If not, see <https://www.gnu.org/licenses/>.

REM #########################
REM ## Windows 10 Settings ##
REM #########################

REM Path to the Python virtual environment (provide absolute path to the 'activate' file)
set PYTHON_VIRTUAL_ENVIRONMENT_PATH=C:\Users\timch\PycharmProjects\MSc-CS-Project---ColourPaletteExtractor\venv\Scripts\activate

REM Path to PyInstaller executables output directory
set EXECUTABLE_OUTPUT_DIRECTORY=C:\Users\timch\PycharmProjects\MSc-CS-Project---ColourPaletteExtractor\ColourPaletteExtractor-Executables
