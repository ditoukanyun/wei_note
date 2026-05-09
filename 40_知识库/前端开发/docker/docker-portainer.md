---
type: wiki
area: "[[前端开发]]"
tags:
  - Docker
  - Portainer
created: 2026-05-08
---
# docker-portainer

Portainer 是 Docker 可视化管理工具，可通过 Web UI 管理容器、镜像、网络、数据卷和 Compose Stack。

## 要点

- 适合学习和小规模环境管理。
- 生产使用必须配置认证和访问控制。
- 不应替代基础命令和部署流程理解。

## 相关概念

- [[Docker]]
- [[docker-容器]]

## 使用流程

```mermaid
flowchart LR
  A[启动 Portainer] --> B[连接 Docker 环境]
  B --> C[查看容器和镜像]
  C --> D[管理 Stack 或卷]
  D --> E[配置用户和权限]
```

## 实践检查清单

- 是否为 Portainer 配置强密码、HTTPS 和访问控制。
- 是否限制可管理的 Docker 环境范围。
- 对生产环境操作是否仍走变更流程，而不是直接点 UI。
- 是否备份 Portainer 配置和 Stack 定义。
- 使用 UI 后是否同步更新 Compose 或基础设施代码。

## 案例

小团队内网环境可以用 Portainer 查看容器状态和日志，但正式服务的部署仍应通过 CI/CD 和 Compose 文件完成，避免 UI 手工操作造成配置漂移。

## 使用边界

Portainer 适合降低观察和管理 Docker 环境的门槛，但它不应该成为绕过基础设施代码的入口。生产环境中，容器、网络、卷、Stack 和权限变更应经过代码评审或发布流程；UI 操作只适合排查、查看和受控变更。

安全上要把 Portainer 当作高权限管理面。它能操作 Docker 宿主环境，一旦暴露或账号泄露，影响可能比单个应用更大。因此需要 HTTPS、强认证、最小权限、访问来源限制和操作审计。

## 常见误区

- 把 Portainer 暴露到公网且没有强认证。
- 通过 UI 临时修改容器，忘记同步到代码。
- 依赖可视化工具后不再理解 Docker 基础命令。
