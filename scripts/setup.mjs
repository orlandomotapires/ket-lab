// Prepares the development environment: checks versions, creates the Python
// virtual environment, installs the engine and the interface dependencies.
// Usage: npm run setup   (from the repository root)
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const windows = process.platform === "win32";
const venv = join(root, "engine", ".venv");
const venvPython = windows ? join(venv, "Scripts", "python.exe") : join(venv, "bin", "python");

function fail(message) {
  console.error(`\n${message}`);
  process.exit(1);
}

function run(command, args, options = {}) {
  console.log(`\n> ${command} ${args.join(" ")}`);
  const result = spawnSync(command, args, { stdio: "inherit", cwd: root, shell: windows, ...options });
  if (result.status !== 0) fail(`"${command} ${args.join(" ")}" failed. Fix the error above and run npm run setup again.`);
}

// Checked first, so nothing is installed for a version that cannot run the project.
const nodeMajor = Number(process.versions.node.split(".")[0]);
if (nodeMajor < 22) {
  fail(`Node ${process.versions.node} is too old: this project needs Node 22 or newer.\nInstall it with nvm (nvm install 22) or fnm (fnm install 22), then run npm run setup again.`);
}

/** First Python 3.11+ found among the usual names. */
function findPython() {
  for (const candidate of windows ? ["py", "python"] : ["python3", "python"]) {
    const probe = spawnSync(candidate, ["-c", "import sys; print(sys.version_info[0], sys.version_info[1])"], { encoding: "utf-8", shell: windows });
    if (probe.status !== 0) continue;
    const [major, minor] = probe.stdout.trim().split(" ").map(Number);
    if (major === 3 && minor >= 11) return candidate;
    console.error(`${candidate} is Python ${major}.${minor}; 3.11 or newer is needed.`);
  }
  return null;
}

if (!existsSync(venvPython)) {
  const python = findPython();
  if (!python) fail("Python 3.11 or newer was not found. Install it from https://www.python.org/downloads/ and run npm run setup again.");
  run(python, ["-m", "venv", venv]);
}
run(venvPython, ["-m", "pip", "install", "-e", "engine[dev]"]);
// npm ci installs exactly what package-lock.json records.
run("npm", ["ci"], { cwd: join(root, "app") });

console.log("\nReady. Start the platform with:  npm run dev");
