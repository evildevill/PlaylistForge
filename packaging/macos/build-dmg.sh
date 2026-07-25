#!/usr/bin/env bash
# Build a PlaylistForge .dmg for macOS.
# Run this from the project root: bash packaging/macos/build-dmg.sh

set -euo pipefail

APP="PlaylistForge"
VERSION="0.4.0"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> Building ${APP} v${VERSION} for macOS"

echo "==> Step 1: Install dependencies"
python3 -m pip install -e "${ROOT}[dev]"

echo "==> Step 2: PyInstaller .app bundle"
pyinstaller \
    "${ROOT}/packaging/pyinstaller/playlistforge.macos.spec" \
    --clean --noconfirm

APP_BUNDLE="${ROOT}/dist/${APP}.app"
if [ ! -d "${APP_BUNDLE}" ]; then
    echo "Error: ${APP_BUNDLE} not found. PyInstaller build failed."
    exit 1
fi

echo "==> Step 3: Codesign the .app (if identity is available)"
if [ -n "${APPLE_SIGN_IDENTITY:-}" ]; then
    codesign --deep --force --options runtime \
        --sign "${APPLE_SIGN_IDENTITY}" \
        "${APP_BUNDLE}"
    echo "    Signed with identity: ${APPLE_SIGN_IDENTITY}"
else
    echo "    Skipping codesign (APPLE_SIGN_IDENTITY not set)"
    echo "    Export APPLE_SIGN_IDENTITY for production builds."
fi

echo "==> Step 4: Create DMG"
DMG_PATH="${ROOT}/dist/${APP}-${VERSION}.dmg"
STAGING="${ROOT}/build/dmg-staging"
rm -rf "${STAGING}"
mkdir -p "${STAGING}"

# Create a symlink to /Applications for drag-and-drop install
ln -s /Applications "${STAGING}/Applications"
cp -R "${APP_BUNDLE}" "${STAGING}/"

if command -v create-dmg &>/dev/null; then
    DMG_OPTS=(
        --volname "${APP}"
        --window-size 640 420
        --app-drop-link 480 200
        --icon-size 128
    )
    if [ -f "${ROOT}/packaging/icons/playlistforge.icns" ]; then
        DMG_OPTS+=(--volicon "${ROOT}/packaging/icons/playlistforge.icns")
    fi
    create-dmg \
        "${DMG_OPTS[@]}" \
        --add-file "${APP}.app" "${STAGING}/${APP}.app" 180 200 \
        --add-file "Applications" "${STAGING}/Applications" 480 200 \
        "${DMG_PATH}" \
        "${STAGING}"
elif command -v hdiutil &>/dev/null; then
    # Fallback using hdiutil
    DMG_TMP="${ROOT}/build/${APP}-tmp.dmg"
    hdiutil create \
        -volname "${APP}" \
        -srcfolder "${STAGING}" \
        -ov \
        -format UDZO \
        "${DMG_TMP}"
    mv "${DMG_TMP}" "${DMG_PATH}"
else
    echo "Error: Neither create-dmg nor hdiutil found."
    exit 1
fi

rm -rf "${STAGING}"

echo "==> Step 5: Notarize (if credentials are set)"
if [ -n "${APPLE_ID:-}" ] && [ -n "${APPLE_TEAM_ID:-}" ] && [ -n "${APPLE_APP_PASSWORD:-}" ]; then
    echo "    Submitting for notarization..."
    xcrun notarytool submit "${DMG_PATH}" \
        --apple-id "${APPLE_ID}" \
        --team-id "${APPLE_TEAM_ID}" \
        --password "${APPLE_APP_PASSWORD}" \
        --wait
    echo "    Stapling notarization ticket..."
    xcrun stapler staple "${DMG_PATH}"
else
    echo "    Skipping notarization (APPLE_ID / APPLE_TEAM_ID / APPLE_APP_PASSWORD not set)"
    echo "    Export these env vars for production builds."
fi

echo "==> Done: ${DMG_PATH}"
ls -lh "${DMG_PATH}"
