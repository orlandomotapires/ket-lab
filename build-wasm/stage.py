"""Collects what the browser engine downloads into one folder the site serves.

    python3 build-wasm/stage.py [output-dir]      (default: app/public/browser-engine)

Output:
  manifest.json   read by the Web Worker (app/src/engine/browser/worker.ts)
  pyodide/        the Pyodide runtime (from build-wasm/node_modules/pyodide) and the Pyodide
                  packages the engine needs, checked against pyodide-lock.json's SHA-256: the
                  site serves everything itself, the learner's browser contacts no CDN
  wheels/         the PyPI wheels of wheels.json (checked against their SHA-256) and the
                  Qiskit wheel from build.sh (build-wasm/dist)

Every wheel is shipped without its `tests/` folders (5.5 MB the browser would never run: SciPy,
PennyLane, networkx); the served pyodide-lock.json gets the new SHA-256 of the packages it lists.
  engine.zip      qlp_engine (Python sources) and content/

Needs build.sh to have run and `npm ci` in build-wasm. Downloads are cached in build-wasm/work.
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
# All needed: `import pennylane` imports requests (pennylane.data) and malt (autograph, which needs termcolor).
PYODIDE_PACKAGES = ["numpy", "scipy", "requests", "packaging", "typing-extensions", "termcolor"]
PYODIDE_RUNTIME = ["pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]
PYODIDE_CDN = "https://cdn.jsdelivr.net/pyodide/v{version}/full/"


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
    for wheel in (out / "wheels").glob("*.whl"):
        _strip_tests(wheel)

    _bundle(out / "engine.zip")
    pyodide = _pyodide(out / "pyodide")
    manifest = {
        "pyodide": pyodide,
        "indexURL": "pyodide/",
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


def _pyodide(target: Path) -> str:
    """Copies the runtime and downloads the packages (with their dependencies); returns the version."""
    npm = HERE / "node_modules" / "pyodide"
    if not npm.is_dir():
        sys.exit("Pyodide is not installed in build-wasm: run `npm ci` there first.")
    version = json.loads((npm / "package.json").read_text())["version"]
    pinned = json.loads((HERE / "package.json").read_text())["devDependencies"]["pyodide"]
    if version != pinned:
        sys.exit(f"build-wasm/node_modules has Pyodide {version}, package.json pins {pinned}: run `npm ci`.")
    target.mkdir(parents=True)
    for name in PYODIDE_RUNTIME:
        shutil.copy2(npm / name, target / name)

    def norm(name: str) -> str:
        return name.lower().replace("_", "-")

    lock = {norm(name): entry for name, entry in json.loads((npm / "pyodide-lock.json").read_text())["packages"].items()}
    needed, todo = set(), [norm(name) for name in PYODIDE_PACKAGES]
    while todo:
        name = todo.pop()
        if name not in needed:
            needed.add(name)
            todo += [norm(dep) for dep in lock[name]["depends"]]
    for name in sorted(needed):
        entry = lock[name]
        cache = HERE / "work" / f"pyodide-{version}" / entry["file_name"]
        if not cache.is_file() or _sha256(cache) != entry["sha256"]:
            cache.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(PYODIDE_CDN.format(version=version) + entry["file_name"]) as response:
                cache.write_bytes(response.read())
        if _sha256(cache) != entry["sha256"]:
            sys.exit(f"{entry['file_name']}: SHA-256 does not match pyodide-lock.json")
        shipped = target / entry["file_name"]
        shutil.copy2(cache, shipped)
        if _strip_tests(shipped):
            entry["sha256"] = _sha256(shipped)  # Pyodide checks the file against the lock
    served = json.loads((npm / "pyodide-lock.json").read_text())
    served["packages"] = {name: lock.get(norm(name), entry) for name, entry in served["packages"].items()}
    (target / "pyodide-lock.json").write_text(json.dumps(served, separators=(",", ":")))
    return version


def _strip_tests(wheel: Path) -> bool:
    """Rewrites the wheel without files under a `tests/` folder; True if it changed."""
    with zipfile.ZipFile(wheel) as source:
        entries = source.infolist()
        keep = [entry for entry in entries if "tests" not in entry.filename.split("/")[:-1]]
        if len(keep) == len(entries):
            return False
        data = [(entry, source.read(entry)) for entry in keep]
    with zipfile.ZipFile(wheel, "w", zipfile.ZIP_DEFLATED) as target:
        for entry, content in data:
            target.writestr(entry, content)
    return True


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
