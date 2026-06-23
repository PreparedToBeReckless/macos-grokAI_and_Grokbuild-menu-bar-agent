#!/bin/zsh
# Launch the latest test-install copy of Grok Overlay.
set -euo pipefail

SCRIPT_DIR=${0:a:h}
APP_PATH="$SCRIPT_DIR/test-install/Grok Overlay.app"

if [[ ! -d "$APP_PATH" ]]; then
    echo "No test app found. Build one first:"
    echo "  cd \"$SCRIPT_DIR\" && ./build-dmg.sh"
    exit 1
fi

if [[ -f "$SCRIPT_DIR/test-install/VERSION.txt" ]]; then
    echo "Launching test install ($(cat "$SCRIPT_DIR/test-install/VERSION.txt" | head -1))..."
else
    echo "Launching test install..."
fi

open -n "$APP_PATH"