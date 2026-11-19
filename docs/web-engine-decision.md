# Plan: Ket Lab entirely in the browser

**Goal:** publish Ket Lab as a static site (GitHub Pages) with no server. The engine (Python, Qiskit, PennyLane) runs inside the learner's browser through [Pyodide](https://pyodide.org), the Python runtime compiled to WebAssembly.

**Status (18 Nov 2026):** feasible. The libraries the lessons teach now run in Pyodide, including Qiskit 2.6.2 built by us, and the engine's test suite passes there.

Only the GitHub Pages build uses Pyodide. Local development (`npm run dev`) keeps the native engine over a WebSocket, and the Docker setup in `deploy/` keeps working as an optional server; the app picks the mode at build time. What remains is engineering, listed under "Steps" below.

## How it will work

```text
GitHub Pages (static files)
├── the interface (app/, built by Vite)
├── Pyodide runtime + wheels (Qiskit, PennyLane, rustworkx, ...)
└── qlp_engine and content/

Learner's browser
├── page: the interface, same as today
└── Web Worker: Pyodide + qlp_engine
    └── receives the same jobs the WebSocket carries today (run, shots, validate, export)
```

- The interface talks to a Web Worker instead of a WebSocket. The job and result messages stay the same; only the transport changes.
- Learner code runs in the learner's own browser tab, so there is no server to protect. The server, the worker pool and the container hardening in `deploy/` are not needed for this version.
- Progress stays in the browser (localStorage), as the hosted mode already does, with export and import on the hub.
- A runaway job is stopped by terminating the Web Worker and starting a new one.

## What was measured

Pyodide 314.0.7 (Python 3.14) in Node, on the development machine, 18 Nov 2026.

| Piece | Result |
|---|---|
| NumPy 2.4.6, SciPy 1.18.0, networkx | From Pyodide's own package set |
| rustworkx 0.18.1 | Official WebAssembly wheel on PyPI (experimental, "best effort" support) |
| PennyLane 0.45.1 | Works, installed without `pennylane-lightning` (compiled, no WebAssembly build; the lessons use `default.qubit` and `default.mixed`) |
| `qml.qchem` H2 + VQE (lesson 3.2) | E = −1.136189 Ha, the exact value |
| Qiskit 2.6.2, built by us from the official source (step 1) | Builds in about 4.5 min, 6.0 MB wheel (not byte-for-byte reproducible: two builds of the same source gave different hashes, so each build is tested rather than checked against a hash). Statevector, transpile, OpenQASM 3, Sampler and Estimator all work |
| Engine test suite with that wheel | **837 of 837 collected tests pass** (346 s; natively 964 tests in 141 s). The 7 files not collected test the WebSocket server, the worker pool and the SQLite progress store, which the browser version replaces |
| All lesson reference solutions (`test_content.py`) | 365 of 365 pass |
| Startup | About 8 s to load everything, after the first download |
| First download | About 50 MB (Pyodide with SciPy 41 MB, PennyLane 5 MB, Qiskit 6 MB, rustworkx 1.3 MB), cached by the browser afterwards |

## Steps

1. **Build Qiskit 2.6.2 for WebAssembly (done: [`build-wasm/`](../build-wasm/README.md)).** Neither Qiskit nor PyPI publishes a WebAssembly build, so we compile the official 2.6.2 source ourselves, following the recipe of the community project [QisPlay](https://github.com/kriss-u/QisPlay) (written for 2.5.2, ported to 2.6.2). Build tools: Python 3.14, `pyodide-build`, Rust and Emscripten. The patch is small (5 files) and only removes what a browser cannot do:
   - no terminal-size query in the text circuit drawer (assumes 80 columns);
   - the `faer` linear algebra library built without its thread pool;
   - primitives (`Sampler`, `Estimator`) run on the calling thread, and `parallel_map` never starts processes.

   The wheel is not committed: `build-wasm/build.sh` rebuilds it from the official source (checked against PyPI's hash), and CI keeps each build as an artifact. The wheel is tied to one Pyodide version: upgrading Pyodide means rebuilding it.
2. **Run the engine suite in Pyodide in CI (done).** The "Engine in Pyodide" CI job rebuilds the wheel and runs `build-wasm/run-engine-tests.mjs` on every push, so a Qiskit, PennyLane or Pyodide upgrade cannot silently break the browser version.
3. **Browser engine.** A Web Worker that loads Pyodide, installs the wheels from the site itself (no request to PyPI at runtime) and calls `qlp_engine.worker.handle(job)`. On the app side, a second transport in `app/src/engine/client.ts`, chosen at build time next to the existing local and hosted modes.
4. **Limits in the browser.** A per-job timeout (terminate and restart the worker), a clear loading screen for the first download, and a message when a circuit is too large for the tab's memory.
5. **Smaller download.** Drop matplotlib (pulled in by networkx, about 8 MB) and anything else the lessons do not import.
6. **Publish.** A GitHub Actions workflow that builds the static site and deploys it to GitHub Pages. GitHub Pages is free for public repositories; a private repository needs a paid plan.

## Risks and open questions

- **The Qiskit wheel is ours to maintain.** Each Qiskit or Pyodide upgrade needs a rebuild, and the patch may need adjusting (porting it from 2.5.2 to 2.6.2 needed small edits). If Qiskit starts publishing WebAssembly wheels, switch to those.
- **rustworkx's WebAssembly wheel is experimental.** Upstream calls its support best effort.
- **Speed.** The suite ran about 3 times slower than native. Fine for the lessons tested; the heaviest ones (Track 3 training loops) need checking in a real browser, not only in Node.
- **Hardware track.** Running on real IBM hardware (`qiskit-ibm-runtime`) needs network calls from inside Pyodide; not tested yet.
- **Real browsers.** Everything above ran in Node. Chrome, Firefox and Safari, and a phone, still need checking.

The hosted engine in `deploy/` remains available as an alternative, but it is no longer the plan for the web version.
