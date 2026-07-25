#!/usr/bin/env bash
# Build a PlaylistForge AppImage using linuxdeploy.
# Run this from the project root: bash packaging/linux/build-appimage.sh

set -euo pipefail

APP="PlaylistForge"
VERSION="0.3.0"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD_DIR="${ROOT}/build/appimage"

echo "==> Cleaning build directory"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}/AppDir/usr/bin"
mkdir -p "${BUILD_DIR}/AppDir/usr/share/applications"
mkdir -p "${BUILD_DIR}/AppDir/usr/share/icons/hicolor/scalable/apps"

echo "==> Building with PyInstaller"
pyinstaller \
    "${ROOT}/packaging/pyinstaller/playlistforge.linux.spec" \
    --clean --noconfirm 2>&1 | tail -5

echo "==> Copying PyInstaller build into AppDir"
cp -r "${ROOT}/dist/PlaylistForge/"* "${BUILD_DIR}/AppDir/usr/bin/"
cp "${ROOT}/packaging/linux/playlistforge.desktop" \
   "${BUILD_DIR}/AppDir/usr/share/applications/playlistforge.desktop"
cp "${ROOT}/packaging/icons/playlistforge.svg" \
   "${BUILD_DIR}/AppDir/usr/share/icons/hicolor/scalable/apps/playlistforge.svg"
cp "${ROOT}/packaging/linux/playlistforge.desktop" \
   "${BUILD_DIR}/AppDir/playlistforge.desktop"
cp "${ROOT}/packaging/icons/playlistforge.svg" \
   "${BUILD_DIR}/AppDir/playlistforge.svg"

echo "==> Running linuxdeploy"
LINUXDEPLOY="${LINUXDEPLOY:-linuxdeploy-x86_64.AppImage}"
if command -v "${LINUXDEPLOY}" &>/dev/null; then
    "${LINUXDEPLOY}" \
        --appdir "${BUILD_DIR}/AppDir" \
        --desktop-file "${BUILD_DIR}/AppDir/playlistforge.desktop" \
        --icon-file "${BUILD_DIR}/AppDir/playlistforge.svg" \
        --output appimage
    echo "==> Done: PlaylistForge-x86_64.AppImage"
elif command -v appimagetool &>/dev/null; then
    ARCH=x86_64 appimagetool "${BUILD_DIR}/AppDir" \
        "${ROOT}/dist/${APP}-${VERSION}-x86_64.AppImage"
    echo "==> Done: dist/${APP}-${VERSION}-x86_64.AppImage"
else
    echo "==> AppDir prepared at ${BUILD_DIR}/AppDir"
    echo "==> Install linuxdeploy or appimagetool to create the AppImage."
    echo "    https://github.com/linuxdeploy/linuxdeploy"
fi
