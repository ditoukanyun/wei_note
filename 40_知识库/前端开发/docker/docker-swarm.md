---
type: wiki
area: "[[前端开发]]"
tags:
  - Docker
  - Swarm
created: 2026-05-08
---
# docker-swarm

Docker Swarm 是 Docker 原生集群编排能力，用于在多台机器上运行服务、副本和滚动更新。

## 要点

- 适合轻量集群编排场景。
- Kubernetes 生态更主流，能力和社区更完整。
- 学习 Swarm 有助于理解服务、副本和滚动发布概念。

## 相关概念

- [[Docker]]
- [[云原生部署总览：Docker、Kubernetes 与 CI-CD]]

## 核心对象

- Node：加入集群的机器，分为 manager 和 worker。
- Service：期望运行的服务定义，包括镜像、副本数、端口和更新策略。
- Task：Service 在某个节点上实际运行的容器任务。
- Overlay Network：跨主机容器通信网络。
- Secret 和 Config：向服务注入敏感信息和配置。

## 发布流程

```mermaid
flowchart LR
  A[初始化 Swarm] --> B[加入节点]
  B --> C[创建网络和配置]
  C --> D[部署 Service]
  D --> E[滚动更新]
  E --> F[观察副本和日志]
```

## 实践检查清单

- manager 节点是否有奇数个并具备备份策略。
- 服务是否配置健康检查、重启策略和资源限制。
- 数据库、缓存等有状态组件是否明确卷和备份方案。
- 滚动更新是否配置并发数、间隔和失败回滚。
- 是否为跨节点通信开放必要端口并限制暴露面。

## 常见误区

- 把单机 Compose 文件直接当生产编排文件使用。
- 忽视有状态服务的数据迁移和故障恢复。
- 没有监控副本分布，多个关键副本可能落在同一台机器。
