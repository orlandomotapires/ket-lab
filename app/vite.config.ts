import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// VITE_ENGINE_PROXY simula o deploy hospedado no desenvolvimento: /engine vai para o motor,
// como faz o nginx em deploy/nginx.conf.
const engineProxy = (globalThis as { process?: { env: Record<string, string | undefined> } }).process?.env.VITE_ENGINE_PROXY;

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    host: "127.0.0.1",
    proxy: engineProxy
      ? { "/engine": { target: engineProxy, ws: true, rewrite: (path) => path.replace(/^\/engine/, "") || "/" } }
      : undefined,
  },
  build: { target: "es2022", chunkSizeWarningLimit: 4000 },
  test: { environment: "node", include: ["src/**/*.test.ts"] },
});
