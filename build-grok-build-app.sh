#!/bin/zsh
# Build Grok Build.app — native Swift terminal host running `agent` in its own process.
set -euo pipefail

SCRIPT_DIR=${0:a:h}
APP_NAME="Grok Build"
NATIVE_DIR="$SCRIPT_DIR/grok-build-native"
DIST_APP="$SCRIPT_DIR/dmg-builder/dist/${APP_NAME}.app"
MACOS_DIR="$DIST_APP/Contents/MacOS"
CONTENTS_DIR="$DIST_APP/Contents"
BUILD_DIR="$NATIVE_DIR/build"
BINARY_NAME="GrokBuild"
ICON_SRC="$SCRIPT_DIR/macos_grok_overlay/logo/icon.icns"
SDK=$(xcrun --show-sdk-path)

if [[ ! -d "$NATIVE_DIR/vendor/SwiftTerm" ]]; then
    echo "Fetching SwiftTerm sources..."
    git clone --depth 1 --branch 1.5.0 https://github.com/migueldeicaza/SwiftTerm.git "$NATIVE_DIR/vendor/SwiftTerm"
fi

mkdir -p "$BUILD_DIR"
find "$NATIVE_DIR/vendor/SwiftTerm/Sources/SwiftTerm" -name '*.swift' \
    ! -path '*/iOS/*' ! -path '*/tvOS/*' ! -path '*/visionOS/*' > "$BUILD_DIR/sources.rsp"
find "$NATIVE_DIR/Sources/GrokBuild" -name '*.swift' >> "$BUILD_DIR/sources.rsp"

echo "Compiling native Grok Build..."
swiftc -O -sdk "$SDK" \
    -o "$BUILD_DIR/$BINARY_NAME" \
    "@$BUILD_DIR/sources.rsp" \
    -framework AppKit -framework CoreGraphics -framework CoreText -framework Carbon

rm -rf "$DIST_APP"
mkdir -p "$MACOS_DIR"
cp "$BUILD_DIR/$BINARY_NAME" "$MACOS_DIR/$BINARY_NAME"
chmod +x "$MACOS_DIR/$BINARY_NAME"

if [[ -f "$ICON_SRC" ]]; then
    cp "$ICON_SRC" "$CONTENTS_DIR/icon.icns"
fi

if [[ -z "${PYTHON_BIN:-}" || ! -x "${PYTHON_BIN}" ]]; then
    for candidate in /opt/homebrew/bin/python3.12 /usr/local/bin/python3.12 python3; do
        if [[ -x "$candidate" ]]; then
            PYTHON_BIN="$candidate"
            break
        fi
    done
fi

"$PYTHON_BIN" - <<PY
import plistlib
from pathlib import Path

contents = Path("$CONTENTS_DIR")
plist = {
    "CFBundleDevelopmentRegion": "English",
    "CFBundleExecutable": "$BINARY_NAME",
    "CFBundleIdentifier": "com.grokoverlay.grokbuild",
    "CFBundleInfoDictionaryVersion": "6.0",
    "CFBundleName": "Grok Build",
    "CFBundleDisplayName": "Grok Build",
    "CFBundlePackageType": "APPL",
    "CFBundleShortVersionString": "2.0",
    "CFBundleVersion": "9",
    "LSMinimumSystemVersion": "13.0",
    "NSHighResolutionCapable": True,
    "NSAppleScriptEnabled": True,
    "NSHumanReadableCopyright": (
        "Fork of macos-grok-overlay by Thomas C.H. Lux (tchlux). "
        "Grok Build added by reckless using Grok (xAI). See ATTRIBUTION.md."
    ),
}
if (contents / "icon.icns").exists():
    plist["CFBundleIconFile"] = "icon.icns"

with open(contents / "Info.plist", "wb") as handle:
    plistlib.dump(plist, handle)
PY

printf 'APPL????' > "$CONTENTS_DIR/PkgInfo"

if command -v codesign >/dev/null 2>&1; then
    codesign --force --sign - "$DIST_APP" >/dev/null 2>&1 || true
fi

echo "Built $DIST_APP"