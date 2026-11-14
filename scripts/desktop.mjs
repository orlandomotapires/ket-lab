// Roda um comando do shell desktop (Tauri) com o ambiente limpo.
// Uso: node scripts/desktop.mjs dev | build | run
//
// Por que existe: o VS Code instalado via snap injeta no terminal variáveis
// (GTK_PATH, GIO_MODULE_DIR, LOCPATH...) que apontam para bibliotecas do próprio
// snap. Qualquer programa WebKitGTK iniciado desse terminal carrega as
// bibliotecas erradas e morre com "symbol lookup error". Aqui elas voltam ao
// valor original antes de o aplicativo ser iniciado.
import { spawn } from "node:child_process";
import { createConnection } from "node:net";
import { cpSync, existsSync, rmSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

export function cleanEnvironment(source = process.env) {
  const env = { ...source };
  const SUFFIX = "_VSCODE_SNAP_ORIG";
  for (const [key, original] of Object.entries(source)) {
    if (!key.endsWith(SUFFIX)) continue;
    const name = key.slice(0, -SUFFIX.length);
    if (original) env[name] = original;
    else delete env[name];
    delete env[key];
  }
  for (const [key, value] of Object.entries(env)) {
    const gtkRelated = /^(GTK_|GDK_|GIO_|GSETTINGS_|LOCPATH$)/.test(key);
    if (gtkRelated && typeof value === "string" && value.includes("/snap/")) delete env[key];
  }
  const cargoBin = join(homedir(), ".cargo", "bin");
  if (existsSync(cargoBin) && !(env.PATH ?? "").split(":").includes(cargoBin)) {
    env.PATH = `${cargoBin}:${env.PATH ?? ""}`;
  }
  return env;
}

const tauri = join(root, "node_modules", "@tauri-apps", "cli", "tauri.js");
const binary = join(
  root, "src-tauri", "target", "release",
  process.platform === "win32" ? "quantum-learning-platform.exe" : "quantum-learning-platform",
);

const commands = {
  // Janela de desenvolvimento: recarrega a interface a cada alteração.
  dev: [process.execPath, [tauri, "dev"]],
  // Build de produção com o motor empacotado e os instaladores da plataforma.
  build: [process.execPath, [tauri, "build", "--config", "src-tauri/tauri.release.conf.json", ...process.argv.slice(3)]],
  // Abre o último build de produção.
  run: [binary, process.argv.slice(3)],
};

function portInUse(port) {
  return new Promise((resolve) => {
    const socket = createConnection({ host: "127.0.0.1", port });
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.once("error", () => resolve(false));
  });
}

async function main() {
  const name = process.argv[2];
  const selected = commands[name];
  if (!selected) {
    console.error("Uso: node scripts/desktop.mjs dev | build | run");
    process.exit(1);
  }
  // Com a porta ocupada, o Tauri falha ao subir o Vite e deixa uma janela órfã.
  if (name === "dev" && (await portInUse(5173))) {
    console.error(
      "A porta 5173 já está em uso, provavelmente por um `npm run dev` aberto.\n" +
        "Encerre-o antes de rodar `npm run desktop:dev`.",
    );
    process.exit(1);
  }
  if (name === "build") {
    // O Tauri copia o motor para target/release sem apagar o que já estava lá: lições
    // renomeadas deixariam pastas antigas (e ids duplicados) dentro do instalador.
    // Por isso a cópia é refeita aqui, a partir do motor recém-empacotado.
    const target = join(root, "src-tauri", "target", "release", "qlp-engine");
    rmSync(target, { recursive: true, force: true });
    const packaged = join(root, "engine", "dist", "qlp-engine");
    if (existsSync(packaged)) cpSync(packaged, target, { recursive: true });
  }
  const child = spawn(selected[0], selected[1], { cwd: root, env: cleanEnvironment(), stdio: "inherit" });
  child.on("exit", (code, signal) => process.exit(code ?? (signal ? 1 : 0)));
  for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => child.kill(signal));
}

// Só executa quando chamado diretamente (o módulo também é importado por utilitários).
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) await main();
