import { defineConfig } from "vitest/config";
import content, { BUILD_DAY } from "./scripts/vite-content.mjs";

export default defineConfig({
  plugins: [content()],
  define: { __BUILD_DAY__: JSON.stringify(BUILD_DAY) },
  test: {
    include: ["tests/**/*.test.js"],
    environment: "node",
    testTimeout: 20000
  }
});
