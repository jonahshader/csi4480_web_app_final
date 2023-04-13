import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const apiurl = "http://127.0.0.1:8000/"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      src: "/src",
    },
  },
  server: {
    host: true,
    cors: false,
    proxy: {
      '/api': {
        target: apiurl,
        changeOrigin: true,
        secure: false
      },
    }
  }
})
 
