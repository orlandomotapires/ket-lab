import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";
import packageJson from "./package.json";

// VITE_ENGINE_PROXY simulates the hosted deploy in development: /engine goes to the engine,
// as nginx does in deploy/nginx.conf.
const env = (globalThis as { process?: { env: Record<string, string | undefined> } }).process?.env ?? {};
const engineProxy = env.VITE_ENGINE_PROXY;

export default defineConfig({
  // VITE_BASE: the path the site is served under, e.g. "/ket-lab/" on GitHub Pages.
  base: env.VITE_BASE ?? "/",
  plugins: [react()],
  // The version in the About dialog comes from package.json, so it always matches the release.
  define: { __APP_VERSION__: JSON.stringify(packageJson.version) },
  server: {
    port: 5173,
    strictPort: true,
    host: "127.0.0.1",
    proxy: engineProxy
      ? { "/engine": { target: engineProxy, ws: true, rewrite: (path) => path.replace(/^\/engine/, "") || "/" } }
      : undefined,
  },
  build: { target: "es2022", chunkSizeWarningLimit: 4000 },
  // The browser engine's worker loads Pyodide with a dynamic import: needs an ES module worker.
  worker: { format: "es" },
  test: { environment: "node", include: ["src/**/*.test.ts"] },
});
