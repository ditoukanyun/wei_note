---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Next.js
  - 部署
created: 2026-05-08
---
# Next.js 认证、缓存与部署实践

## 定义

Next.js 认证、缓存与部署实践关注 App Router 应用在登录态、数据缓存、运行时选择和生产发布中的工程边界。

## 要点

- 认证要区分服务端读取 Cookie、客户端会话状态和后端授权。
- 缓存策略需要明确页面、请求和 CDN 层级。
- 部署前要确认 Node/Edge Runtime、环境变量和日志监控。

## 相关概念

- [[Next.js App Router 总览]]
- [[前端鉴权与 Token 存储安全]]
- [[云原生部署总览：Docker、Kubernetes 与 CI-CD]]
