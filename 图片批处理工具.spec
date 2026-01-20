# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('.venv/Lib/site-packages/customtkinter', 'customtkinter/')]
datas += collect_data_files('customtkinter')
datas += collect_data_files('darkdetect')


a = Analysis(
    ['image_processor.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['PIL', 'PIL._imaging', 'customtkinter', 'darkdetect'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='图片批处理工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='图片批处理工具',
)
