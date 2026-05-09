---
type: wiki
area: "[[前端开发]]"
tags:
  - React
  - 状态管理
created: 2026-05-08
---
# Flux

Flux 是 Facebook 提出的前端单向数据流架构思想，强调 Action、Dispatcher、Store 和 View 之间的明确数据流。

## 相关概念

- [[Redux]]
- [[状态管理 MOC]]
- [[不可变性]]

## 数据流

```mermaid
flowchart LR
  A[View 触发 Action] --> B[Dispatcher 分发]
  B --> C[Store 更新状态]
  C --> D[View 重新渲染]
```

## 实践检查清单

- Action 是否表达用户或系统事件，而不是直接描述 UI 修改细节。
- Store 是否集中管理共享状态，并保持可预测更新。
- 数据流是否单向，避免 View 直接修改 Store。
- 状态更新是否保持不可变，便于调试和回放。
- 是否确认项目复杂度真的需要 Flux 架构。

## 案例

待办应用中，用户点击“完成”产生 `todo_completed` Action，Dispatcher 把事件分发给 Store，Store 更新状态后通知 View 渲染完成状态。

## 常见误区

- 小型局部状态也引入全局 Flux，增加样板代码。
- Action 命名混乱，难以追踪业务事件。
- Store 中混入大量副作用，破坏可预测性。
