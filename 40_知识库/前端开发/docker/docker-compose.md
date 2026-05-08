---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Docker
created: 2026-05-08
---
# docker-compose

## 定义

docker-compose 是 Docker Compose 命令的常见写法，用于通过 YAML 文件定义并启动多容器应用，适合本地开发和集成测试环境。

## 要点

- `services` 定义应用、数据库、缓存等容器。
- `volumes` 保存持久化数据。
- `networks` 让容器通过服务名互相访问。
- 前后端联调可用 Compose 固化 Node、Nginx、MySQL、Redis 等依赖。

## 相关概念

- [[Docker]]
- [[docker-网络]]
- [[docker-数据卷]]
