---
title: "研究计划: Redis + Java 操作"
date: 2026-03-16
tags: ["research", "redis", "java", "backend"]
category: "research-plan"
status: active
area: "[[后端开发]]"
---

# 研究计划: Redis + Java 操作

## 研究目标

完成此研究后，您将理解 Redis 核心概念、掌握 Java 操作 Redis 的主流方式，并能够在实际项目中应用 Redis 进行缓存、分布式锁、消息队列等场景开发。

## 发现的上下文

- **相关领域**: [[后端开发]]
- **现有笔记**: 未发现 Redis 相关笔记
- **相关项目**: 无

## 研究策略

- [ ] Docker 启动 Redis
  - [ ] 基础启动命令
  - [ ] 持久化配置
  - [ ] 密码与安全配置
  - [ ] 集群模式启动
- [ ] Redis 核心概念复习
  - [ ] 数据类型（String、Hash、List、Set、Sorted Set）
  - [ ] 持久化机制（RDB、AOF）
  - [ ] 过期策略与淘汰策略
  - [ ] 事务与管道
- [ ] Java Redis 客户端对比
  - [ ] Jedis 特点与使用场景
  - [ ] Lettuce 特点与使用场景
  - [ ] Redisson 特点与使用场景
  - [ ] 三者的性能与功能对比
- [ ] Spring Data Redis 使用
  - [ ] Spring Boot 集成 Redis 配置
  - [ ] RedisTemplate 与 StringRedisTemplate
  - [ ] Repository 模式操作 Redis
  - [ ] 缓存注解（@Cacheable、@CacheEvict 等）
- [ ] 常用操作示例
  - [ ] 基础 CRUD 操作
  - [ ] 缓存设计与实现
  - [ ] 分布式锁实现
  - [ ] 消息队列（Pub/Sub、Stream）
  - [ ] 限流与计数器
- [ ] 最佳实践和性能优化
  - [ ] 连接池配置
  - [ ] 序列化方案选择
  - [ ] 大 Key 问题处理
  - [ ] 缓存穿透、击穿、雪崩解决方案

## 输出结构

- **主笔记**: `30_研究/SoftwareEngineering/Redis-Java/Redis-Java-操作指南.md`
- **原子概念**:
  - `40_知识库/后端开发/Redis-数据类型.md`
  - `40_知识库/后端开发/Redis-持久化机制.md`
  - `40_知识库/后端开发/Redis-Java客户端对比.md`
  - `40_知识库/后端开发/Spring-Data-Redis.md`
  - `40_知识库/后端开发/Redis-分布式锁.md`
  - `40_知识库/后端开发/Redis-缓存策略.md`
- **示例代码**: `30_研究/SoftwareEngineering/Redis-Java/examples/`

## 澄清问题

_如果你有答案，请在下方填写。如果留空，我将按标准假设继续。_

**问:** 你的 Redis 知识水平？（初级/中级/高级）
**答:**

**问:** 使用场景是什么？（缓存/消息队列/分布式锁/全部）
**答:**

**问:** 使用 Spring Boot 还是原生 Java？
**答:**

**问:** 需要覆盖哪些客户端？（Jedis/Lettuce/Redisson/全部）
**答:**

---

## 关联笔记

- [[后端开发 MOC]]
- [[Redis-数据类型]]（待创建）
- [[Redis-Java客户端对比]]（待创建）

## 参考资料（待补充）

- Redis 官方文档
- Spring Data Redis 文档
