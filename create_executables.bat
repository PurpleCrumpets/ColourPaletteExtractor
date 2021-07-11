@echo off

REM Name of the executable
set NAME=ColourPaletteExtractor

REM Setting directories
REM Primary Working Directory
set MAIN_DIR=%cd%
echo %cd%
REM PyInstaller output directory
set OUTPUT_DIR=%MAIN_DIR%\ColourPaletteExtractor-Executables
REM Python Virtual Environment directory
set VENV_DIR=%MAIN_DIR%\venv

REM Build application
echo Building %NAME% app %OUTPUT_DIR% using __main__.py file...

REM Connect to virtual Python environment, run pyinstaller command
call %VENV_DIR%\Scripts\activate.bat & cd /d %MAIN_DIR%\colourpaletteextractor && pyinstaller __main__.py --onedir --clean --workpath %OUTPUT_DIR%\build --distpath %OUTPUT_DIR%\dist --add-data view\resources;resources --add-data app_icon.ico;. --name %NAME% --icon=app_icon.ico --windowed --noconfirm --onedir

REM Create a short-cut to the executable one level up
set EXE_PATH=%OUTPUT_DIR%\dist\%NAME%


echo Creating a short-cut to the executable...

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%OUTPUT_DIR%\dist\%NAME%.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%EXE_PATH%\%NAME%.exe" >> CreateShortcut.vbs
echo olink.WorkingDirectory = "%EXE_PATH%" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
call cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo Finished!



