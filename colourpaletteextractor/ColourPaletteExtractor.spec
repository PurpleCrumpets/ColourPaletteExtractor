# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import importlib

block_cipher = None

# Adding necessary resource files
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


a = Analysis(['__main__.py'],
             pathex=['C:\\Users\\timch\\PycharmProjects\\MSc-CS-Project---ColourPaletteExtractor\\colourpaletteextractor'],
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
             version='0.2',
             info_plist={
               'NSPrincipalClass': 'NSApplication',
               'NSAppleScriptEnabled': False,
               'NSRequiresAquaSystemAppearance': False
                },
             )

