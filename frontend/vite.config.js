import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Split the heavy, rarely-changing vendors so a UI change does not invalidate
// them in the browser cache.
export default defineConfig({
  plugins: [react()],
  build: {
    target: "es2020",
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return;
          if (id.includes("@xyflow")) return "graph";
          if (id.includes("recharts") || id.includes("d3-")) return "charts";
          if (id.includes("framer-motion")) return "motion";
          if (id.includes("react-router")) return "router";
          if (id.includes("react-dom") || id.includes("/react/") || id.includes("scheduler")) {
            return "react";
          }
          return "vendor";
        },
      },
    },
  },
});
