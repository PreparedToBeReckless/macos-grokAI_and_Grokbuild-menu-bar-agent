#!/bin/zsh
# Remove build artifacts and old installers. Keeps source and the current-version DMG.
#
# Usage:
#   zsh clean.sh          # full clean (removes test-install; run build-dmg.sh after)
#   zsh clean.sh --keep   # cache-only clean (keeps dist/ and test-install/)
set -euo pipefail

SCRIPT_DIR=${0:a:h}
VERSION=$(cat "$SCRIPT_DIR/macos_grok_overlay/about/version.txt")
CURRENT_DMG="$SCRIPT_DIR/Grok-Overlay-${VERSION}.dmg"
KEEP_BUILDS=false
if [[ "${1:-}" == "--keep" ]]; then
    KEEP_BUILDS=true
fi

echo "Cleaning build artifacts..."

rm -rf \
    "$SCRIPT_DIR/dmg-builder/build" \
    "$SCRIPT_DIR/dmg-builder/env" \
    "$SCRIPT_DIR/grok-build-native/build" \
    "$SCRIPT_DIR/grok-build-native/vendor" \
    "$SCRIPT_DIR/macos_grok_overlay.egg-info"

if [[ "$KEEP_BUILDS" == false ]]; then
    rm -rf "$SCRIPT_DIR/test-install"
fi

find "$SCRIPT_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -name '*.pyc' -delete 2>/dev/null || true
find "$SCRIPT_DIR" -name '.DS_Store' -delete 2>/dev/null || true

echo "Removing old DMG installers (keeping ${VERSION})..."
for dmg in "$SCRIPT_DIR"/Grok-Overlay-*.dmg(N); do
    if [[ "$dmg" != "$CURRENT_DMG" ]]; then
        rm -f "$dmg"
    fi
done

rm -f "$SCRIPT_DIR/Grok-Overlay-latest.dmg"
if [[ -f "$CURRENT_DMG" ]]; then
    ln -sf "Grok-Overlay-${VERSION}.dmg" "$SCRIPT_DIR/Grok-Overlay-latest.dmg"
fi

echo ""
echo "Clean complete."
echo "  Kept DMG: Grok-Overlay-${VERSION}.dmg"
echo "  Latest link: Grok-Overlay-latest.dmg"
echo ""
echo "Rebuild with: zsh build-dmg.sh"