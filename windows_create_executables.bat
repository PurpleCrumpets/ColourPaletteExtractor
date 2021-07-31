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

REM ##################################################################
REM ## Create the ColourPaletteExtractor application for Windows 10 ##
REM ##################################################################


echo Loading settings from windows_config.bat...
call windows_config.bat

REM Primary Working Directory
set MAIN_DIR=%cd%

REM Python Virtual Environment directory
set VENV_DIR=%PYTHON_VIRTUAL_ENVIRONMENT_PATH%

REM PyInstaller output directory
set OUTPUT_DIR=%EXECUTABLE_OUTPUT_DIRECTORY%

REM ############################
REM ############################

REM Name of the executable
set NAME=ColourPaletteExtractor

REM Name and path of expected PyInstaller SPEC file
set SPEC_FILE_PATH=%MAIN_DIR%\colourpaletteextractor\%NAME%.spec

REM Spec file find and replace details
set FILE_NAME="%NAME%.spec"
set PATTERN="pathex=\['(.*)'\]"
set REPLACEMENT="pathex=['%MAIN_DIR%\colourpaletteextractor']"
set REPLACEMENT=%REPLACEMENT:\=\\%
set FIND_AND_REPLACE="%MAIN_DIR%\find_and_replace.ps1"


REM Build application
echo Building %NAME% app %OUTPUT_DIR%...
cd /d .\colourpaletteextractor


IF EXIST %SPEC_FILE_PATH% (
echo Spec file found! Using this to build the application!

REM Spec file find and replace pathex for Windows
PowerShell.exe -ExecutionPolicy Bypass -File %FIND_AND_REPLACE% %FILE_NAME% %PATTERN% %REPLACEMENT%

REM Connect to virtual Python environment, run pyinstaller command
call %VENV_DIR% && ^
pyinstaller %SPEC_FILE_PATH% ^
--clean ^
--workpath %OUTPUT_DIR%\build ^
--distpath %OUTPUT_DIR%\dist ^
--noconfirm

) ELSE (

    echo Spec file not found! Building application from scratch!
    echo Once built, please run this file again to add in version information...
    echo Please be aware that the application may not run correctly or even open if the custom spec file cannot be found...

REM Connect to virtual Python environment, run pyinstaller command
call %VENV_DIR%\Scripts\activate.bat & ^
cd /d %MAIN_DIR%\colourpaletteextractor && ^
pyinstaller __main__.py ^
--onedir ^
--clean ^
--workpath %OUTPUT_DIR%\build ^
--distpath %OUTPUT_DIR%\dist ^
--add-data view\resources;resources ^
--add-data app_icon.ico;. ^
--name %NAME% ^
--icon=app_icon.ico ^
--windowed ^
--noconfirm ^
--onedir

)

REM Create a short-cut to the executable one level up
echo Creating a short-cut to the executable...

set EXE_PATH=%OUTPUT_DIR%\dist\%NAME%

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%OUTPUT_DIR%\dist\%NAME%.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%EXE_PATH%\%NAME%.exe" >> CreateShortcut.vbs
echo olink.WorkingDirectory = "%EXE_PATH%" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
call cscript CreateShortcut.vbs
del CreateShortcut.vbs


REM Add a copy of the README.md to the distribution folder
set README=%MAIN_DIR%\README.md

IF EXIST %README% (
    echo "README.md found and added to the chosen distribution directory..."
    copy %README% %OUTPUT_DIR%\dist
) ELSE (
    echo "README.md not found..."
)


REM Add a copy of the LICENCE.md to the distribution folder
set LICENCE=%MAIN_DIR%\LICENCE.md

IF EXIST %LICENCE% (
    echo "LICENCE.md found and added to the chosen distribution directory..."
    copy %LICENCE% %OUTPUT_DIR%\dist
) ELSE (
    echo "LICENCE.md not found..."
)

echo Finished!
