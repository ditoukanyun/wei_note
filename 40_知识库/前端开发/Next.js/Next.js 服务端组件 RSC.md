---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Next.js
  - React
created: 2026-05-08
---
# Next.js 服务端组件 RSC

## 定义

React Server Components 允许组件在服务端执行并返回序列化结果，减少客户端 JavaScript 体积并更贴近数据源渲染页面。

## 要点

- 默认服务端组件不能使用浏览器 API 和客户端状态。
- 需要交互时使用 `"use client"` 标记客户端组件边界。
- 服务端组件适合读取数据和组装页面结构。

## 相关概念

- [[Next.js App Router 总览]]
- [[SSR Hydration]]
- [[React 基础]]
