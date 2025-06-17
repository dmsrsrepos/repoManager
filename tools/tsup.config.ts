import { defineConfig } from 'tsup'
import type { Options } from 'tsup'

const tsupOptions: Options = {
  platform: 'node', // 目标平台
  entry: ['./checkCodeRunnerEnvironment.ts'],
  format: ['esm'],
  outExtension({ format }) {
    switch (format) {
      case 'cjs':
        return {
          js: '.js',
          dts: '.d.ts',
        }
      case 'esm':
        return {
          js: '.js',
          dts: '.d.ts',
        }
      case 'iife':
        return {
          js: '.global.js',
          dts: '.d.ts',
        }
      default:
        break
    }
    return {
      js: '.js',
      dts: '.d.ts',
    }
  },
  splitting: false, // 代码拆分
  sourcemap: false,
  clean: false,
  dts: false,
  minify: false, // 缩小输出
  shims: false, // 注入 cjs 和 esm 填充代码，解决 import.meta.url 和 __dirname 的兼容问题
  esbuildOptions(options, _context) { // 设置编码格式
    options.charset = 'utf8'
  },
  banner: {
    js: '#!/usr/bin/env node',
  },
  // external: [], // 排除的依赖项
  // noExternal: [/(.*)/], // 将依赖打包到一个文件中
  // bundle: true,
  outDir: './',
}

export default defineConfig([tsupOptions])
