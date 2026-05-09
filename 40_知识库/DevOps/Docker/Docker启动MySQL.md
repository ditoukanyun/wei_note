---
type: wiki
area: "[[DevOps]]"
tags: [Docker, MySQL]
created: 2026-05-08
---
# Docker启动MySQL
Docker启动MySQL 是用容器快速运行 MySQL 实例的操作笔记，适合本地开发和实验环境。

## 相关概念
- [[Docker]]
- [[MySQL/MySQL_高级操作总览]]

## 启动流程

```mermaid
flowchart LR
  A[选择 MySQL 镜像版本] --> B[设置 root 密码和数据库]
  B --> C[挂载数据卷]
  C --> D[映射端口]
  D --> E[连接验证]
```

## 实践检查清单

- 是否固定 MySQL 版本，而不是长期使用 `latest`。
- 数据目录是否挂载到命名卷或本地目录。
- 字符集、时区和排序规则是否与项目一致。
- root 密码是否只用于本地实验，应用使用独立账号。
- 是否准备初始化 SQL，保证环境可重复创建。

## 案例

本地开发可以用 Compose 启动 MySQL 8，挂载数据卷并执行初始化脚本。团队成员拉取项目后能得到相同数据库结构，而不是手工点 UI 创建表。

## 常见误区

- 删除容器后才发现数据没有挂载卷。
- 本地和测试环境 MySQL 版本不同，SQL 行为不一致。
- 应用直接使用 root 账号连接数据库。
