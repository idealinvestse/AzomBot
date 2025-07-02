import { defineConfig } from "vite";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(dirname(fileURLToPath(import.meta.url)), "src"),
    },
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      "/chat": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/pipeline": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/admin": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/ping": {
        target: "http://localhost:8008",
        changeOrigin: true,
      },
    },
  }
});
