# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

import os
from pathlib import Path

# Obtener la ruta base del proyecto (directorio donde está el spec)
spec_dir = os.path.dirname(os.path.abspath(SPECPATH))
bd_path = Path(spec_dir) / 'bd'
icons_path = Path(spec_dir) / 'icons'

# Incluir carpeta bd con todos sus archivos JSON
bd_files = []
if bd_path.exists():
    for json_file in bd_path.glob('*.json'):
        # Ruta relativa desde el spec
        rel_path = os.path.relpath(json_file, spec_dir)
        bd_files.append((rel_path, 'bd'))

# Incluir carpeta icons con todos los iconos PNG
icons_files = []
if icons_path.exists():
    for icon_file in icons_path.glob('*.png'):
        # Ruta absoluta del archivo
        abs_path = str(icon_file)
        # Ruta de destino en el ejecutable (relativa a la carpeta del exe)
        icons_files.append((abs_path, 'icons'))

datas = [
    ('icon.ico', '.'),
] + bd_files + icons_files
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
    upx=False,  # Desactivar UPX para evitar problemas con el bootloader
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Cambiar a True temporalmente para ver errores
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
