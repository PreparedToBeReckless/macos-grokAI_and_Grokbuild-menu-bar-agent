#!/bin/zsh
# py2app 0.28.x does not fully bundle Python 3.15's lib-dynload extensions.
# Copy them into the embedded framework so the app can launch.
set -euo pipefail

APP_PATH="$1"
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
DYNLOAD_SRC=$(python3 -c "import sysconfig; print(sysconfig.get_path('platstdlib'))")/lib-dynload
DYNLOAD_DST="${APP_PATH}/Contents/Frameworks/Python.framework/Versions/${PYTHON_VERSION}/lib/python${PYTHON_VERSION}/lib-dynload"

if [[ ! -d "$DYNLOAD_SRC" ]]; then
    echo "No lib-dynload source at ${DYNLOAD_SRC}; skipping stdlib fix."
    exit 0
fi

mkdir -p "$DYNLOAD_DST"
ditto "$DYNLOAD_SRC" "$DYNLOAD_DST"
echo "Copied Python ${PYTHON_VERSION} lib-dynload extensions into app bundle."