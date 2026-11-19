// Runs the engine's test suite inside Pyodide (the WebAssembly Python the browser version uses).
// Usage (from build-wasm/): node run-engine-tests.mjs [pytest args...]
// Needs the Qiskit wheel from build.sh in dist/. Packages other than Qiskit come from
// Pyodide's distribution and PyPI.
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { loadPyodide } from "pyodide";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..");
const wheel = readdirSync(join(here, "dist")).find((f) => /^qiskit-.*wasm32\.whl$/.test(f));
if (!wheel) throw new Error("No Qiskit wheel in build-wasm/dist: run build.sh first.");

const start = performance.now();
const py = await loadPyodide();
await py.loadPackage(["numpy", "scipy", "networkx", "micropip", "pytest", "jsonschema"], { messageCallback: () => {} });
py.FS.writeFile(`/tmp/${wheel}`, readFileSync(join(here, "dist", wheel)));
// pennylane-lightning (PennyLane's compiled simulator) has no WebAssembly build: install
// PennyLane without it, and its other dependencies at the versions of engine/constraints.txt.
await py.runPythonAsync(`
import micropip
await micropip.install(["rustworkx==0.18.1", "emfs:/tmp/${wheel}"])
await micropip.install("pennylane==0.45.1", deps=False)
await micropip.install(["autograd==1.8.0", "appdirs==1.4.4", "autoray==0.8.4", "cachetools==8.0.0",
                        "tomlkit==0.15.2", "diastatic-malt==2.15.3", "gast==0.7.0",
                        "typing_extensions", "packaging", "requests"])
`);
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
