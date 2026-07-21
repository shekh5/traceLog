import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// Built assets are served by the FastAPI dashboard (dashboard/main.py mounts
// web/dist). In dev, proxy the live API to the running FastAPI backend.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  return {
    base: env.VITE_BASE_PATH || "/",
    plugins: [react()],
    build: { outDir: "dist", emptyOutDir: true },
    server: {
      port: 5173,
      proxy: {
        "/events": { target: "http://127.0.0.1:8085", changeOrigin: true },
        "/ask": { target: "http://127.0.0.1:8085", changeOrigin: true },
      },
    },
  };
});
