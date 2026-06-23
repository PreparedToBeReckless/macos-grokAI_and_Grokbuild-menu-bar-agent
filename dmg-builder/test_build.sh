#!/bin/zsh

# Minimal local build (no signing/notarization)
set -euo pipefail

APP_NAME="Grok Overlay"
ENTITLEMENTS="../macos_grok_overlay/entitlements.plist"

# py2app does not fully support Python 3.15 yet (missing lib-dynload modules).
# Prefer a system Python 3.12, never a stale dmg-builder/env interpreter.
resolve_python_bin() {
    local candidate
    for candidate in \
        "${PYTHON_BIN:-}" \
        /opt/homebrew/bin/python3.12 \
        /usr/local/bin/python3.12 \
        "$(command -v python3.12 2>/dev/null || true)" \
        "$(command -v python3 2>/dev/null || true)"; do
        [[ -n "$candidate" && -x "$candidate" ]] || continue
        case "$candidate" in
            *"/dmg-builder/env/"*) continue ;;
        esac
        print -r -- "$candidate"
        return 0
    done
    return 1
}

PYTHON_BIN=$(resolve_python_bin) || {
    echo "Could not find a usable Python 3.12+ interpreter."
    echo "Install with: brew install python@3.12"
    exit 1
}
echo "Using Python: $("$PYTHON_BIN" --version 2>&1) ($PYTHON_BIN)"

# Determine which architecture(s) to target (defaults to universal binary).
PY2APP_ARCH=${PY2APP_ARCH:-universal2}
case "$PY2APP_ARCH" in
    universal2)
        export ARCHFLAGS="-arch arm64 -arch x86_64"
        ;;
    arm64|x86_64)
        export ARCHFLAGS="-arch $PY2APP_ARCH"
        ;;
    *)
        echo "Unsupported PY2APP_ARCH value: $PY2APP_ARCH"
        echo "Use one of: arm64, x86_64, universal2."
        exit 1
        ;;
esac
echo "Local test build targeting architecture: $PY2APP_ARCH"

touch temp.egg-info env dist build 2> /dev/null
rm -rf env dist build *.egg-info || echo 'Nothing to delete.'
"$PYTHON_BIN" -m venv env
source env/bin/activate
python -m pip install --upgrade pip
python -m pip install setuptools==70.3.0 py2app -r ../macos_grok_overlay/about/requirements.txt

pushd .. >/dev/null
# Build a full (non-alias) app. py2app may fail at the final ad-hoc sign step on
# some filesystems; the bundle itself is still produced.
python setup.py py2app --arch "$PY2APP_ARCH" --dist-dir="dmg-builder/dist" --bdist-base="dmg-builder/build" || true
popd >/dev/null

APP_PATH="dist/${APP_NAME}.app"
if [[ ! -d "$APP_PATH" ]]; then
    echo "Build failed: ${APP_PATH} was not created."
    exit 1
fi

# Fallback for Python 3.15 builds where py2app omits new stdlib extensions.
PYTHON_MINOR=$(python -c "import sys; print(sys.version_info.minor)")
if [[ "$PYTHON_MINOR" -ge 15 ]]; then
    chmod +x fix_stdlib_dynload.sh
    ./fix_stdlib_dynload.sh "$APP_PATH"
fi

# Strip resource forks / Finder metadata that break codesign on Desktop/iCloud volumes.
CLEAN_DIR=$(mktemp -d)
ditto --norsrc "$APP_PATH" "$CLEAN_DIR/${APP_NAME}.app"
rm -rf "$APP_PATH"
ditto --norsrc "$CLEAN_DIR/${APP_NAME}.app" "$APP_PATH"
rm -rf "$CLEAN_DIR"

echo "Ad-hoc signing ${APP_PATH} (microphone entitlement included)."
find "$APP_PATH" -type f \( -name "*.so" -o -name "*.dylib" \) -exec codesign --force --sign - {} \; 2>/dev/null || true
codesign --force --sign - --entitlements "$ENTITLEMENTS" "$APP_PATH"

echo "Built app at $(pwd)/${APP_PATH}"