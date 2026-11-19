// Browser mode: the production build with VITE_ENGINE=browser, no engine server.
// Needs the staged engine files: build-wasm/build.sh, then python3 build-wasm/stage.py.
import { defineConfig } from "@playwright/test";
import base from "./playwright.config";

const APP_PORT = 5183;
const appUrl = `http://127.0.0.1:${APP_PORT}`;

export default defineConfig({
  ...base,
  testMatch: "browser-engine.spec.ts",
  testIgnore: [],
  expect: { timeout: 180_000 },
  use: { ...base.use, baseURL: appUrl },
  webServer: [
    {
      command: `node node_modules/vite/bin/vite.js build --outDir dist-browser && node node_modules/vite/bin/vite.js preview --outDir dist-browser --port ${APP_PORT} --strictPort --host 127.0.0.1`,
      url: appUrl,
      env: { VITE_ENGINE: "browser" },
      reuseExistingServer: false,
      timeout: 180_000,
    },
  ],
});
