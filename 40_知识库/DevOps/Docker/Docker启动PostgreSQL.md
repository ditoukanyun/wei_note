---
type: wiki
area: "[[DevOps]]"
tags: [Docker, PostgreSQL]
created: 2026-05-08
---
# Docker启动PostgreSQL
Docker启动PostgreSQL 是用容器快速运行 PostgreSQL 实例的操作笔记，适合本地开发和集成测试。

## 相关概念
- [[Docker]]
- [[PostgreSQL 核心能力总览]]

## 启动流程

```mermaid
flowchart LR
  A[选择 PostgreSQL 版本] --> B[设置用户和数据库]
  B --> C[挂载数据卷]
  C --> D[执行初始化脚本]
  D --> E[连接和迁移验证]
```

## 实践检查清单

- 是否固定 PostgreSQL 主版本，避免扩展和 SQL 行为变化。
- 数据卷是否持久化，初始化脚本是否可重复执行。
- 时区、编码和排序规则是否符合项目要求。
- 应用账号是否最小权限，不直接使用超级用户。
- 集成测试是否能自动创建和清理数据库。

## 案例

后端集成测试可以用 Docker 启动临时 PostgreSQL，执行迁移脚本后跑测试，结束后销毁容器。这样比共享测试库更稳定，也能避免数据污染。

## 使用边界

Docker 启动 PostgreSQL 适合本地和 CI，但要尽量贴近真实版本。PostgreSQL 的 JSONB、全文检索、事务隔离、扩展和执行计划都可能受版本影响。若生产使用特定扩展，本地容器也应在初始化阶段安装和验证。

测试环境要关注可重复性。迁移脚本、种子数据、账号权限和清理策略都应自动化，避免不同开发者手工创建出不同数据库状态。

如果测试依赖 PostgreSQL 特性，应优先用真实 PostgreSQL 容器，而不是退回 H2 或 Mock 数据库。

## 常见误区

- 只暴露端口不挂载卷，容器重建后数据消失。
- 本地和生产 PostgreSQL 主版本不同。
- 初始化 SQL 依赖手工执行，团队环境不一致。
