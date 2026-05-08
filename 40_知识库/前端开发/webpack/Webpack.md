---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Webpack
  - 工程化
created: 2026-05-08
---
# Webpack

## 定义

Webpack 是一个模块打包工具，把 JavaScript、CSS、图片等资源视为模块，通过 Loader 和 Plugin 构建依赖图并输出浏览器可加载的产物。

## 要点

- Loader 负责把不同类型资源转换为模块。
- Plugin 参与构建生命周期，扩展打包能力。
- Code Splitting、Tree Shaking 和缓存命名影响生产性能。
- Vite 更偏开发体验和原生 ESM，Webpack 仍适合复杂定制场景。

## 相关概念

- [[webpack/README]]
- [[Vite 与 Webpack 的差异对比]]
- [[代码分割]]
