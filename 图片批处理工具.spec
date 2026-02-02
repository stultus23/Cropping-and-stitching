# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all
import os
import sys

# 收集完整的模块（包括代码、数据和二进制文件）
datas = []
binaries = []
hiddenimports = []

# 完整收集 customtkinter
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# 收集其他依赖
datas += collect_data_files('darkdetect')
hiddenimports += collect_submodules('PIL')
hiddenimports += collect_submodules('tkinter')
hiddenimports += [
    'PIL._imaging', 
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'darkdetect',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
    'tkinter',
    'tkinter.ttk',
    '_tkinter',
]

a = Analysis(
    ['image_processor.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy'],
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
