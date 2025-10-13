import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  
  const isProduction = mode === 'production'
  const isDevelopment = mode === 'development'
  
  const plugins = [react()]
  
  // Add bundle analyzer in analyze mode
  if (mode === 'analyze') {
    plugins.push(
      visualizer({
        filename: 'dist/stats.html',
        open: true,
        gzipSize: true,
        brotliSize: true,
      })
    )
  }
  
  return {
    plugins,
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      port: parseInt(env.VITE_DEV_PORT) || 5173,
      host: true, // Allow external connections
      proxy: isDevelopment ? {
        '/api': {
          target: env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          timeout: parseInt(env.VITE_REQUEST_TIMEOUT) || 30000,
        },
        '/ws': {
          target: env.VITE_WS_PROXY_TARGET || 'ws://localhost:8000',
          ws: true,
          changeOrigin: true,
          timeout: parseInt(env.VITE_REQUEST_TIMEOUT) || 30000,
        },
      } : {},
    },
    build: {
      outDir: 'dist',
      sourcemap: env.VITE_ENABLE_SOURCE_MAPS === 'true' || isDevelopment,
      minify: isProduction,
      rollupOptions: {
        output: {
          manualChunks: {
            // Vendor chunk for large dependencies
            vendor: ['react', 'react-dom'],
            charts: ['recharts', 'cytoscape'],
            ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', 'framer-motion'],
          },
        },
      },
      // Build optimizations
      chunkSizeWarningLimit: 1000,
    },
    define: {
      // Ensure NODE_ENV is properly set for production builds
      'process.env.NODE_ENV': JSON.stringify(mode),
    },
    // Enable devtools in development only
    esbuild: {
      drop: isProduction ? ['console', 'debugger'] : [],
    },
  }
})
