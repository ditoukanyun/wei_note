---
date: 2026-04-28
task: SpringBoot 知识点提取
---
# SpringBoot 知识点提取复盘

## 做对了什么

- 先定位到真实源码目录 `/Users/chenwei/Documents/code/java/learn-springboot`，并确认现有笔记只整理到 22 章。
- 按已有笔记风格继续整理 23-25 章，保留源码路径、项目结构、核心代码、API 与要点总结。
- 同步更新学习计划，把后续 26-35 章纳入工程治理阶段，避免计划显示已 100% 完成但源码还有未整理模块。

## 做错了什么

- 读取 Markdown 文件时误传了空的 `pages` 参数，导致前几次 Read 调用失败。
- 一开始没有直接限定读取 Markdown 不需要 `pages`，造成了不必要的工具调用重试。

## 下次先改哪一步

- 使用 Read 读取普通 Markdown 文件时不要传 `pages` 参数；只有读取 PDF 时才指定页码范围。
