// Runs the engine's test suite inside Pyodide (the WebAssembly Python the browser version uses),
// with exactly the packages the site ships: the staged manifest of stage.py.
// Usage (from build-wasm/, after build.sh and stage.py): node run-engine-tests.mjs [pytest args...]
import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { loadPyodide } from "pyodide";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..");
const staged = join(repo, "app", "public", "browser-engine");
const manifest = JSON.parse(readFileSync(join(staged, "manifest.json"), "utf8"));

const start = performance.now();
const py = await loadPyodide();
// pytest and jsonschema only for the tests; everything else as in the browser.
await py.loadPackage([...manifest.packages, "pytest", "jsonschema"], { messageCallback: () => {} });
await py.loadPackage(manifest.wheels.map((wheel) => join(staged, wheel)), { messageCallback: () => {} });
py.FS.mkdir("/repo");
py.FS.mount(py.FS.filesystems.NODEFS, { root: repo }, "/repo");
console.log(`Pyodide ready in ${((performance.now() - start) / 1000).toFixed(1)} s`);

py.globals.set("ARGS", py.toPy(process.argv.slice(2)));
const code = await py.runPythonAsync(`
import os, sys
sys.dont_write_bytecode = True
os.chdir("/repo/engine")
sys.path.insert(0, "/repo/engine")
import pytest
# These files test the WebSocket server, the worker pool and the SQLite progress store,
# which the browser version replaces (and websockets does not run in Pyodide).
SERVER_ONLY = ["test_backup_and_notes", "test_database_lock", "test_engine_runs", "test_hardware",
               "test_robustness", "test_server", "test_stable_keys"]
ignore = [f"--ignore=tests/{name}.py" for name in SERVER_ONLY]
int(pytest.main(["-p", "no:cacheprovider", "-q", "-rf", *ignore, *ARGS]))
`);
process.exit(code);
