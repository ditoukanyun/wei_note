---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - React
created: 2026-05-08
---
# Suspense

## 定义

Suspense 是 React 用于声明异步等待边界的机制，可以在子树数据或代码尚未准备好时展示 fallback。

## 要点

- 常与 lazy 代码分割、服务端组件和数据获取框架配合。
- fallback 应保持稳定，避免造成布局跳动。
- Suspense 边界是用户体验和加载策略的设计边界。

## 相关概念

- [[代码分割]]
- [[React Hooks]]
- [[Next.js 服务端组件 RSC]]
