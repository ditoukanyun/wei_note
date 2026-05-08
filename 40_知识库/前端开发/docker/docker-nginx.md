---
type: wiki
area: "[[前端开发]]"
tags:
  - Docker
  - Nginx
created: 2026-05-08
---
# docker-nginx

docker-nginx 是用 Nginx 镜像托管静态资源、反向代理 API 或作为前端容器运行时的常见方式。

## 要点

- 前端构建产物可复制到 Nginx 静态目录。
- SPA 需要配置路由 fallback。
- 反向代理时要正确传递 Host、X-Forwarded-* 等头。

## 相关概念

- [[Nginx 反向代理与 HTTPS 配置]]
- [[docker-dockerfile]]
- [[前后端项目部署方案详解]]
