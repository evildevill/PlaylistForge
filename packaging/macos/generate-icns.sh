#!/usr/bin/env bash
# Generate playlistforge.icns from playlistforge.svg for macOS .app bundle.
# Uses only macOS built-in tools: sips + iconutil.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ICON_SVG="${ROOT}/packaging/icons/playlistforge.svg"
OUTPUT="${ROOT}/packaging/icons/playlistforge.icns"

# Only works on macOS with sips and iconutil
if ! command -v iconutil &>/dev/null || ! command -v sips &>/dev/null; then
    echo "iconutil/sips not available — skipping .icns generation (not macOS)."
    exit 0
fi

ICONSET_DIR="${ROOT}/build/playlistforge.iconset"
BASE_PNG="${ROOT}/build/icon-base.png"
mkdir -p "${ICONSET_DIR}"

# Step 1: Convert SVG to high-res PNG using Python + PySide6 (available in CI)
# QT_QPA_PLATFORM=offscreen allows Qt to run headlessly (no display required).
# QGuiApplication must be created before any Qt GUI objects (QImage, QPainter, etc.).
# QSvgRenderer renders SVG directly to QImage without needing QPixmap.
QT_QPA_PLATFORM=offscreen python3 -c "
import sys
from PySide6.QtGui import QGuiApplication, QPainter, QImage
from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgRenderer

app = QGuiApplication(sys.argv)
renderer = QSvgRenderer('${ICON_SVG}')
img = QImage(1024, 1024, QImage.Format.Format_ARGB32_Premultiplied)
img.fill(Qt.GlobalColor.transparent)
painter = QPainter(img)
renderer.render(painter)
painter.end()
img.save('${BASE_PNG}')
"

# Step 2: Resize to all required icon sizes using sips (macOS built-in)
for size in 16 32 64 128 256 512; do
    out="${ICONSET_DIR}/icon_${size}x${size}.png"
    out2x="${ICONSET_DIR}/icon_${size}x${size}@2x.png"
    sips -z "${size}" "${size}" "${BASE_PNG}" --out "${out}" &>/dev/null
    sips -z "$((size * 2))" "$((size * 2))" "${BASE_PNG}" --out "${out2x}" &>/dev/null
done

# Step 3: Convert iconset to .icns
iconutil -c icns "${ICONSET_DIR}" -o "${OUTPUT}"

rm -rf "${ICONSET_DIR}" "${BASE_PNG}"
echo "Created: ${OUTPUT}"
