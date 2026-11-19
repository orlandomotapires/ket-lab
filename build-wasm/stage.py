"""Collects what the browser engine downloads into one folder the site serves.

    python3 build-wasm/stage.py [output-dir]      (default: app/public/browser-engine)

Output:
  manifest.json   read by the Web Worker (app/src/engine/browser/worker.ts)
  wheels/         the PyPI wheels of wheels.json (checked against their SHA-256) and the
                  Qiskit wheel from build.sh (build-wasm/dist)
  engine.zip      qlp_engine (Python sources) and content/

Needs build.sh to have run. Downloads are cached in build-wasm/work/wheels.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# From Pyodide's own distribution (loaded with their dependencies by pyodide.loadPackage).
PYODIDE_PACKAGES = ["numpy", "scipy", "requests", "packaging", "typing-extensions", "termcolor"]


def main() -> None:
    out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "app" / "public" / "browser-engine"
    if out.exists():
        shutil.rmtree(out)
    (out / "wheels").mkdir(parents=True)

    wheels = [_pypi_wheel(entry, out / "wheels") for entry in json.loads((HERE / "wheels.json").read_text())["wheels"]]
    built = sorted((HERE / "dist").glob("qiskit-*-pyemscripten_*_wasm32.whl"))
    if len(built) != 1:
        sys.exit("Expected exactly one Qiskit wheel in build-wasm/dist: run build-wasm/build.sh first.")
    shutil.copy2(built[0], out / "wheels" / built[0].name)
    wheels.append(built[0].name)

    _bundle(out / "engine.zip")
    pyodide = json.loads((HERE / "package.json").read_text())["devDependencies"]["pyodide"]
    manifest = {
        "pyodide": pyodide,
        "packages": PYODIDE_PACKAGES,
        "wheels": [f"wheels/{name}" for name in wheels],
        "bundle": "engine.zip",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"staged {len(wheels)} wheels and the engine bundle in {out} ({size / 2**20:.1f} MB)")


def _pypi_wheel(entry: dict, target: Path) -> str:
    cache = HERE / "work" / "wheels" / entry["file"]
    if not cache.is_file() or _sha256(cache) != entry["sha256"]:
        cache.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(entry["url"]) as response:
            cache.write_bytes(response.read())
    if _sha256(cache) != entry["sha256"]:
        sys.exit(f"{entry['file']}: SHA-256 does not match wheels.json")
    shutil.copy2(cache, target / entry["file"])
    return entry["file"]


def _bundle(path: Path) -> None:
    """qlp_engine/*.py and content/, at the paths the worker puts on sys.path."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for source in sorted((ROOT / "engine" / "qlp_engine").rglob("*.py")):
            archive.write(source, source.relative_to(ROOT / "engine").as_posix())
        for source in sorted((ROOT / "content").rglob("*")):
            if source.is_file() and "__pycache__" not in source.parts:
                archive.write(source, source.relative_to(ROOT).as_posix())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    main()
