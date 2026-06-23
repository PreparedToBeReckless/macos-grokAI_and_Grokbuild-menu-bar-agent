#!/bin/zsh
# Build a local Grok Overlay.app (no Developer ID signing required).
set -euo pipefail

SCRIPT_DIR=${0:a:h}
cd "$SCRIPT_DIR/dmg-builder"
./test_build.sh

APP_PATH="$SCRIPT_DIR/dmg-builder/dist/Grok Overlay.app"
echo ""
echo "Done. Open with:"
echo "  open \"$APP_PATH\""