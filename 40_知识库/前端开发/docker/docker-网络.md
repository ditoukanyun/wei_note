---
type: wiki
area: "[[前端开发]]"
tags:
  - Docker
  - 网络
created: 2026-05-08
---
# docker-网络

Docker 网络用于连接容器、宿主机和外部服务。常见模式包括 bridge、host、none 和自定义网络。

## 要点

- Compose 中同一网络内服务可用服务名互相访问。
- 端口映射负责把容器端口暴露到宿主机。
- 生产环境需要明确只暴露必要端口。

## 相关概念

- [[docker-compose]]
- [[docker-容器]]
- [[Docker]]
