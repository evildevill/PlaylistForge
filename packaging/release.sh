#!/usr/bin/env bash
# Create a new PlaylistForge release tag and push it.
# Usage: bash packaging/release.sh 0.2.0

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: bash packaging/release.sh <version>"
    echo "Example: bash packaging/release.sh 0.2.0"
    exit 1
fi

VERSION="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Validate semver format
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Error: '$VERSION' is not a valid semver (e.g. 0.2.0)"
    exit 1
fi

echo "==> Releasing PlaylistForge v${VERSION}"

# Check we're on main/master
BRANCH="$(git -C "${ROOT}" rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ]; then
    echo "Error: must be on main or master (currently on ${BRANCH})"
    exit 1
fi

# Check working tree is clean
if ! git -C "${ROOT}" diff --quiet --exit-code; then
    echo "Error: working tree is not clean. Commit or stash changes first."
    exit 1
fi

# Update version in __init__.py
INIT_FILE="${ROOT}/playlistforge/__init__.py"
sed -i "s/__version__ = \".*\"/__version__ = \"${VERSION}\"/" "${INIT_FILE}"
echo "    Updated version in ${INIT_FILE}"

# Update version in all spec files
for spec in "${ROOT}/packaging/pyinstaller/"*.spec; do
    sed -i "s/bundle_identifier=.*/bundle_identifier=\"com.playlistforge.app\",/" "$spec"
done

# Update version in DEBIAN control
CONTROL="${ROOT}/packaging/linux/DEBIAN/control"
sed -i "s/Version: .*/Version: ${VERSION}/" "${CONTROL}"
echo "    Updated version in ${CONTROL}"

# Update version in Inno Setup script
ISS="${ROOT}/packaging/windows/playlistforge.iss"
sed -i "s/#define MyAppVersion \".*\"/#define MyAppVersion \"${VERSION}\"/" "${ISS}"
echo "    Updated version in ${ISS}"

# Update version in all build scripts
for script in "${ROOT}/packaging/linux/"build-*.sh "${ROOT}/packaging/macos/"*.sh; do
    if [ -f "$script" ]; then
        sed -i "s/VERSION=\".*\"/VERSION=\"${VERSION}\"/" "$script"
    fi
done
echo "    Updated version in build scripts"

# Commit version bump
git -C "${ROOT}" add \
    "${INIT_FILE}" \
    "${CONTROL}" \
    "${ISS}" \
    "${ROOT}/packaging/linux/build-dpkg.sh" \
    "${ROOT}/packaging/macos/build-dmg.sh"

git -C "${ROOT}" commit -m "Bump version to ${VERSION}"
echo "    Committed version bump"

# Create tag
git -C "${ROOT}" tag -a "v${VERSION}" -m "PlaylistForge v${VERSION}"
echo "    Created tag v${VERSION}"

echo ""
echo "==> Ready to push:"
echo "    git push origin main --follow-tags"
echo ""
echo "    GitHub Actions will build all platform installers automatically."
