---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Next.js
  - React
created: 2026-04-30
---
# Next.js App Router 总览

## 学习目标

- 理解 App Router 相比 Pages Router 的核心变化。
- 掌握路由、布局、服务端组件、数据获取、缓存和部署的基本模型。
- 能判断页面应该使用 SSR、SSG、ISR 还是客户端渲染。

## 核心概念

- **文件系统路由**：`app` 目录中的文件和文件夹决定路由结构。
- **Layout**：跨页面共享 UI 和状态边界。
- **Server Components**：默认在服务端渲染，减少客户端 JavaScript 体积。
- **Client Components**：通过 `use client` 使用浏览器 API、事件和客户端状态。
- **缓存策略**：数据请求、路由段和页面输出都有独立缓存语义。

## 推荐阅读顺序

1. [[React 基础]]：先理解组件和状态。
2. [[Hooks]]：理解客户端组件中的交互逻辑。
3. 本文：建立 Next.js App Router 总览。
4. 后续拆分文章：路由、RSC、缓存、认证、部署。

## 工程实践清单

- 默认优先使用 Server Components，只有需要交互或浏览器 API 时才使用 Client Components。
- 数据获取尽量靠近使用位置，避免把所有请求集中到页面顶层。
- 认证、缓存和重定向需要结合运行环境设计，不能只按客户端 SPA 思路处理。
- 部署前检查运行时、环境变量、图片优化和缓存失效策略。

## 后续可拆分文章

- [[Next.js App Router 路由机制]]
- [[Next.js 服务端组件 RSC]]
- [[Next.js SSR、SSG、ISR 对比]]
- [[Next.js 认证、缓存与部署实践]]

## 相关链接

- [[前端开发 MOC]]
- [[React 基础]]
- [[Web Vitals 与前端性能监控总览]]
