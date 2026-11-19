#!/usr/bin/env bash
# Cross-compiles Qiskit to a WebAssembly wheel for Pyodide (the browser version of the engine).
# Output: build-wasm/dist/qiskit-<version>-cp310-abi3-pyemscripten_2026_0_wasm32.whl
#
# Requirements: Python 3.14 (must match Pyodide's; set PYTHON if it is not `python3.14`),
# rustup, curl. Work files stay in build-wasm/work (ignored by git); re-runnable.
# Recipe adapted from QisPlay (https://github.com/kriss-u/QisPlay, MIT). See .claude/docs/web-engine-decision.md.
set -euo pipefail
cd "$(dirname "$0")"

PYODIDE_VERSION=314.0.7     # keep in sync with package.json
PYODIDE_BUILD_VERSION=0.39.4
QISKIT_VERSION=2.6.2        # keep in sync with engine/pyproject.toml
QISKIT_SDIST_SHA256=b85b5f7b56700b864cc06dbfb33f01453a42024cf5ab954a0e0a275127ebd255
PYTHON=${PYTHON:-python3.14}

"$PYTHON" -c 'import sys; assert sys.version_info[:2] == (3, 14), sys.version' \
  || { echo "Python 3.14 is required (set PYTHON)." >&2; exit 1; }

mkdir -p work dist
WORK=$(pwd)/work

# --- toolchain -------------------------------------------------------------
if [ ! -x work/.venv/bin/pyodide ]; then
  "$PYTHON" -m venv work/.venv
  work/.venv/bin/python -m pip install -q "pyodide-build==$PYODIDE_BUILD_VERSION"
fi
# shellcheck disable=SC1091
. work/.venv/bin/activate
pyodide xbuildenv install "$PYODIDE_VERSION"
pyodide xbuildenv install-emscripten
RUST_TOOLCHAIN=$(pyodide config get rust_toolchain)
rustup toolchain install "$RUST_TOOLCHAIN" --profile minimal --target wasm32-unknown-emscripten
export RUSTUP_TOOLCHAIN=$RUST_TOOLCHAIN

# --- official source, checked against PyPI's hash ---------------------------
SDIST="$WORK/qiskit-$QISKIT_VERSION.tar.gz"
if [ ! -f "$SDIST" ]; then
  url=$(curl -sf "https://pypi.org/pypi/qiskit/$QISKIT_VERSION/json" |
    python3 -I -c "import json,sys;print([u['url'] for u in json.load(sys.stdin)['urls'] if u['packagetype']=='sdist'][0])")
  curl -sfL "$url" -o "$SDIST"
fi
echo "$QISKIT_SDIST_SHA256  $SDIST" | sha256sum -c -

SRC="$WORK/qiskit-$QISKIT_VERSION"
rm -rf "$SRC"
tar xzf "$SDIST" -C "$WORK"
patch -d "$SRC" -p1 < "patches/qiskit-$QISKIT_VERSION-emscripten.patch"

# --- build ------------------------------------------------------------------
rm -f dist/qiskit-*.whl
(cd "$SRC" && QISKIT_BUILD_PROFILE=release pyodide build -o "$(pwd -P)/../../dist" .)
sha256sum dist/qiskit-*.whl
