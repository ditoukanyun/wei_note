---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - React
  - 测试
created: 2026-05-08
---
# React Testing Library 组件测试

## 定义

React Testing Library 是从用户视角测试 React 组件渲染和交互的测试工具，强调查询用户能感知的文本、角色和标签。

## 要点

- 优先使用 `getByRole`、`getByLabelText`、`getByText`。
- 避免测试内部 state 和实现细节。
- 交互测试配合 user-event 更接近真实用户操作。

## 相关概念

- [[前端测试体系总览]]
- [[Web 可访问性 A11y]]
