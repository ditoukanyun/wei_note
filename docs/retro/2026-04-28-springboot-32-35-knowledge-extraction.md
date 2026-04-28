---
date: 2026-04-28
task: SpringBoot 32-35 知识点提取收尾
---
# SpringBoot 32-35 知识点提取复盘

## 做对了什么

- 完成了 32-35 章最后四个模块整理，覆盖 Saga、CQRS、Event Sourcing、Feature Flag 灰度发布。
- 继续先读 README 再读关键源码，确保笔记中的流程、代码片段和状态流转来自实际实现。
- 更新学习计划到 35/35，工程治理阶段和总进度都收尾为 100%。

## 做错了什么

- 仍有部分 Read 调用带了 `pages` 参数，后续读取普通文本文件应彻底去掉该参数。
- 本轮以模块笔记为主，没有额外拆出 `Saga`、`CQRS`、`Event Sourcing`、`Feature Flag` 等原子概念独立条目。

## 下次先改哪一步

- 如果继续深化这组笔记，优先补独立原子概念页，并把模块笔记中的 wikilinks 指向这些原子页。
- 普通文本读取时只使用 `file_path`、`limit`、`offset`。
