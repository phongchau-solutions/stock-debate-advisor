import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8001/api', // Backend API
        changeOrigin: true,
        secure: false,
      },
    },
  },
  define: {
    // Ensure env vars are available at build time
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify(process.env.VITE_API_BASE_URL || 'http://localhost:8001/api'),
  },
});
