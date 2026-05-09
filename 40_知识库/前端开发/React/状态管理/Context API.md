---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - React
  - 状态管理
created: 2026-05-08
---
# Context API

## 定义

Context API 是 React 内置的跨组件层级传值机制，适合主题、语言、当前用户、权限等低频变化的全局上下文。

## 要点

- Context 解决的是跨层级传递，不等同于完整状态管理框架。
- Provider 的 value 变化会影响消费者组件渲染，需要控制引用稳定性。
- 高频、复杂、可派生的状态通常更适合专门状态库或局部状态。

## 相关概念

- [[React 基础]]
- [[组件设计与状态边界]]
- [[状态管理 MOC]]

## 使用流程

```mermaid
flowchart LR
  A[创建 Context] --> B[在上层提供 Provider]
  B --> C[子组件 useContext 读取]
  C --> D[控制 value 稳定性]
```

## 实践检查清单

- Context 是否承载低频变化的全局上下文。
- Provider value 是否使用稳定引用，避免无关重渲染。
- 是否把不同变化频率的数据拆成多个 Context。
- 是否避免把复杂业务状态全部塞进单个 Context。
- 测试组件时是否提供必要的 Provider 包装。

## 案例

主题、语言和当前登录用户适合放入 Context；实时输入框状态和大列表筛选条件更适合局部状态或专门状态库。

## 设计边界

Context 解决的是传值路径问题，不是性能优化工具。Provider 的 value 一变化，所有消费该 Context 的组件都可能重新渲染，因此高频变化状态要谨慎放入。可以按变化频率拆分多个 Context，也可以把复杂状态放在外部 store 中。

使用 Context 前应先判断是否真的跨越多层组件。如果只是父子或相邻组件共享状态，组合组件、props 或状态提升通常更简单。Context 过多会让组件依赖变隐式，测试也需要额外 Provider 包装。

## 常见误区

- 把 Context 当全局状态库使用，导致重渲染范围过大。
- Provider 每次渲染都创建新对象，消费者全部更新。
- Context 嵌套过深，组件测试和复用困难。
