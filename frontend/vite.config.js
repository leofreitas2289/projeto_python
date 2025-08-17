import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react( )],
  server: {
    host: true,
    allowedHosts: ["5174-i8l55yqmpt9867xvcyz6h-674df8ca.manus.computer"],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path ) => path.replace(/^\/api/, '')
      }
    }
  }
})
