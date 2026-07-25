# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Windows onedir build."""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("playlistforge")

a = Analysis(
    ["../../playlistforge/__main__.py"],
    pathex=["../../"],
    binaries=[],
    datas=datas,
    hiddenimports=["yt_dlp", "openpyxl", "playlistforge"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "PIL",
        "cv2",
        "scipy",
        "notebook",
        "jupyter",
        "IPython",
        "setuptools",
        "pip",
    ],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PlaylistForge",
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
    icon="../../packaging/icons/playlistforge.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PlaylistForge",
)
