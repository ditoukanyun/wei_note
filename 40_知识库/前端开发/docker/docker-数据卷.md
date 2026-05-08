---
type: wiki
area: "[[前端开发]]"
tags:
  - Docker
  - 存储
created: 2026-05-08
---
# docker-数据卷

Docker 数据卷用于把容器中的数据持久化到容器生命周期之外，常用于数据库、缓存和上传文件目录。

## 要点

- Volume 由 Docker 管理，适合持久化数据。
- Bind mount 直接挂载宿主机路径，适合开发调试。
- 删除容器不等于删除数据卷。

## 相关概念

- [[docker-compose]]
- [[docker-容器]]
- [[Docker]]
