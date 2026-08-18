import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    allowedHosts: true,
    headers: {
      "Permissions-Policy": "geolocation=(self)",
    },
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
      },
      "/api/public": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
      },
      "/backend": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/backend/, ""),
      },
      "/static": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
      },
      "/media": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
      },
    },
  },
});
