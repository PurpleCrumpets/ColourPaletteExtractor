# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['__main__.py'],
             pathex=['/Users/tim/OneDrive - University of St Andrews/University/MScProject/ColourPaletteExtractor/colourpaletteextractor'],
             binaries=[],
             datas=[('./view/resources', 'resources')],
             hiddenimports=[],
             hookspath=[],
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
          console=False , icon='app_icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ColourPaletteExtractor')
app = BUNDLE(coll,
             name='ColourPaletteExtractor.app',
             icon='app_icon.icns',
             bundle_identifier=None,
             version='0.2')