import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Purpose: standard Vite + React setup. Dev server runs on 5173, which is
// the origin whitelisted in the backend's CORS config (app/main.py).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
