# -*- mode: python ; coding: utf-8 -*-

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


import sys
from pathlib import Path
import importlib

# Adding necessary resource files
added_files = []
if sys.platform == "win32":
    added_files = [('view\\resources', 'resources'), ('app_icon.ico', '.')]
else:
    added_files = [('view/resources', 'resources'), ('app_icon.icns', '.')]


# qtmodern package resources
# Adapted from: https://github.com/gmarull/qtmodern/issues/34 (Jerkin, 10/12/2019)
# Accessed: 14/07/21
package_imports = [['qtmodern', ['resources/frameless.qss', 'resources/style.qss']]]
for package, files in package_imports:
    proot = Path(importlib.import_module(package).__file__).parent
    added_files.extend((proot / f, package) for f in files)

block_cipher = None


a = Analysis(['__main__.py'],
             pathex=['/Users/tim/OneDrive - University of St Andrews/University/MScProject/ColourPaletteExtractor/colourpaletteextractor'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='ColourPaletteExtractor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='app_icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ColourPaletteExtractor')

if sys.platform == "darwin":
    app = BUNDLE(coll,
             name='ColourPaletteExtractor.app',
             icon='app_icon.icns',
             bundle_identifier=None,
             version='0.5.5',
             info_plist={
               'NSPrincipalClass': 'NSApplication',
               'NSAppleScriptEnabled': False,
               'NSRequiresAquaSystemAppearance': False
                },
             )
