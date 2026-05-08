---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - TypeScript
created: 2026-05-08
---
# TypeScript 泛型与条件类型

## 定义

泛型让类型定义保留参数化能力，条件类型根据类型关系选择不同结果，二者是 TypeScript 类型复用和类型推导的重要基础。

## 要点

- 泛型适合表达输入输出之间的类型关系。
- 条件类型常写作 `T extends U ? X : Y`。
- 配合 `infer` 可以从复杂类型中提取局部类型。
- 复杂类型应控制可读性，避免变成维护负担。

## 相关概念

- [[TypeScript 类型系统基础]]
- [[TypeScript 工程实践总览]]
