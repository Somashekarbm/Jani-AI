import { defineConfig } from 'vite';
import { node } from '@electron-forge/plugin-vite/dist/vite-plugin.js';

export default defineConfig({
  plugins: [node()],
  build: {
    rollupOptions: {
      external: ['electron'],
    },
  },
});