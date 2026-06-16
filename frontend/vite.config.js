import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      // Jika React melihat request ke '/api', lempar ke Flask (Port 5000)
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
