/// <reference lib="webworker" />
/**
 * The engine inside the browser: Pyodide (Python compiled to WebAssembly) running
 * qlp_engine.browser.BrowserEngine, in a Web Worker so long jobs never freeze the page.
 *
 * Files come from the site (staged by build-wasm/stage.py into public/browser-engine/):
 * manifest.json, the wheels (Qiskit built by build-wasm/build.sh, PennyLane, ...) and
 * engine.zip (qlp_engine and content/). Pyodide itself and its packages (NumPy, SciPy, ...)
 * come from Pyodide's CDN, at the version the manifest names.
 *
 * Messages with the page (socket.ts):
 *   in:  {kind: "init", base} once, then {kind: "request", raw} one at a time
 *   out: {kind: "ready", texts} | {kind: "reply", raw} | {kind: "event", raw}
 *        | {kind: "job", seconds, reply} | {kind: "phase", reply} | {kind: "finished"}
 *        | {kind: "fatal", message} (could not start) | {kind: "crashed", message}
 */

interface Manifest {
  pyodide: string;
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
}

interface Engine {
  handle(raw: string): Promise<string>;
}

const scope = self as unknown as DedicatedWorkerGlobalScope;

let engine: Engine | null = null;

const post = (message: Record<string, unknown>) => scope.postMessage(message);
const quiet = { messageCallback: () => undefined };

async function start(base: string): Promise<void> {
  const response = await fetch(new URL("manifest.json", base), { cache: "no-cache" });
  if (!response.ok) throw new Error(`manifest.json: HTTP ${response.status}`);
  const manifest = (await response.json()) as Manifest;

  const indexURL = `https://cdn.jsdelivr.net/pyodide/v${manifest.pyodide}/full/`;
  const { loadPyodide } = (await import(/* @vite-ignore */ `${indexURL}pyodide.mjs`)) as {
    loadPyodide: (options: { indexURL: string }) => Promise<PyodideApi>;
  };
  const py = await loadPyodide({ indexURL });
  await py.loadPackage(manifest.packages, quiet);
  await py.loadPackage(manifest.wheels.map((wheel) => new URL(wheel, base).href), quiet);
  const bundle = await fetch(new URL(manifest.bundle, base));
  if (!bundle.ok) throw new Error(`${manifest.bundle}: HTTP ${bundle.status}`);
  py.unpackArchive(await bundle.arrayBuffer(), "zip", { extractDir: "/engine" });

  py.globals.set("host", {
    job_started: (seconds: number, reply: string) => post({ kind: "job", seconds, reply }),
    job_phase: (reply: string) => post({ kind: "phase", reply }),
    job_finished: () => post({ kind: "finished" }),
    send_event: (raw: string) => post({ kind: "event", raw }),
  });
  engine = (await py.runPythonAsync(`
import sys
sys.path.insert(0, "/engine")
from qlp_engine.browser import BrowserEngine
BrowserEngine.warm_up()
BrowserEngine("/engine/content", host)
`)) as Engine;
  post({ kind: "ready", texts: JSON.parse(String(py.runPython("BrowserEngine.texts()"))) });
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
    try {
      post({ kind: "reply", raw: await engine.handle(message.raw!) });
    } catch (error) {
      // Python itself broke (out of memory, a WebAssembly trap): the page starts a new worker.
      post({ kind: "crashed", message: String(error instanceof Error ? error.message : error) });
    }
  }
};
