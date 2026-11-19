// Browser mode: the production build with VITE_ENGINE=browser, no engine server.
// Needs the staged engine files: build-wasm/build.sh, then python3 build-wasm/stage.py.
// One browser only: --project chromium (or firefox, webkit).
import { defineConfig, devices } from "@playwright/test";
import base from "./playwright.config";

const APP_PORT = 5183;
// The base config picks the system Chrome locally: a channel only the Chromium project can use.
const { channel, ...shared } = base.use ?? {};
const appUrl = `http://127.0.0.1:${APP_PORT}`;

export default defineConfig({
  ...base,
  testMatch: "browser-engine.spec.ts",
  testIgnore: [],
  // A failure here is a browser that cannot run the engine: a retry repeats a 4-minute wait.
  retries: 0,
  expect: { timeout: 180_000 },
  use: { ...shared, baseURL: appUrl },
  // Pyodide must work in each engine: Chromium (Chrome, Edge), Firefox and WebKit (Safari).
  projects: [
    { name: "chromium", use: { browserName: "chromium", channel } },
    { name: "firefox", use: { browserName: "firefox" } },
    { name: "webkit", use: { browserName: "webkit" } },
    // Phone screens and touch (not a phone's CPU or memory limits: those need a real device).
    { name: "mobile-chrome", use: { ...devices["Pixel 7"] } },
    { name: "mobile-safari", use: { ...devices["iPhone 14"] } },
  ],
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
