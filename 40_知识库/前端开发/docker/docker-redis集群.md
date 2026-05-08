---
type: wiki
area: "[[前端开发]]"
tags:
  - Docker
  - Redis
created: 2026-05-08
---
# docker-redis集群

docker-redis集群是用 Docker 或 Compose 启动多个 Redis 节点，模拟主从、哨兵或 Cluster 的本地实验环境。

## 要点

- 本地学习可用容器快速搭建多节点。
- 生产 Redis 集群要关注持久化、网络、内存和故障转移。
- 客户端需要支持对应的集群或哨兵模式。

## 相关概念

- [[Redis]]
- [[Docker]]
- [[docker-compose]]
