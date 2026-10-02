import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import content, { BUILD_DAY } from './scripts/vite-content.mjs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), content()],
  define: { __BUILD_DAY__: JSON.stringify(BUILD_DAY) },
  build: {
    // scripts/prerender.mjs reads it to preload each page's own chunks.
    manifest: true,
    // One stylesheet, linked from every prerendered page. Split per route, a
    // page's CSS would arrive with its script, after the HTML had painted.
    cssCodeSplit: false,
  },
})
