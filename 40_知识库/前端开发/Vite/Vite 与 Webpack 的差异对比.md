---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Vite
  - Webpack
created: 2026-05-08
---
# Vite 与 Webpack 的差异对比

## 定义

Vite 与 Webpack 都是前端工程化工具，但 Vite 开发环境基于原生 ESM 和按需转换，Webpack 更偏完整依赖图打包与高度可配置。

## 对比要点

- 开发启动：Vite 通常更快，Webpack 需要构建依赖图。
- 生产构建：Vite 默认使用 Rollup，Webpack 使用自身打包器。
- 生态成熟度：Webpack 老项目和复杂配置更多。
- 插件模型：Vite 兼容 Rollup 插件并扩展开发服务器钩子。

## 相关概念

- [[Vite 原理与插件机制总览]]
- [[Webpack]]
- [[包管理与依赖治理]]
