---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Next.js
created: 2026-05-08
---
# Next.js App Router 路由机制

## 定义

Next.js App Router 使用 `app` 目录和文件约定描述路由、布局、加载态、错误边界和页面结构。

## 要点

- `page.tsx` 定义路由页面。
- `layout.tsx` 定义共享布局。
- `loading.tsx` 和 `error.tsx` 处理加载与错误状态。
- 动态路由通过方括号目录表达。

## 相关概念

- [[Next.js App Router 总览]]
- [[Next.js 服务端组件 RSC]]

## 路由流程

```mermaid
flowchart LR
  A[请求路径] --> B[匹配 app 目录]
  B --> C[组合 layout]
  C --> D[渲染 page]
  D --> E[处理 loading 和 error]
```

## 实践检查清单

- 路由段是否按业务领域组织，而不是按组件类型堆放。
- layout 是否只放真正共享的 UI 和数据。
- loading、error、not-found 是否覆盖关键页面。
- 动态路由参数是否做校验和不存在处理。
- 服务端组件和客户端组件边界是否明确。

## 案例

后台订单模块可以使用 `app/orders/page.tsx` 展示列表，`app/orders/[id]/page.tsx` 展示详情，共享筛选布局放在订单目录的 `layout.tsx` 中。

## 常见误区

- 所有共享逻辑都塞进根 layout，导致页面耦合。
- 忘记错误边界，服务端请求失败时整页崩溃。
- 不区分服务端和客户端组件，把交互逻辑放错位置。
