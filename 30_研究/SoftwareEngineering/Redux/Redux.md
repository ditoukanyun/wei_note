---
title: "Redux"
created: 2026-02-11
area: "[[前端开发]]"
tags: [状态管理, Redux, React, 架构]
status: complete
type: reference
---

# Redux 深度解析

## 概述

Redux 是一个用于 JavaScript 应用的可预测状态容器。它通过强制执行单一数据源、不可变更新和纯函数修改，让状态管理变得可预测、易于测试和调试。尽管在 React 生态中应用最广，但它可以与任何 UI 库（Angular, Vue, Vanilla JS）配合使用。

### 为什么选择 Redux？

在复杂的前端应用中，状态分散在各个组件中会导致难以追踪的数据流问题（Prop Drilling）。Redux 提供了一个**单一的事实来源（Single Source of Truth）**，使得应用的行为更加一致。

## 演进历史：从 Classic Redux 到 Redux Toolkit (RTK)

### Classic Redux (旧时代)

早期的 Redux 虽然强大，但存在显著痛点：
1. **配置繁琐**：需要手动配置 store、middleware、devtools。
2. **样板代码多**：创建 action types、action creators、switch-case reducers。
3. **不可变更新困难**：必须小心翼翼地使用扩展运算符 `...` 来更新嵌套状态，极易出错。

```javascript
// 旧式 Redux 写法示例 (繁琐且易错)
const ADD_TODO = 'ADD_TODO';
const addTodo = text => ({ type: ADD_TODO, text });

const initialState = { todos: [] };
function todoReducer(state = initialState, action) {
  switch (action.type) {
    case ADD_TODO:
      return {
        ...state,
        todos: [...state.todos, { text: action.text, completed: false }]
      };
    default:
      return state;
  }
}
```

### Modern Redux (Redux Toolkit)

Redux Toolkit (RTK) 是官方推荐的标准开发方式，旨在解决上述问题：
1. **内置 Immer**：允许编写"可变"的更新逻辑，自动转换为不可变更新。
2. **自动生成 Action**：`createSlice` 自动生成 action creators 和 action types。
3. **预配置 Store**：`configureStore` 默认集成了 Thunk、DevTools 和不可变性检查中间件。

```typescript
// 现代 Redux Toolkit 写法 (简洁且安全)
const todoSlice = createSlice({
  name: 'todos',
  initialState: [],
  reducers: {
    addTodo(state, action) {
      // 直接 push，Immer 会处理不可变更新
      state.push({ text: action.payload, completed: false })
    }
  }
})
export const { addTodo } = todoSlice.actions
```

## 核心架构原理

Redux 的三大原则是其设计的基石：

1. **单一数据源 (Single Source of Truth)**
   整个应用的状态被存储在一个对象树中，并且这个对象树只存在于唯一的 Store 中。
   *优势*：便于调试、快照持久化、服务端渲染。

2. **状态只读 (State is Read-Only)**
   唯一改变状态的方法是触发一个 **Action**（一个描述已发生事件的对象）。
   *优势*：视图和网络回调不能直接修改状态，确保了修改的集中化和顺序化。

3. **使用纯函数执行修改 (Changes are made with Pure Functions)**
   为了描述 action 如何改变状态树，你需要编写 **Reducers**。
   *优势*：纯函数易于测试，结果确定，无副作用。

## 深入对比：Redux vs Zustand

虽然两者都用于状态管理，但设计哲学截然不同。

| 特性 | Redux (RTK) | Zustand |
|-----|-------------|---------|
| **架构模式** | **Flux** (单向数据流) | **Hook-based** (去中心化) |
| **Store 结构** | 单一巨大的 Store 对象 | 可以创建多个独立的 Store |
| **状态更新** | 必须通过 Dispatch Action -> Reducer | 直接调用 Store 中的 set 函数 |
| **心智负担** | 较高（需理解 Action, Reducer, Slice） | 极低（类似 useState 的加强版） |
| **代码量** | 中等（RTK 简化了很多） | 极少 |
| **DevTools** | **非常强大**（时间旅行、Action 重放） | 基础功能（状态查看） |
| **中间件** | 强大的中间件生态（Saga, Observable） | 简单的中间件支持 |
| **适用规模** | 大型、超大型、团队协作项目 | 中小型、快速迭代项目 |

### 何时选择 Redux？
- **复杂的状态逻辑**：状态更新依赖于之前的状态，或者多个 Slice 之间有复杂的联动。
- **频繁的状态快照**：需要记录用户操作历史，实现撤销/重做功能。
- **严格的代码规范**：团队成员较多，需要强制统一的代码风格和数据流向。
- **服务端渲染 (SSR)**：Redux 在 SSR 方面有成熟的解决方案。

### 何时选择 Zustand？
- **快速开发**：不想写额外的 boilerplate。
- **简单应用**：状态逻辑并不复杂，只是需要跨组件共享。
- **性能敏感**：Zustand 的选择器模式默认避免了不必要的重渲染。

## 最佳实践 (Redux Style Guide)

1. **总是使用 Redux Toolkit**：不要再手写原始 Redux 代码。
2. **将 Redux 状态设计为标准化 (Normalized)**：避免深层嵌套，像数据库一样存储数据（ID 为键的对象）。
3. **不要在 Redux 中存储所有状态**：表单状态、UI 临时状态（如模态框开关）应优先使用组件局部状态（useState）。
4. **Action 描述"发生了什么"，而非"怎么做"**：
   - ✅ `dispatch(userLoggedIn(user))`
   - ❌ `dispatch(setUser(user))`
5. **Reducer 必须是纯函数**：禁止在 Reducer 中进行 API 请求、路由跳转或生成随机数。

## 性能优化

1. **使用 Selector 选择最小必要数据**：
   ```typescript
   // ❌ 导致不必要的重渲染
   const { items } = useSelector(state => state.todos);
   
   // ✅ 仅在 todos.items 变化时重渲染
   const items = useSelector(state => state.todos.items);
   ```
2. **使用 Reselect 进行记忆化 (Memoization)**：
   对于复杂的派生数据计算，使用 `createSelector` 缓存计算结果，避免重复计算。
   
   ```typescript
   import { createSelector } from '@reduxjs/toolkit'
   
   const selectItems = state => state.items
   const selectFilter = state => state.filter
   
   const selectFilteredItems = createSelector(
     [selectItems, selectFilter],
     (items, filter) => items.filter(item => item.type === filter)
   )
   ```

## 常见陷阱

1. **在 Reducer 中修改 State**：虽然 RTK 允许写可变逻辑，但底层必须是不可变的。如果你不使用 RTK，直接修改 `state.value = 1` 是致命错误。
2. **过度使用 Redux**：把所有东西都塞进 Redux，导致代码臃肿。
3. **忽视 Redux DevTools**：这是 Redux 最强大的武器，不使用它就浪费了 Redux 一半的价值。

## 相关阅读

- [[40_知识库/前端开发/React/状态管理/Redux|Redux 概念笔记]] - 快速查阅
- [[40_知识库/前端开发/React/状态管理/Zustand|Zustand 笔记]] - 轻量级替代
- [[Flux]] - Redux 的架构源头
- [[不可变性]] - Redux 的核心原则

## 参考资源

- [Redux Toolkit 官方文档](https://redux-toolkit.js.org/)
- [Redux Style Guide](https://redux.js.org/style-guide/style-guide)
