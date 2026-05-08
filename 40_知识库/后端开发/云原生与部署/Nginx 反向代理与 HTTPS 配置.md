---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - Nginx
  - HTTPS
created: 2026-05-08
---
# Nginx 反向代理与 HTTPS 配置

## 定义

Nginx 反向代理与 HTTPS 配置用于把外部请求转发到内部前端静态资源或后端服务，并通过 TLS 保护传输安全。

## 要点

- 静态资源可由 Nginx 直接托管。
- API 请求通过 `proxy_pass` 转发到后端服务。
- HTTPS 需要证书、私钥、安全协议和自动续期。
- 前端路由需要配置 fallback 到入口 HTML。

## 相关概念

- [[前后端项目部署方案详解]]
- [[Nginx 多前端项目部署]]
- [[云原生部署总览：Docker、Kubernetes 与 CI-CD]]
