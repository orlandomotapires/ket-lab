// Drives qlp_engine.browser.BrowserEngine in Pyodide the way the Web Worker does
// (app/src/engine/browser/worker.ts): the staged manifest, Pyodide packages, wheels and bundle.
// Usage (from build-wasm/, after build.sh and stage.py): node test-browser-engine.mjs
import assert from "node:assert/strict";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { loadPyodide } from "pyodide";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const staged = join(root, "app", "public", "browser-engine");
const manifest = JSON.parse(readFileSync(join(staged, "manifest.json"), "utf8"));

const start = performance.now();
const py = await loadPyodide();
await py.loadPackage(manifest.packages, { messageCallback: () => {} });
await py.loadPackage(manifest.wheels.map((wheel) => join(staged, wheel)), { messageCallback: () => {} });
py.unpackArchive(new Uint8Array(readFileSync(join(staged, manifest.bundle))), "zip", { extractDir: "/engine" });

const calls = [];
const host = {
  job_started: (seconds, reply) => calls.push(["started", seconds, JSON.parse(reply)]),
  job_phase: (reply) => calls.push(["phase", JSON.parse(reply)]),
  job_finished: () => calls.push(["finished"]),
  send_event: (event) => calls.push(["event", JSON.parse(event)]),
};
py.globals.set("host", host);
const engine = await py.runPythonAsync(`
import sys
sys.path.insert(0, "/engine")
from qlp_engine.browser import BrowserEngine
BrowserEngine.warm_up()
BrowserEngine("/engine/content", host)
`);
console.log(`ready in ${((performance.now() - start) / 1000).toFixed(1)} s`);

let nextId = 1;
async function ask(message) {
  calls.length = 0;
  const begin = performance.now();
  const reply = JSON.parse(await engine.handle(JSON.stringify({ id: nextId++, ...message })));
  console.log(`  ${message.type.padEnd(18)} ${((performance.now() - begin) / 1000).toFixed(2)} s`);
  return reply;
}
const solution = (folder) => readFileSync(join(root, "content", folder, "solution.py"), "utf8");
const starter = (folder) => readFileSync(join(root, "content", folder, "starter_code.py"), "utf8");
const lesson11 = "track_1_fundamentals/section_1_1_qubit";

let reply = await ask({ type: "catalog" });
assert.equal(reply.ok, true);
assert.equal(reply.progress_storage, "client");

reply = await ask({ type: "lesson", lesson_id: "1.1" });
assert.equal(reply.ok, true);
assert.equal(reply.lesson.id, "1.1");

reply = await ask({ type: "run", lesson_id: "1.1", code: solution(lesson11) });
assert.equal(reply.ok, true, JSON.stringify(reply.error));
assert.ok(reply.snapshots.length > 0);
assert.equal(calls[0][0], "started");
assert.equal(calls[0][2].error.kind, "timeout");
assert.equal(calls.at(-1)[0], "finished");

reply = await ask({ type: "validate", lesson_id: "1.1", code: solution(lesson11) });
assert.equal(reply.passed, true, JSON.stringify(reply));
reply = await ask({ type: "validate", lesson_id: "1.1", code: starter(lesson11) });
assert.equal(reply.passed, false);

const bell = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n";
reply = await ask({ type: "shots", code: bell, shots: 1000, seed: 3 });
assert.equal(reply.ok, true, JSON.stringify(reply.error));
assert.ok(calls.some(([kind, value]) => kind === "phase" && value.error.kind === "timeout"), "shots announce the sampling phase");

// Each step takes longer than the reporter's 0.1 s batching interval, so events go out while it runs.
const training = [
  "import numpy as np",
  "from qiskit import QuantumCircuit",
  "qc = QuantumCircuit(1)",
  "m = np.eye(300)",
  "for step in range(6):",
  "    for _ in range(40):",
  "        m = (m @ np.ones((300, 300))) / 300",
  "    report(cost=1 / (step + 1))",
  "",
].join("\n");
reply = await ask({ type: "run", code: training, train: true });
assert.equal(reply.ok, true, JSON.stringify(reply.error));
const events = calls.filter(([kind]) => kind === "event").map(([, event]) => event);
assert.ok(events.length >= 2, `progress events while training (${events.length})`);
assert.equal(events[0].event, "progress");
assert.equal(events[0].id, nextId - 1);

// Over 2 GB: NumPy refuses under WebAssembly; the learner gets the engine's memory message.
reply = await ask({ type: "run", code: "import numpy as np\nfrom qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\na = np.zeros((40000, 40000))\n" });
assert.equal(reply.ok, false);
assert.equal(reply.error.kind, "memory", JSON.stringify(reply.error));
assert.equal(reply.error.line, 4);

// Track 3: PennyLane is not imported at startup; the first job imports it before its clock starts.
assert.equal(py.runPython("import sys; 'pennylane' in sys.modules"), false);
const lesson31 = "track_3_variational/section_3_1_variational";
reply = await ask({ type: "validate", lesson_id: "3.1", code: solution(lesson31) });
assert.equal(reply.passed, true, JSON.stringify(reply));
const started = calls.find(([kind]) => kind === "started");
assert.ok(started, "the job announced its time limit");
assert.ok(py.runPython("import sys; 'pennylane' in sys.modules"));

reply = await ask({ type: "hardware.available" });
assert.equal(reply.available, false);

reply = await ask({ type: "run", code: "while True:\n    pass\n", lesson_id: "1.1", dry: true, ...{ code: 42 } });
assert.equal(reply.ok, false);
assert.equal(reply.error.kind, "protocol");

const texts = JSON.parse(py.runPython("BrowserEngine.texts()", { globals: py.globals }));
assert.equal(texts.cancelled.error.kind, "cancelled");
assert.equal(texts.crash.error.kind, "crash");

// Every lesson's reference solution (and challenge solution) passes, through the browser protocol
// and with only the packages the site ships (unlike the pytest run, which adds pytest's own).
let solutions = 0;
for (const track of readdirSync(join(root, "content")).filter((name) => name.startsWith("track_"))) {
  for (const section of readdirSync(join(root, "content", track))) {
    const folder = join(root, "content", track, section);
    if (!existsSync(join(folder, "manifest.json"))) continue;
    const { id } = JSON.parse(readFileSync(join(folder, "manifest.json"), "utf8"));
    for (const [file, challenge] of [["solution.py", false], ["challenge_solution.py", true]]) {
      if (!existsSync(join(folder, file))) continue;
      const code = readFileSync(join(folder, file), "utf8");
      const result = JSON.parse(await engine.handle(JSON.stringify({ id: nextId++, type: "validate", lesson_id: id, code, challenge })));
      assert.equal(result.passed, true, `${id}${challenge ? " challenge" : ""}: ${JSON.stringify(result.error ?? result.message)}`);
      solutions++;
    }
  }
}
console.log(`  ${solutions} reference solutions pass`);

console.log("browser engine: all checks passed");
