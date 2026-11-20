// Starts the Python engine and Vite together for development in the browser.
// Usage: npm run dev   (from the repository root)
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const venv = join(root, "engine", ".venv");
const python = process.platform === "win32" ? join(venv, "Scripts", "python.exe") : join(venv, "bin", "python");

// Vite 7 needs Node 22 (see "engines" in app/package.json); older versions fail with a cryptic error.
const nodeMajor = Number(process.versions.node.split(".")[0]);
if (nodeMajor < 22) {
  console.error(`Node ${process.versions.node} is too old: this project needs Node 22 or newer.`);
  console.error("Install it with nvm (nvm install 22) or fnm (fnm install 22), then run npm run dev again.");
  process.exit(1);
}

if (!existsSync(python)) {
  console.error("Python environment missing. Run this first:  npm run setup");
  process.exit(1);
}

const PORT = process.env.VITE_ENGINE_PORT ?? "8765";
const TOKEN = process.env.VITE_ENGINE_TOKEN ?? "dev";
// KET_LAB_DATA_DIR isolates progress (useful in tests); without it, the user's data directory is used.
const dataDir = process.env.KET_LAB_DATA_DIR ? ["--data-dir", process.env.KET_LAB_DATA_DIR] : [];
const origins = ["http://localhost:5173", "http://127.0.0.1:5173"].flatMap((o) => ["--allow-origin", o]);

const children = [
  spawn(python, ["-m", "ket_lab_engine", "--port", PORT, "--token", TOKEN, ...origins, ...dataDir], {
    cwd: join(root, "engine"),
    stdio: "inherit",
  }),
  // Vite is started directly by Node (not via npm) so that shutdown reaches it.
  spawn(process.execPath, [join(root, "app", "node_modules", "vite", "bin", "vite.js")], {
    cwd: join(root, "app"),
    stdio: "inherit",
  }),
];

let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) child.kill();
  process.exit(code);
}
for (const child of children) child.on("exit", (code) => stop(code ?? 0));
process.on("SIGINT", () => stop(0));
process.on("SIGTERM", () => stop(0));
