#!/usr/bin/env bash
# Build a PlaylistForge .deb package for Debian/Ubuntu.
# Run this from the project root: bash packaging/linux/build-dpkg.sh

set -euo pipefail

APP="PlaylistForge"
VERSION="0.3.0"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

BUILD_DIR="${ROOT}/build/dpkg/${APP}-${VERSION}"
DESTDIR="${BUILD_DIR}/debian/${APP}"

echo "==> Cleaning build directory"
rm -rf "${BUILD_DIR}"
mkdir -p "${DESTDIR}/DEBIAN"
mkdir -p "${DESTDIR}/usr/bin"
mkdir -p "${DESTDIR}/usr/share/applications"
mkdir -p "${DESTDIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${DESTDIR}/usr/share/icons/hicolor/128x128/apps"
mkdir -p "${DESTDIR}/usr/share/icons/hicolor/64x64/apps"
mkdir -p "${DESTDIR}/usr/share/icons/hicolor/48x48/apps"
mkdir -p "${DESTDIR}/usr/share/doc/${APP,,}"

echo "==> Copying control file"
cp "${ROOT}/packaging/linux/DEBIAN/control" "${DESTDIR}/DEBIAN/control"

echo "==> Copying desktop entry"
cp "${ROOT}/packaging/linux/playlistforge.desktop" \
   "${DESTDIR}/usr/share/applications/playlistforge.desktop"

echo "==> Copying icons"
cp "${ROOT}/packaging/icons/playlistforge.svg" \
   "${DESTDIR}/usr/share/icons/hicolor/scalable/apps/playlistforge.svg"

# Generate PNG icons from SVG (requires librsvg or Inkscape)
if command -v rsvg-convert &>/dev/null; then
    rsvg-convert -w 128 -h 128 \
        "${ROOT}/packaging/icons/playlistforge.svg" \
        -o "${DESTDIR}/usr/share/icons/hicolor/128x128/apps/playlistforge.png"
    rsvg-convert -w 64 -h 64 \
        "${ROOT}/packaging/icons/playlistforge.svg" \
        -o "${DESTDIR}/usr/share/icons/hicolor/64x64/apps/playlistforge.png"
    rsvg-convert -w 48 -h 48 \
        "${ROOT}/packaging/icons/playlistforge.svg" \
        -o "${DESTDIR}/usr/share/icons/hicolor/48x48/apps/playlistforge.png"
elif command -v inkscape &>/dev/null; then
    inkscape -w 128 -h 128 \
        "${ROOT}/packaging/icons/playlistforge.svg" \
        -o "${DESTDIR}/usr/share/icons/hicolor/128x128/apps/playlistforge.png"
    inkscape -w 64 -h 64 \
        "${ROOT}/packaging/icons/playlistforge.svg" \
        -o "${DESTDIR}/usr/share/icons/hicolor/64x64/apps/playlistforge.png"
    inkscape -w 48 -h 48 \
        "${ROOT}/packaging/icons/playlistforge.svg" \
        -o "${DESTDIR}/usr/share/icons/hicolor/48x48/apps/playlistforge.png"
else
    echo "Warning: rsvg-convert/inkscape not found. Skipping PNG icon generation."
    echo "Install librsvg (librsvg2-bin) or Inkscape for proper icon support."
fi

echo "==> Installing Python package with pip to DESTDIR prefix"
pip install \
    --target="${DESTDIR}/usr/lib/playlistforge" \
    --no-compile \
    --no-deps \
    "${ROOT}"

# Create wrapper script that adds our lib to PYTHONPATH
cat > "${DESTDIR}/usr/bin/playlistforge" << 'WRAPPER'
#!/usr/bin/env bash
PYTHONPATH="/usr/lib/playlistforge${PYTHONPATH:+:}${PYTHONPATH}"
export PYTHONPATH
exec /usr/bin/python3 -m playlistforge "$@"
WRAPPER
chmod 755 "${DESTDIR}/usr/bin/playlistforge"

echo "==> Copying copyright and changelog"
cat > "${DESTDIR}/usr/share/doc/${APP,,}/copyright" << 'COPYRIGHT'
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: PlaylistForge
Upstream-Contact: PlaylistForge Contributors
Source: https://github.com/playlistforge/playlistforge

Files: *
Copyright: 2026 PlaylistForge Contributors
License: MIT

License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
COPYRIGHT

echo "==> Setting permissions"
find "${DESTDIR}" -type d -exec chmod 755 {} \;
find "${DESTDIR}" -type f -exec chmod 644 {} \;
chmod 755 "${DESTDIR}/usr/bin/playlistforge"
chmod 755 "${DESTDIR}/DEBIAN"

echo "==> Building .deb package"
mkdir -p "${ROOT}/dist"
dpkg-deb --root-owner-group --build "${DESTDIR}" "${ROOT}/dist/${APP,,}_${VERSION}_all.deb"

echo "==> Done: dist/${APP,,}_${VERSION}_all.deb"
