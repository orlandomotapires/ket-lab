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
| Startup in Chromium (steps 4–5) | Ready in 5.9 s in a fresh browser, served locally under the Pages sub-path: Python 1.5–2.5 s, NumPy and SciPy 1.5 s, wheels and lessons under 1 s, importing Qiskit 2 s. PennyLane (5 s to import, Track 3 only) is imported in the background once the page is idle, or just before the first job that needs it, outside that job's time limit |
| First download (step 5) | About 33 MB on the wire (40 MB on disk), all from the site: Pyodide runtime and its packages, the wheels, the lessons. Wheels ship without their `tests/` folders (5.5 MB). Cached by the browser afterwards |

## Steps

1. **Build Qiskit 2.6.2 for WebAssembly (done: [`build-wasm/`](../build-wasm/README.md)).** Neither Qiskit nor PyPI publishes a WebAssembly build, so we compile the official 2.6.2 source ourselves, following the recipe of the community project [QisPlay](https://github.com/kriss-u/QisPlay) (written for 2.5.2, ported to 2.6.2). Build tools: Python 3.14, `pyodide-build`, Rust and Emscripten. The patch is small (5 files) and only removes what a browser cannot do:
   - no terminal-size query in the text circuit drawer (assumes 80 columns);
   - the `faer` linear algebra library built without its thread pool;
   - primitives (`Sampler`, `Estimator`) run on the calling thread, and `parallel_map` never starts processes.

   The wheel is not committed: `build-wasm/build.sh` rebuilds it from the official source (checked against PyPI's hash), and CI keeps each build as an artifact. The wheel is tied to one Pyodide version: upgrading Pyodide means rebuilding it.
2. **Run the engine suite in Pyodide in CI (done).** The "Engine in Pyodide" CI job rebuilds the wheel and runs `build-wasm/run-engine-tests.mjs` on every push, so a Qiskit, PennyLane or Pyodide upgrade cannot silently break the browser version.
3. **Browser engine (done).** Build the app with `VITE_ENGINE=browser`.
   - Python: the protocol moved from `server.py` to `qlp_engine/dispatch.py`, shared by the server and by `qlp_engine/browser.py` (`BrowserEngine`, public mode: progress and notes in the browser, no IBM hardware). Jobs run in the worker itself, one at a time.
   - Web Worker (`app/src/engine/browser/worker.ts`): loads Pyodide, its packages, the wheels and `engine.zip` (qlp_engine and content) from the site, staged by `build-wasm/stage.py` into `public/browser-engine/`. The learner's browser contacts no other site.
   - Page (`app/src/engine/browser/socket.ts`): looks like a WebSocket to `EngineClient`. One request at a time; an edit replaces a waiting run; a timeout or Stop terminates the worker, answers with the engine's own message and starts a new worker.
   - Checked by `build-wasm/test-browser-engine.mjs` (Node) and `npm run e2e:browser` (Chromium: lesson 1.1 runs and is checked; an infinite loop times out and the next run works). Both run in CI.
4. **Limits in the browser (done).**
   - Loading: a banner shows the step ("Step 3 of 5: Qiskit and PennyLane") with a progress bar, also when the worker restarts.
   - Memory: an array over 2 GB (the WebAssembly limit) gets the same "too much memory" message as on the server; after a job that leaves the worker's memory above 1 GB, the page starts a fresh worker, because WebAssembly memory cannot shrink.
   - Startup: PennyLane is no longer imported at start (see "Startup" above).
   - Checked by `npm run e2e:browser` (loading banner, timeout, memory) and `build-wasm/test-browser-engine.mjs` (memory message, Track 3 without PennyLane preloaded).
5. **Smaller download, one origin (done).**
   - Pyodide and its packages are served by the site (copied from the npm package and checked against `pyodide-lock.json`), not by jsdelivr.
   - Wheels ship without `tests/` folders (SciPy 2.2 MB, PennyLane 2.4 MB, networkx 0.9 MB); the served lock file carries the new hashes.
   - matplotlib is out (networkx comes from its PyPI wheel). Every other package is needed: `import pennylane` imports `requests` and `malt` (with `gast` and `termcolor`), checked by removing them.
   - The Pyodide test run now installs exactly the staged files, and the Node test validates all 85 reference solutions with only what the site ships.
6. **Publish (workflow ready, needs a one-time setting).** `.github/workflows/pages.yml` builds the wheel, stages the files, validates every reference solution in the browser engine, builds the interface with `VITE_ENGINE=browser` and the Pages base path (`VITE_BASE`), and deploys on every push to `main`. One-time setup: Settings > Pages > Source: "GitHub Actions". GitHub Pages is free for public repositories; a private repository needs a paid plan.

## Risks and open questions

- **The Qiskit wheel is ours to maintain.** Each Qiskit or Pyodide upgrade needs a rebuild, and the patch may need adjusting (porting it from 2.5.2 to 2.6.2 needed small edits). If Qiskit starts publishing WebAssembly wheels, switch to those.
- **rustworkx's WebAssembly wheel is experimental.** Upstream calls its support best effort.
- **Speed (measured, 19 Nov 2026).** A job takes 2 to 2.6 times as long in Pyodide as natively, so the browser engine multiplies every time limit by 3 (`BROWSER_TIME_SCALE` in `qlp_engine/browser.py`). With that, the slowest of the 170 jobs (every reference solution, run and Check) uses 17% of its limit (2.9 challenge: 2.5 s of 15 s); a learner's machine about 6 times slower than the development one still fits. The cost: an infinite loop is stopped after 15 s instead of 5. `build-wasm/time-lessons.mjs` checks this in CI and fails above 50%.
- **Hardware track.** Off in the browser version. Running on real IBM hardware (`qiskit-ibm-runtime`) would need calls to IBM's API from the page, which may be refused by cross-origin rules; not tried.
- **Browsers.** The browser-mode tests pass in Chromium and Firefox and on an emulated Pixel 7; CI also runs them in WebKit (Safari's engine) and on an emulated iPhone 14. Emulation covers screen size and touch, not a phone's CPU or memory: a real iPhone, where Safari gives WebAssembly less memory, still needs a check after the first deploy.
- **Live run of three challenge solutions.** 3.1, 4.1 and 5.3: the challenge code defines what the checker calls, so a plain run draws nothing ("variable not defined yet" or "no circuit"). Check passes. Same on the native engine; not specific to the browser.

The hosted engine in `deploy/` remains available as an alternative, but it is no longer the plan for the web version.
