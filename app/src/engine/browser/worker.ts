/// <reference lib="webworker" />
/**
 * The engine inside the browser: Pyodide (Python compiled to WebAssembly) running
 * ket_lab_engine.browser.BrowserEngine, in a Web Worker so long jobs never freeze the page.
 *
 * Files come from the site (staged by build-wasm/stage.py into public/browser-engine/):
 * manifest.json, the wheels (Qiskit built by build-wasm/build.sh, PennyLane, ...) and
 * engine.zip (ket_lab_engine and content/), and Pyodide itself with its packages (NumPy, SciPy, ...)
 * under pyodide/. Nothing is fetched from another site.
 *
 * Messages with the page (socket.ts):
 *   in:  {kind: "init", base} once, then {kind: "request", raw} one at a time
 *   out: {kind: "loading", step, total, stage} while starting | {kind: "ready", texts}
 *        | {kind: "reply", raw, heapMB} | {kind: "event", raw}
 *        | {kind: "job", seconds, reply} | {kind: "phase", reply} | {kind: "finished"}
 *        | {kind: "fatal", message} (could not start) | {kind: "crashed", message}
 */

interface Manifest {
  pyodide: string;
  /** Folder of the Pyodide runtime and packages, relative to the manifest. */
  indexURL: string;
  packages: string[];
  wheels: string[];
  bundle: string;
}

interface PyodideApi {
  loadPackage(names: string | string[], options?: { messageCallback?: (message: string) => void }): Promise<unknown>;
  unpackArchive(buffer: ArrayBuffer, format: string, options?: { extractDir?: string }): void;
  runPython(code: string): unknown;
  runPythonAsync(code: string): Promise<unknown>;
  globals: { set(name: string, value: unknown): void };
  /** Emscripten module; its heap only grows (WebAssembly memory cannot shrink). */
  _module?: { HEAPU8?: { length: number } };
}

interface Engine {
  handle(raw: string): Promise<string>;
}

const scope = self as unknown as DedicatedWorkerGlobalScope;

let engine: Engine | null = null;
let pyodide: PyodideApi | null = null;
let idleTimer: ReturnType<typeof setTimeout> | undefined;

/** PennyLane takes seconds to import and only Track 3 uses it: import it once the page is quiet. */
const IDLE_BEFORE_PENNYLANE_MS = 1500;
function warmPennyLaneWhenIdle(): void {
  clearTimeout(idleTimer);
  idleTimer = setTimeout(() => pyodide?.runPython("BrowserEngine.warm_up_pennylane()"), IDLE_BEFORE_PENNYLANE_MS);
}

const post = (message: Record<string, unknown>) => scope.postMessage(message);
const quiet = { messageCallback: () => undefined };

/** Loading steps, in order; the page shows them as "step k of n" with its own wording. */
const STAGES = ["runtime", "packages", "libraries", "lessons", "starting"] as const;
const stage = (name: (typeof STAGES)[number]) =>
  post({ kind: "loading", step: STAGES.indexOf(name) + 1, total: STAGES.length, stage: name });

async function start(base: string): Promise<void> {
  stage("runtime");
  const response = await fetch(new URL("manifest.json", base), { cache: "no-cache" });
  if (!response.ok) throw new Error(`manifest.json: HTTP ${response.status}`);
  const manifest = (await response.json()) as Manifest;

  const indexURL = new URL(manifest.indexURL, base).href;
  const { loadPyodide } = (await import(/* @vite-ignore */ `${indexURL}pyodide.mjs`)) as {
    loadPyodide: (options: { indexURL: string }) => Promise<PyodideApi>;
  };
  const py = await loadPyodide({ indexURL });
  pyodide = py;
  stage("packages");
  await py.loadPackage(manifest.packages, quiet);
  stage("libraries");
  await py.loadPackage(manifest.wheels.map((wheel) => new URL(wheel, base).href), quiet);
  stage("lessons");
  const bundle = await fetch(new URL(manifest.bundle, base));
  if (!bundle.ok) throw new Error(`${manifest.bundle}: HTTP ${bundle.status}`);
  py.unpackArchive(await bundle.arrayBuffer(), "zip", { extractDir: "/engine" });

  py.globals.set("host", {
    job_started: (seconds: number, reply: string) => post({ kind: "job", seconds, reply }),
    job_phase: (reply: string) => post({ kind: "phase", reply }),
    job_finished: () => post({ kind: "finished" }),
    send_event: (raw: string) => post({ kind: "event", raw }),
  });
  stage("starting");
  engine = (await py.runPythonAsync(`
import sys
sys.path.insert(0, "/engine")
from ket_lab_engine.browser import BrowserEngine
BrowserEngine.warm_up()
BrowserEngine("/engine/content", host)
`)) as Engine;
  post({ kind: "ready", texts: JSON.parse(String(py.runPython("BrowserEngine.texts()"))) });
  warmPennyLaneWhenIdle();
}

scope.onmessage = async (event: MessageEvent<{ kind: string; base?: string; raw?: string }>) => {
  const message = event.data;
  if (message.kind === "init") {
    try {
      await start(message.base!);
    } catch (error) {
      post({ kind: "fatal", message: String(error instanceof Error ? error.message : error) });
    }
    return;
  }
  if (message.kind === "request" && engine) {
    clearTimeout(idleTimer);
    try {
      const raw = await engine.handle(message.raw!);
      post({ kind: "reply", raw, heapMB: (pyodide?._module?.HEAPU8?.length ?? 0) / 2 ** 20 });
      warmPennyLaneWhenIdle();
    } catch (error) {
      // Python itself broke (out of memory, a WebAssembly trap): the page starts a new worker.
      post({ kind: "crashed", message: String(error instanceof Error ? error.message : error) });
    }
  }
};
