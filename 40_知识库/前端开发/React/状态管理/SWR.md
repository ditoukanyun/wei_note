---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - React
  - 服务器状态
created: 2026-05-08
---
# SWR

## 定义

SWR 是一种 React 数据获取策略和同名库，名称来自 Stale-While-Revalidate。它先返回缓存中的旧数据，再在后台重新验证并更新数据。

## 要点

- 适合读取型接口和允许短暂陈旧的页面数据。
- 用 key 表示请求身份，用 fetcher 执行实际请求。
- 自动处理缓存、重新聚焦刷新、错误重试和加载状态。

## 相关概念

- [[Stale-While-Revalidate]]
- [[React Query]]
- [[TanStack-Query]]
