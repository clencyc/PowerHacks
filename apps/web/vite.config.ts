import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

export default defineConfig(({ mode }) => ({
  // VERY IMPORTANT for Render static sites
  base: mode === "production" ? "/" : undefined,

  server: {
    host: "::",
    port: 8080,
    // This only works for dev server, Render ignores it anyway
    allowedHosts: ["powerhacks-2.onrender.com"],  // ← remove or comment out
  },

  plugins: [
    react({
      // You are using SWC → this is correct and recommended in 2025
    }),
  ],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  build: {
    outDir: "dist",
    sourcemap: false,           // set true only if you need debugging
    rollupOptions: {
      output: {
        // Prevents very large chunks that sometimes confuse Render
        manualChunks: undefined,
      },
    },
  },
}));