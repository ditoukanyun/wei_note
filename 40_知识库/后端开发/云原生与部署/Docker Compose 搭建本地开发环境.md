---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - Docker
  - 本地开发
created: 2026-05-08
---
# Docker Compose 搭建本地开发环境

## 定义

Docker Compose 搭建本地开发环境是用一个 Compose 文件启动应用依赖的数据库、缓存、消息队列和搜索服务，让团队本地环境更一致。

## 要点

- 服务名可以作为容器间访问主机名。
- 数据卷保存数据库和缓存数据。
- `.env` 管理本地配置，但密钥不要提交仓库。
- 初始化脚本可以固化表结构和测试数据。

## 相关概念

- [[Docker]]
- [[docker-compose]]
- [[云原生部署总览：Docker、Kubernetes 与 CI-CD]]
