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

## 启动流程

```mermaid
flowchart LR
    A["compose.yaml"] --> B["解析 services"]
    B --> C["创建 network/volume"]
    C --> D["拉取或构建镜像"]
    D --> E["按依赖启动容器"]
    E --> F["通过服务名互相访问"]
```

Compose 的价值是把本地依赖环境写成版本化配置，减少“每个人本机装法不同”的问题。

## 示例

```yaml
services:
  frontend:
    image: node:20
    working_dir: /app
    volumes:
      - .:/app
    command: pnpm dev
    ports:
      - "5173:5173"

  api:
    build: ../api
    ports:
      - "8080:8080"
    depends_on:
      - mysql

  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: demo
```

前端访问后端时，如果运行在宿主机浏览器里，应访问 `localhost:8080`；如果前端代码运行在容器里，应访问服务名 `api:8080`。

## 检查清单

- 端口映射是否只暴露本地开发需要的端口。
- 数据库、Redis 是否使用 volume 保存数据。
- 服务之间是否使用 Compose 服务名访问，而不是写死容器 IP。
- 密码和密钥是否只用于本地开发，不复用生产配置。
- 是否提供初始化脚本或种子数据，方便新人启动。
- 是否和 [[Docker]]、[[Docker Compose 搭建本地开发环境]] 的生产边界区分清楚。

## 相关概念

- [[Docker]]
- [[docker-网络]]
- [[docker-数据卷]]
- [[Docker Compose 搭建本地开发环境]]
