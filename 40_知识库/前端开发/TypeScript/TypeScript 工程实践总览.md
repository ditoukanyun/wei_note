---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - TypeScript
  - 工程化
created: 2026-04-30
---
# TypeScript 工程实践总览

## 学习目标

- 理解 TypeScript 在前端工程中的价值：类型约束、编辑器提示、重构安全和接口协作。
- 掌握项目级配置：`tsconfig.json`、路径别名、类型声明文件和严格模式。
- 能在 React、Vite、Node 工具脚本中合理使用 TypeScript。

## 核心概念

- **类型系统**：基础类型、联合类型、交叉类型、字面量类型、类型收窄。
- **泛型**：用类型参数表达输入和输出之间的关系。
- **工具类型**：`Partial`、`Pick`、`Omit`、`Record`、`ReturnType`。
- **声明文件**：用 `.d.ts` 补充第三方库或全局变量类型。
- **工程配置**：通过 `strict`、`baseUrl`、`paths`、`types` 控制项目类型检查行为。

## 推荐阅读顺序

1. [[JavaScript]]：先熟悉 JavaScript 运行时语义。
2. [[React 基础]]：理解组件、props、state 后再学习 React 类型写法。
3. 本文：建立 TypeScript 工程全局视角。
4. 后续拆分文章：类型系统、泛型、React 类型实践、tsconfig 配置。

## 工程实践清单

- 新项目优先开启 `strict`，旧项目可以分模块逐步收紧。
- API 响应、表单数据、路由参数和组件 props 应优先定义明确类型。
- 公共类型放在靠近业务的模块中，避免过早建立庞大的全局 types 目录。
- 类型用于表达约束，不要为了炫技写难以维护的类型体操。

## 后续可拆分文章

- [[TypeScript 类型系统基础]]
- [[TypeScript 泛型与条件类型]]
- [[TypeScript tsconfig 配置详解]]
- [[TypeScript 在 React 项目中的最佳实践]]

## 相关链接

- [[前端开发 MOC]]
- [[Vite 原理与插件机制总览]]
- [[Next.js App Router 总览]]
