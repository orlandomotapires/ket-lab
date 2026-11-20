# Context: Ket Lab in the browser (Pyodide + GitHub Pages)

Saved 19 Nov 2026. Work done on branch `browser-engine-qiskit-wasm` (from `main`), merged into `main`
by the owner (merge commit `328ca9d`). Plan and measurements: `.claude/docs/web-engine-decision.md`
(rewritten as the plan; the old "no-go" decision was removed on purpose). `.claude/docs/master-plan.md`
points to it (roadmap 1.1 "viable", 1.2a "done, not yet published", history entry 18 Nov).

## Goal

Publish Ket Lab as a static site on GitHub Pages: the real engine (Python, Qiskit 2.6.2,
PennyLane 0.45.1) runs in the learner's browser through Pyodide 314.0.7 in a Web Worker.
Local dev (`npm run dev`, native engine over WebSocket) and Docker (`deploy/`) are unchanged.
The repository is public (owner made it public on 19 Nov), so Pages is free.

Target URL: https://orlandomotapires.github.io/ket-lab/

## Status at save time

- Steps 1-6 of the plan done and pushed; last commit on the branch `7c2005d`.
- CI on `ff803b8` all green (first run with split Pyodide jobs). CI on `7c2005d` was queued.
- After the owner merged into `main`, the Pages workflow (run 44452961688) was building
  (compiling Qiskit, ~8-10 min: the branch's wheel cache is not shared with `main`).
- Pages settings: API `GET /repos/.../pages` returned 404 unauthenticated; owner must set
  Settings > Pages > Source: "GitHub Actions" or `configure-pages` fails; then re-run
  (Actions > Pages > Run workflow).
- Local checks all passed before the last push: native engine 964, Pyodide suite 837,
  all 85 reference solutions via BrowserEngine, browser-mode e2e in Chromium, Firefox and
  emulated Pixel 7 (WebKit/iPhone only in CI), unit 39, local e2e 57, hosted e2e 1.

## Next steps

1. Confirm the Pages deploy is green and the site loads.
2. Step 7, live site: `.wasm` served as `application/wasm`, second visit from cache,
   real first-visit download (~33 MB expected) on a slower connection.
3. Real iPhone (Safari gives WebAssembly less memory; restart threshold is 1 GB heap).
4. Confirm CI on `7c2005d` (adds time-lessons, Firefox/WebKit/phones) is green.
5. Later decisions: IBM hardware stays off in browser mode (CORS unknown); optional
   service worker for offline; Qiskit/Pyodide upgrades need patch port + rebuild.

## Architecture (what was built)

- `build-wasm/build.sh`: downloads qiskit 2.6.2 sdist, checks SHA-256 vs PyPI, applies
  `patches/qiskit-2.6.2-emscripten.patch` (5 files: no crossterm terminal size, faer without
  rayon, PrimitiveJob synchronous, parallel_map never parallel; ported from QisPlay's 2.5.2
  patch, MIT), builds with pyodide-build 0.39.4 (needs Python 3.14 via `PYTHON`, rustup).
  Output `build-wasm/dist/qiskit-2.6.2-cp310-abi3-pyemscripten_2026_0_wasm32.whl` (~6 MB).
  Not byte-reproducible (hash differs between builds); each build is tested instead.
- `build-wasm/stage.py` -> `app/public/browser-engine/` (gitignored): `manifest.json`,
  `pyodide/` (runtime from `build-wasm/node_modules/pyodide` + Pyodide packages checked
  against `pyodide-lock.json`), `wheels/` (PyPI wheels pinned in `wheels.json` with SHA-256,
  plus the Qiskit wheel), `engine.zip` (ket_lab_engine + content). Strips `tests/` folders from
  every wheel and rewrites hashes in the served lock. Learner's browser contacts no other host.
- Python: protocol moved from `server.py` to `ket_lab_engine/dispatch.py` (`Dispatcher`);
  `EngineServer(Dispatcher)` keeps `_handle_message`/`_dispatch` (tests use them).
  `ket_lab_engine/browser.py`: `BrowserEngine` (public mode, progress in browser, hardware off),
  `InlinePool` (runs jobs inline, tells host `job_started(seconds, timeout_reply)` etc.),
  `BROWSER_TIME_SCALE = 3.0` (Pyodide is 2-2.6x slower than native), maps NumPy's
  "array is too big" to the engine's memory message, PennyLane imported lazily
  (`warm_up_pennylane`, before the job clock if the job mentions pennylane).
- App: `app/src/engine/browser/worker.ts` (loads Pyodide from the site, reports loading
  stages, heap size per reply, imports PennyLane after 1.5 s idle);
  `app/src/engine/browser/socket.ts` (`BrowserEngineSocket`, WebSocket-like: one request at a
  time, stale runs dropped, timeout/Stop/crash -> terminate and restart worker, restart when
  heap > 1 GB); `EngineClient` picks it when built with `VITE_ENGINE=browser` (lazy import);
  `EngineLoadingBanner.tsx` ("Step k of 5"); `vite.config.ts` `base` from `VITE_BASE`,
  `worker.format: "es"`.
- Tests: `build-wasm/run-engine-tests.mjs` (pytest in Pyodide with the staged files; skips 7
  server-only files), `build-wasm/test-browser-engine.mjs` (protocol + all 85 reference
  solutions with only shipped packages), `build-wasm/time-lessons.mjs` (170 jobs vs limits,
  fails above 50%; worst is 2.9 challenge at 17%), `app/e2e/browser-engine.spec.ts` with
  `app/playwright.browser.config.ts` (projects chromium, firefox, webkit, mobile-chrome,
  mobile-safari; `npm run e2e:browser`).
- CI (`.github/workflows/ci.yml`): `wasm-build` (wheel cached by hash of build.sh, patch,
  package.json; uploads staged files), `wasm-suite`, `wasm-browser` (protocol, time-lessons,
  all browsers). `pages.yml`: on push to `main`, same build + reference-solution check +
  `VITE_ENGINE=browser VITE_BASE=<base_path>/` + deploy.

## Measurements

- First download ~33 MB on the wire (40 MB on disk); SciPy 13 MB is the largest.
- Ready in 5.9 s in a fresh Chromium under the Pages sub-path (local preview).
- Trimming tried and rejected: `import pennylane` needs `requests` and `malt`
  (diastatic-malt, gast, termcolor). matplotlib avoided by taking networkx from PyPI.
- Live run of challenge solutions 3.1, 4.1, 5.3 draws nothing (same natively; Check passes).

## Commands

```bash
build-wasm/build.sh                  # PYTHON=<python3.14>; scratch conda env was used locally
cd build-wasm && npm ci && cd ..
python3 build-wasm/stage.py
cd build-wasm && node run-engine-tests.mjs && node test-browser-engine.mjs && node time-lessons.mjs
cd app && npm run e2e:browser -- --project chromium   # or firefox, mobile-chrome
cd app && VITE_ENGINE=browser npm run dev
```

## Gotchas met

- Don't run `npm run setup` with sudo: root PATH has Node 18 (nvm Node 22 is per user).
- Never restage (`stage.py` deletes the output folder) while tests read it.
- `pkill -f <pattern>` can match the running shell's own command line: kill by PID.
- Pyodide in Node: `unpackArchive` needs `Uint8Array`, not `Buffer`; Node `--permission`
  breaks Pyodide; errors print a minified source line, so catch and print `.message`.
- Playwright: the base config sets `channel: "chrome"`; Firefox/WebKit projects need it
  removed from shared `use`. Firefox/WebKit cannot grant clipboard permissions:
  `replaceCode` uses `keyboard.insertText` there. Phones show one lab panel at a time.
- WebKit locally needs `sudo apt-get install libavif16` (not installed); runs in CI.
- `gh` CLI is not installed; the repo is public, so the REST API works unauthenticated.
- The lab's guard rejects `import time` in learner code.
- CI WebKit (and once Firefox) sometimes hung at "Step 2 of 5" (Pyodide `loadPackage` never
  settled, no error) until the 3-minute expect timeout. `socket.ts` now replaces a worker whose
  start stays on one step for 60 s (doubled per stuck start); the page console then shows
  "start stuck at step N". Root cause not reproduced (no WebKit locally).
