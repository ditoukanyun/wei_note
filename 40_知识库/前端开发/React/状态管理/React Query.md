---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - React
  - 服务器状态
created: 2026-05-08
---
# React Query

## 定义

React Query 是 [[TanStack-Query]] 的早期名称和 React 生态常用称呼，用于管理服务器状态，包括请求、缓存、重新验证、分页、乐观更新和错误重试。

## 要点

- 适合 API 数据、加载状态、错误状态和缓存失效。
- 不应把服务器状态重复同步到 Redux 或 Zustand。
- 查询键决定缓存身份，失效策略决定数据刷新时机。

## 相关概念

- [[TanStack-Query]]
- [[SWR]]
- [[组件设计与状态边界]]
