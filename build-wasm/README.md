# build-wasm

Builds what the browser version of the engine needs and checks the engine against it. Plan and measurements: [docs/web-engine-decision.md](../docs/web-engine-decision.md).

Neither Qiskit nor PyPI publishes a WebAssembly build of Qiskit, so `build.sh` compiles the official source (checked against PyPI's SHA-256) with a small patch, `patches/qiskit-<version>-emscripten.patch`. The patch only removes what a browser cannot do: query the terminal size, run the `faer` thread pool, start threads for primitives, or start processes in `parallel_map`.

```bash
# needs Python 3.14 (set PYTHON if it is not python3.14), rustup and Node 22
build-wasm/build.sh                 # ~5 min; writes build-wasm/dist/qiskit-*.whl
cd build-wasm && npm ci
node run-engine-tests.mjs           # the engine suite inside Pyodide (~6 min)
```

CI runs both on every push (the "Engine in Pyodide" job) and keeps the wheel as an artifact for 30 days.

## Upgrading

- **Qiskit:** change `QISKIT_VERSION` and `QISKIT_SDIST_SHA256` in `build.sh`, port the patch to the new source (the hunks are short; `patch` reports the ones that moved), rename it, and run both commands.
- **Pyodide:** the wheel is built for one Pyodide release. Change `PYODIDE_VERSION` in `build.sh` and the `pyodide` version in `package.json` together, then rebuild.
