#!/bin/zsh
# Build Grok Overlay.app and package it as a drag-to-install DMG.
set -euo pipefail

SCRIPT_DIR=${0:a:h}
APP_NAME="Grok Overlay"
DMG_NAME="Grok-Overlay"
VERSION=$(cat "$SCRIPT_DIR/macos_grok_overlay/about/version.txt")
OUTPUT_DMG="$SCRIPT_DIR/${DMG_NAME}-${VERSION}.dmg"
STAGING_DIR=$(mktemp -d)

cleanup() {
    rm -rf "$STAGING_DIR"
}
trap cleanup EXIT

if [[ -z "${PYTHON_BIN:-}" || ! -x "${PYTHON_BIN}" ]]; then
    for candidate in /opt/homebrew/bin/python3.12 /usr/local/bin/python3.12; do
        if [[ -x "$candidate" ]]; then
            PYTHON_BIN="$candidate"
            break
        fi
    done
fi
if [[ -z "${PYTHON_BIN:-}" || ! -x "${PYTHON_BIN}" ]]; then
    echo "Python 3.12 not found. Install with: brew install python@3.12"
    exit 1
fi
export PYTHON_BIN

echo "Building ${APP_NAME}.app..."
cd "$SCRIPT_DIR"
PY2APP_ARCH=${PY2APP_ARCH:-arm64} zsh build-app.sh

echo "Building Grok Build.app..."
zsh build-grok-build-app.sh

APP_PATH="$SCRIPT_DIR/dmg-builder/dist/${APP_NAME}.app"
BUILD_APP_PATH="$SCRIPT_DIR/dmg-builder/dist/Grok Build.app"
if [[ ! -d "$APP_PATH" ]]; then
    echo "Expected app bundle at: $APP_PATH"
    exit 1
fi
if [[ ! -d "$BUILD_APP_PATH" ]]; then
    echo "Expected app bundle at: $BUILD_APP_PATH"
    exit 1
fi

echo "Preparing DMG contents..."
ditto --norsrc "$APP_PATH" "$STAGING_DIR/${APP_NAME}.app"
ditto --norsrc "$BUILD_APP_PATH" "$STAGING_DIR/Grok Build.app"
cp "$SCRIPT_DIR/ATTRIBUTION.md" "$STAGING_DIR/ATTRIBUTION.md"
ln -s /Applications "$STAGING_DIR/Applications"

rm -f "$OUTPUT_DMG" "${OUTPUT_DMG%.dmg}-temp.dmg"

if command -v create-dmg >/dev/null 2>&1; then
    echo "Creating DMG with create-dmg..."
    create-dmg \
        --volname "$APP_NAME" \
        --window-size 600 320 \
        --icon-size 96 \
        --app-drop-link 430 170 \
        --hide-extension "${APP_NAME}.app" \
        "$OUTPUT_DMG" \
        "$STAGING_DIR"
else
    echo "create-dmg not found; using hdiutil fallback..."
    hdiutil create \
        -volname "$APP_NAME" \
        -srcfolder "$STAGING_DIR" \
        -ov \
        -format UDZO \
        "$OUTPUT_DMG"
fi

# Optional local test copy; do not fail the DMG build if this step errors.
if [[ -x "$SCRIPT_DIR/sync-test-install.sh" ]]; then
    zsh "$SCRIPT_DIR/sync-test-install.sh" || true
fi

echo ""
echo "DMG ready:"
echo "  $OUTPUT_DMG"
echo ""
echo "Install: open the DMG, then drag '${APP_NAME}' and 'Grok Build' to Applications."