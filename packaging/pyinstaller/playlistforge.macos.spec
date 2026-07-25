# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for macOS .app bundle."""

import os
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("playlistforge")

SPEC_DIR = globals().get("SPECPATH", os.getcwd())
ICON_PATH = os.path.join(
    SPEC_DIR,
    "..", "icons", "playlistforge.icns",
)
if not os.path.isfile(ICON_PATH):
    ICON_PATH = None

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
    [],
    exclude_binaries=True,
    name="PlaylistForge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="PlaylistForge",
)

app = BUNDLE(
    coll,
    name="PlaylistForge.app",
    icon=ICON_PATH,
    bundle_identifier="com.playlistforge.app",
    info_plist={
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleVersion": "0.1.0",
        "CFBundleName": "PlaylistForge",
        "CFBundleDisplayName": "PlaylistForge",
        "CFBundleExecutable": "PlaylistForge",
        "CFBundlePackageType": "APPL",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSMinimumSystemVersion": "11.0",
    },
)
