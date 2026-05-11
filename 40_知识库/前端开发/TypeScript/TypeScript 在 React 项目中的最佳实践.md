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

## 复盘问题

- 类型是否表达了业务不变量，而不只是让编译器暂时通过。
- API 类型、组件 Props 和页面状态是否有清晰边界。
- 复杂类型是否真的减少错误，还是把简单代码变成难读抽象。

## 掘金文章补充

掘金文章《react typescript 备忘清单》给了 React Props 的常用类型边界：`children` 通常用 `React.ReactNode`，单个 JSX 元素可用 `JSX.Element`，样式可用 `React.CSSProperties`，表单事件可用 `React.FormEventHandler<HTMLInputElement>` 或更具体的事件类型。封装原生按钮、输入框时，可以用 `React.ComponentPropsWithoutRef<"button">` 继承原生属性；需要透传 ref 时再使用 `ComponentPropsWithRef`。

Props 设计时应避免模糊对象类型：`object` 表示任意非原始值，`{}` 允许除 `null/undefined` 外的很多值，都不适合表达具体业务对象。更稳的做法是用明确字段、联合字面量、`Record<string, T>` 或泛型表达输入边界。`Function` 也不推荐作为回调类型，应写出参数和返回值，例如 `(id: number) => void`。

来源：[react typescript 备忘清单](https://juejin.cn/post/7166502182684983327)
