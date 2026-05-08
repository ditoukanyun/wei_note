---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Next.js
  - 渲染
created: 2026-05-08
---
# Next.js SSR、SSG、ISR 对比

## 定义

SSR、SSG、ISR 是 Next.js 常见渲染策略，分别强调请求时渲染、构建时生成和按时间增量再生成。

## 对比

- SSR：每次请求生成页面，适合强动态内容。
- SSG：构建时生成静态页面，适合稳定内容。
- ISR：静态页面按策略重新生成，兼顾性能和新鲜度。

## 相关概念

- [[Next.js App Router 总览]]
- [[缓存系统总览]]
- [[Stale-While-Revalidate]]
