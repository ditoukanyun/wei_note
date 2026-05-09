---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - TypeScript
  - React
created: 2026-05-08
---
# TypeScript 在 React 项目中的最佳实践

## 定义

TypeScript 在 React 项目中的最佳实践是用类型清晰表达组件 Props、事件、状态、接口响应和业务模型边界，同时避免过度类型体操。

## 要点

- Props 类型应表达组件必要输入和可选输入。
- API 响应类型优先来自 [[OpenAPI 与类型生成]]。
- 事件类型按具体元素收窄。
- 复杂业务状态可用联合类型表达状态机。

## 相关概念

- [[React 基础]]
- [[TypeScript 类型系统基础]]
- [[组件设计与状态边界]]

## 设计流程

```mermaid
flowchart LR
  A[定义业务模型] --> B[生成或声明 API 类型]
  B --> C[设计组件 Props]
  C --> D[收窄事件和状态]
  D --> E[用测试和构建校验]
```

## 实践检查清单

- API 类型是否从契约生成，避免前端手写漂移。
- Props 是否区分必填、可选和受控/非受控模式。
- 事件类型是否根据元素精确收窄。
- 异步状态是否用联合类型表达 loading、success、error。
- 是否避免滥用 `any`，必要时用 `unknown` 先收窄。

## 案例

用户详情组件可以把 `User` 作为业务模型，Props 只暴露 `user`、`onSave` 和 `readonly`。保存接口返回类型来自 OpenAPI，组件内部不手写接口响应结构。

## 常见误区

- 为了省事到处使用 `any`，类型系统失去意义。
- 组件 Props 直接复用后端 DTO，导致 UI 边界和接口边界耦合。
- 复杂泛型过度抽象，让组件调用方难以理解。
