# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

import os
from pathlib import Path

# Obtener la ruta base del proyecto (directorio donde está el spec)
spec_dir = os.path.dirname(os.path.abspath(SPECPATH))
bd_path = Path(spec_dir) / 'bd'

# Incluir carpeta bd con todos sus archivos JSON
bd_files = []
if bd_path.exists():
    for json_file in bd_path.glob('*.json'):
        # Ruta relativa desde el spec
        rel_path = os.path.relpath(json_file, spec_dir)
        bd_files.append((rel_path, 'bd'))

datas = [
    ('icon.ico', '.'),
] + bd_files
binaries = []
hiddenimports = ['win32com', 'win32com.shell', 'pythoncom', 'pywintypes']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['consulta_juegos_xbox.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.datas,
    [],
    name='consulta_juegos_xbox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
