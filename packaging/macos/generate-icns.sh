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
# PySide6 is always installed in the build env
python3 -c "
from PySide6.QtGui import QIcon, QPainter, QImage
from PySide6.QtCore import QSize, Qt
img = QImage(1024, 1024, QImage.Format.Format_ARGB32_Premultiplied)
img.fill(Qt.GlobalColor.transparent)
painter = QPainter(img)
icon = QIcon('${ICON_SVG}')
pix = icon.pixmap(QSize(1024, 1024))
painter.drawPixmap(0, 0, pix)
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
