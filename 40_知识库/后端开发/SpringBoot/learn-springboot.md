---
type: project-reference
area: "[[后端开发]]"
tags:
  - SpringBoot
  - 项目实践
created: 2026-05-08
---
# learn-springboot

learn-springboot 是 SpringBoot 学习与示例项目集合，用于沉淀接口、认证、缓存、消息、网关、可观测性和分布式模式练习。

## 相关概念

- [[SpringBoot/SpringBoot 学习计划]]
- [[SpringBoot]]

## 学习流程

```mermaid
flowchart LR
  A[基础接口] --> B[认证授权]
  B --> C[数据访问和事务]
  C --> D[缓存和消息]
  D --> E[网关、监控和部署]
```

## 实践检查清单

- 每个示例是否有 README、接口说明和启动方式。
- 是否覆盖成功、失败和边界请求。
- 是否把示例和真实工程最佳实践区分开。
- 是否记录关键设计取舍，例如为什么用 Redis 或消息队列。
- 学完一个模块后是否沉淀为原子知识笔记。

## 案例

Header Token 登录模块适合学习拦截器和服务端 Token 存储，但生产环境需要补 Redis、过期时间、刷新策略和审计日志。

## 常见误区

- 只把示例跑通，不总结适用场景和限制。
- 示例代码逐渐堆成大杂烩，没有模块边界。
- 忽略测试和异常路径，只演示 happy path。
