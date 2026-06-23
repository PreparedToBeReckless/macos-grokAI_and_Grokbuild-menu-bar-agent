#!/bin/zsh
# Copy the freshly built apps into test-install/ for quick local testing.
set -euo pipefail

SCRIPT_DIR=${0:a:h}
OVERLAY_APP="Grok Overlay"
BUILD_APP="Grok Build"
TEST_DIR="$SCRIPT_DIR/test-install"
OVERLAY_PATH="$SCRIPT_DIR/dmg-builder/dist/${OVERLAY_APP}.app"
BUILD_PATH="$SCRIPT_DIR/dmg-builder/dist/${BUILD_APP}.app"
VERSION=$(cat "$SCRIPT_DIR/macos_grok_overlay/about/version.txt")

if [[ ! -d "$OVERLAY_PATH" ]]; then
    echo "sync-test-install: app bundle not found at $OVERLAY_PATH"
    exit 1
fi
if [[ ! -d "$BUILD_PATH" ]]; then
    echo "sync-test-install: app bundle not found at $BUILD_PATH"
    exit 1
fi

mkdir -p "$TEST_DIR"
rm -rf "$TEST_DIR/${OVERLAY_APP}.app" "$TEST_DIR/${BUILD_APP}.app"
ditto --norsrc "$OVERLAY_PATH" "$TEST_DIR/${OVERLAY_APP}.app"
ditto --norsrc "$BUILD_PATH" "$TEST_DIR/${BUILD_APP}.app"

{
    echo "version=$VERSION"
    echo "built_at=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo "overlay_source=$OVERLAY_PATH"
    echo "grok_build_source=$BUILD_PATH"
} > "$TEST_DIR/VERSION.txt"

echo ""
echo "Test install ready:"
echo "  $TEST_DIR/${OVERLAY_APP}.app"
echo "  $TEST_DIR/${BUILD_APP}.app"
echo "  Version: $VERSION"
echo ""
echo "Launch for testing:"
echo "  open \"$TEST_DIR/${OVERLAY_APP}.app\""