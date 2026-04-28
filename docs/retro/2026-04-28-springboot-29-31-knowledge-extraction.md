---
date: 2026-04-28
task: SpringBoot 29-31 知识点提取
---
# SpringBoot 29-31 知识点提取复盘

## 做对了什么

- 按上轮约定从 29 章继续推进，保持每轮整理 3 章的稳定节奏。
- 读取 README 后补充关键服务类源码，重点提取了 Resilience4j 装饰链、BFF section 级降级、Transactional Outbox 状态流转。
- 同步更新学习计划中的链接与统计，让后续可以直接从 32 章继续。

## 做错了什么

- 仍然在 Read 调用中传入了 `pages` 参数，虽然没有阻塞结果，但与普通文本读取习惯不一致。
- 本轮没有创建独立原子概念笔记，只在模块笔记中使用 wikilinks 连接概念，后续如果需要可再拆分 `Transactional Outbox`、`BFF`、`熔断器` 等原子条目。

## 下次先改哪一步

- 下一轮从 32-SpringBoot-saga-compensation 开始，整理 32-35 章并收尾学习计划。
- 普通文本 Read 调用只保留 `file_path`、`limit`、`offset`。
