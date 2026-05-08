---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - React
  - SSR
created: 2026-05-08
---
# SSR Hydration

## 定义

SSR Hydration 是客户端 React 接管服务端已经生成的 HTML，并绑定事件、恢复交互能力的过程。

## 要点

- 服务端和客户端首屏输出不一致会造成 hydration mismatch。
- 依赖浏览器 API 的逻辑需要放到客户端边界或 effect 中。
- 状态持久化和主题切换容易影响首屏一致性。

## 相关概念

- [[Next.js 服务端组件 RSC]]
- [[状态持久化]]
- [[React 基础]]
