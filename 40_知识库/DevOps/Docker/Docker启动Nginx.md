---
type: wiki
area: "[[DevOps]]"
tags: [Docker, Nginx]
created: 2026-05-08
---
# Docker启动Nginx
Docker启动Nginx 是用容器运行 Nginx 的操作笔记，可用于静态资源托管和反向代理实验。

## 相关概念
- [[docker-nginx]]
- [[Nginx 反向代理与 HTTPS 配置]]

## 启动流程

```mermaid
flowchart LR
  A[准备配置文件] --> B[挂载静态目录或配置]
  B --> C[启动 Nginx 容器]
  C --> D[访问端口验证]
  D --> E[查看日志和代理结果]
```

## 实践检查清单

- 是否固定镜像版本，避免环境变化。
- 静态资源目录和配置文件是否通过卷挂载或镜像构建固化。
- SPA 项目是否配置路由 fallback。
- 反向代理是否传递 Host、真实 IP 和协议头。
- 是否通过 `nginx -t` 或容器日志验证配置。

## 案例

本地验证前端构建产物时，可以把 `dist` 目录挂载到 Nginx 静态目录，再映射 8080 端口访问。若刷新子路由 404，需要补 `try_files` fallback。

## 常见误区

- 在运行中的容器内手工改配置，重建后全部丢失。
- API 代理未设置超时和请求头，导致后端日志无法识别真实客户端。
- HTML 和静态资源使用相同缓存策略，发布后用户加载旧页面。
