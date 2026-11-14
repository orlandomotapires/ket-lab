// Modo hospedado: motor com --public atrás de um proxy em /engine (como em deploy/).
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "@playwright/test";
import base from "./playwright.config";

const ENGINE_PORT = 8792;
const APP_PORT = 5182;
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const python = process.platform === "win32"
  ? join(root, "engine", ".venv", "Scripts", "python.exe")
  : join(root, "engine", ".venv", "bin", "python");
const appUrl = `http://127.0.0.1:${APP_PORT}`;

export default defineConfig({
  ...base,
  testMatch: "hosted.spec.ts",
  testIgnore: [],
  use: { ...base.use, baseURL: appUrl },
  webServer: [
    {
      command: `"${process.env.QLP_PYTHON ?? python}" -m qlp_engine --public --port ${ENGINE_PORT} --workers 2 --allow-origin ${appUrl}`,
      cwd: join(root, "engine"),
      port: ENGINE_PORT,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: `node node_modules/vite/bin/vite.js --port ${APP_PORT} --strictPort --host 127.0.0.1`,
      url: appUrl,
      env: { VITE_ENGINE_URL: "/engine", VITE_ENGINE_PROXY: `http://127.0.0.1:${ENGINE_PORT}` },
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
