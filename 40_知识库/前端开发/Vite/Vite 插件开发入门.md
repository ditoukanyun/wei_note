---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Vite
  - 插件
created: 2026-05-08
---
# Vite 插件开发入门

## 定义

Vite 插件通过 Rollup 插件钩子和 Vite 专属钩子扩展构建、转换和开发服务器能力。

## 常用钩子

- `config`：修改 Vite 配置。
- `resolveId`：自定义模块解析。
- `load`：加载虚拟模块。
- `transform`：转换模块代码。
- `configureServer`：扩展开发服务器。

## 相关概念

- [[Vite 原理与插件机制总览]]
- [[Webpack]]
- [[模块化]]
