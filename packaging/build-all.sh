#!/usr/bin/env bash
# Build PlaylistForge for the current platform.
# Usage: bash packaging/build-all.sh [linux|windows|macos]

set -euo pipefail

APP="PlaylistForge"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

platform="${1:-}"
if [ -z "$platform" ]; then
    case "$(uname -s)" in
        Linux*)   platform="linux" ;;
        Darwin*)  platform="macos" ;;
        CYGWIN*|MINGW*|MSYS*) platform="windows" ;;
        *) echo "Unknown OS. Pass platform: linux, windows, or macos"; exit 1 ;;
    esac
fi

echo "==> Building ${APP} for ${platform}"
echo ""

case "$platform" in
    linux)
        # Option A: pip-installable .deb
        echo "A) Building .deb package..."
        bash "${ROOT}/packaging/linux/build-dpkg.sh"
        echo ""

        # Option B: PyInstaller AppImage
        echo "B) Building AppImage..."
        bash "${ROOT}/packaging/linux/build-appimage.sh" 2>&1 | tail -3
        ;;

    windows)
        if [ "$(uname -s)" != "MINGW"* ] && [ "$(uname -s)" != "MSYS"* ]; then
            echo "Windows builds must run on Windows."
            echo "Run: packaging\\windows\\build.bat"
            exit 1
        fi
        cmd //c "${ROOT}/packaging/windows/build.bat"
        ;;

    macos)
        bash "${ROOT}/packaging/macos/build-dmg.sh"
        ;;

    *)
        echo "Usage: bash packaging/build-all.sh [linux|windows|macos]"
        exit 1
        ;;
esac

echo ""
echo "==> Done. Artifacts in ${ROOT}/dist/"
ls -lh "${ROOT}/dist/" 2>/dev/null || true
