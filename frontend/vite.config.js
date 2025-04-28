import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'  // ✅ 경로 모듈 import

export default defineConfig({
  base: "./",
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),  // ✅ @를 src 폴더로 매핑
    },
  },
})