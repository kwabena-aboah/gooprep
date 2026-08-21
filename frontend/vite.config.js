import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    // base: '/demo/', // sub directory config
    plugins: [vue()],
    resolve: { alias: { '@': resolve(__dirname, 'src') } },
    server: {
      port: 5173,
      proxy: {
        '/api':   { target: env.VITE_API_URL || 'http://localhost:8000', changeOrigin: true, secure: false },
        '/ws':    { target: env.VITE_WS_URL  || 'ws://localhost:8001',  ws: true, changeOrigin: true },
        '/media': { target: env.VITE_API_URL || 'http://localhost:8000', changeOrigin: true },
      }
    },
    build: {
      outDir: 'dist',
      rollupOptions: {
        output: {
          manualChunks: { vendor: ['vue','vue-router','pinia'], bootstrap: ['bootstrap'], axios: ['axios'] }
        }
      }
    }
  }
})
