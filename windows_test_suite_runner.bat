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

REM ###################################################################
REM ## Run the ColourPaletteExtractor Python Test Suite - Windows 10 ##
REM ###################################################################

echo Loading settings from windows_config.bat...
call windows_config.bat

REM Python Virtual Environment directory
set VENV_DIR=%PYTHON_VIRTUAL_ENVIRONMENT_PATH%

echo "Running test suite..."
call %VENV_DIR% && pytest colourpaletteextractor/tests

echo "Finished!"