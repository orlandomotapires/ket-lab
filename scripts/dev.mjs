// Sobe o motor Python e o Vite juntos para desenvolvimento no navegador.
// Uso: npm run dev   (na raiz do repositório)
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const venv = join(root, "engine", ".venv");
const python = process.platform === "win32" ? join(venv, "Scripts", "python.exe") : join(venv, "bin", "python");

if (!existsSync(python)) {
  console.error("Ambiente Python ausente. Rode primeiro:  npm run setup");
  process.exit(1);
}

const PORT = process.env.VITE_ENGINE_PORT ?? "8765";
const TOKEN = process.env.VITE_ENGINE_TOKEN ?? "dev";
// QLP_DATA_DIR isola o progresso (útil em testes); sem ele, usa o diretório de dados do usuário.
const dataDir = process.env.QLP_DATA_DIR ? ["--data-dir", process.env.QLP_DATA_DIR] : [];
const origins = ["http://localhost:5173", "http://127.0.0.1:5173"].flatMap((o) => ["--allow-origin", o]);

const children = [
  spawn(python, ["-m", "qlp_engine", "--port", PORT, "--token", TOKEN, ...origins, ...dataDir], {
    cwd: join(root, "engine"),
    stdio: "inherit",
  }),
  // O Vite é iniciado direto pelo Node (e não via npm) para que o encerramento o alcance.
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
