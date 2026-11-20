// Times every lesson's reference solution in the browser engine against the time limit the
// engine gives the job (the page terminates the worker when a job passes it).
// Usage (from build-wasm/, after stage.py): node time-lessons.mjs [--max-ratio 0.5]
// Exits with 1 if a Check does not pass or a job uses more than --max-ratio of its limit
// (default 0.5: room for learners' machines slower than this one). A live run that fails is
// only listed: some challenge solutions define what the checker calls and draw nothing by
// themselves (the same on the native engine).
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { loadPyodide } from "pyodide";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const staged = join(root, "app", "public", "browser-engine");
const manifest = JSON.parse(readFileSync(join(staged, "manifest.json"), "utf8"));
const flag = process.argv.indexOf("--max-ratio");
const maxRatio = flag > 0 ? Number(process.argv[flag + 1]) : 0.5;

const py = await loadPyodide();
await py.loadPackage(manifest.packages, { messageCallback: () => {} });
await py.loadPackage(manifest.wheels.map((wheel) => join(staged, wheel)), { messageCallback: () => {} });
py.unpackArchive(new Uint8Array(readFileSync(join(staged, manifest.bundle))), "zip", { extractDir: "/engine" });

// The job's own clock: from job_started (after any PennyLane import) to job_finished.
let job = null;
const host = {
  job_started: (seconds) => { job = { limit: seconds, start: performance.now() }; },
  job_phase: () => {},
  job_finished: () => { job.elapsed = (performance.now() - job.start) / 1000; },
  send_event: () => {},
};
py.globals.set("host", host);
const engine = await py.runPythonAsync(`
import sys
sys.path.insert(0, "/engine")
from ket_lab_engine.browser import BrowserEngine
BrowserEngine.warm_up()
BrowserEngine.warm_up_pennylane()
BrowserEngine("/engine/content", host)
`);

let nextId = 1;
const rows = [];
for (const track of readdirSync(join(root, "content")).filter((name) => name.startsWith("track_")).sort()) {
  for (const section of readdirSync(join(root, "content", track)).sort()) {
    const folder = join(root, "content", track, section);
    if (!existsSync(join(folder, "manifest.json"))) continue;
    const { id } = JSON.parse(readFileSync(join(folder, "manifest.json"), "utf8"));
    for (const [file, challenge] of [["solution.py", false], ["challenge_solution.py", true]]) {
      if (!existsSync(join(folder, file))) continue;
      const code = readFileSync(join(folder, file), "utf8");
      for (const type of ["run", "validate"]) {
        job = null;
        const reply = JSON.parse(await engine.handle(JSON.stringify({ id: nextId++, type, lesson_id: id, code, challenge })));
        if (!job) continue; // answered without running a job
        const ok = type === "run" ? reply.ok : reply.passed;
        rows.push({ lesson: `${id}${challenge ? " ch" : ""}`, type, ...job, ratio: job.elapsed / job.limit, ok, detail: JSON.stringify(reply.error ?? reply.message ?? reply).slice(0, 200) });
      }
    }
  }
}

rows.sort((a, b) => b.ratio - a.ratio);
console.log("lesson     job       time   limit  share");
for (const row of rows.slice(0, 15)) {
  console.log(`${row.lesson.padEnd(10)} ${row.type.padEnd(8)} ${row.elapsed.toFixed(2).padStart(6)} s ${String(row.limit).padStart(5)} s  ${(row.ratio * 100).toFixed(0).padStart(3)}%${row.ok ? "" : "  NOT OK"}`);
}
for (const row of rows.filter((r) => !r.ok)) console.log(`not ok: ${row.lesson} ${row.type}: ${row.detail}`);
const over = rows.filter((row) => row.ratio > maxRatio);
const failed = rows.filter((row) => !row.ok && row.type === "validate");
console.log(`${rows.length} jobs; ${over.length} above ${(maxRatio * 100).toFixed(0)}% of their limit; ${failed.length} Checks failed`);
process.exit(over.length || failed.length ? 1 : 0);
