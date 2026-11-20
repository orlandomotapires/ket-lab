// End-to-end tests: start an isolated engine and Vite (own ports and data).
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "@playwright/test";

const ENGINE_PORT = 8791;
const APP_PORT = 5181;
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const python = process.platform === "win32"
  ? join(root, "engine", ".venv", "Scripts", "python.exe")
  : join(root, "engine", ".venv", "bin", "python");
// Progress reset on every run.
const dataDir = mkdtempSync(join(tmpdir(), "ket-lab-e2e-"));
const appUrl = `http://127.0.0.1:${APP_PORT}`;

export default defineConfig({
  testDir: "e2e",
  testIgnore: ["hosted.spec.ts", "browser-engine.spec.ts"],
  timeout: 60_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: appUrl,
    viewport: { width: 1600, height: 900 },
    // Locally uses the system Chrome; on CI, the Chromium installed by Playwright.
    channel: process.env.CI ? undefined : "chrome",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command: `"${process.env.KET_LAB_PYTHON ?? python}" -m ket_lab_engine --port ${ENGINE_PORT} --token e2e --allow-origin ${appUrl} --data-dir "${dataDir}"`,
      cwd: join(root, "engine"),
      // IBM Quantum simulated: the hardware dialog test makes no network calls.
      env: { KET_LAB_FAKE_IBM: "1" },
      port: ENGINE_PORT,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: `node node_modules/vite/bin/vite.js --port ${APP_PORT} --strictPort --host 127.0.0.1`,
      url: appUrl,
      env: { VITE_ENGINE_PORT: String(ENGINE_PORT), VITE_ENGINE_TOKEN: "e2e" },
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
