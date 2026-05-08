---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - JavaScript
  - Promise
created: 2026-05-08
---
# PromiseState

## 定义

`PromiseState` 是理解 Promise 内部状态机时常用的概念，表示一个 Promise 当前处于 `pending`、`fulfilled` 或 `rejected` 中的哪一种状态。真实 JavaScript 引擎不会把它作为可直接访问的公开属性暴露给业务代码。

## 要点

- `pending`：异步操作尚未完成，结果未确定。
- `fulfilled`：异步操作成功完成，拥有成功值。
- `rejected`：异步操作失败，拥有拒绝原因。
- Promise 状态一旦从 `pending` 变为 `fulfilled` 或 `rejected`，就不可逆。

## 示例

手写 Promise 时通常会用 `state` 字段模拟 `PromiseState`，再根据状态决定回调进入成功队列还是失败队列。

## 相关概念

- [[PromiseResult]]
- [[异步编程]]
- [[JavaScript]]
