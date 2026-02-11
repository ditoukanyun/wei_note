---
title: "Valtio"
date: 2026-02-11
tags: [前端框架, 状态管理, React, 概念, Proxy]
category: 前端开发
status: active
---

# Valtio

## 定义

Valtio 是一个基于 **Proxy** 的 React 状态管理库。与其他强调不可变性的状态管理库不同，Valtio 允许直接修改状态对象，通过 Proxy 自动追踪变化并触发重渲染。

**核心理念**: Mutable state for React.

## 核心概念

| 概念 | API | 说明 |
|-----|-----|------|
| **Proxy State** | `proxy(initialState)` | 创建可观察的状态对象 |
| **useSnapshot** | `useSnapshot(proxyState)` | 在 React 中订阅状态 |
| **subscribe** | `subscribe(proxyState, callback)` | 监听状态变化 |
| **snapshot** | `snapshot(proxyState)` | 获取状态的不可变副本 |

## 基础用法

### 1. 创建 Proxy State

```typescript
import { proxy } from 'valtio'

const state = proxy({
  count: 0,
  user: {
    name: 'John',
    email: 'john@example.com'
  },
  todos: []
})
```

### 2. 直接修改状态

```typescript
// ✅ 直接修改 - Valtio 会自动追踪
state.count++
state.user.name = 'Jane'
state.todos.push({ id: 1, text: 'New Todo' })

// ✅ 在异步函数中修改
async function fetchUser() {
  const response = await fetch('/api/user')
  state.user = await response.json()
}
```

### 3. 在 React 中使用

```tsx
import { useSnapshot } from 'valtio/react'

function Counter() {
  const snap = useSnapshot(state)
  
  return (
    <div>
      <p>Count: {snap.count}</p>
      <button onClick={() => state.count++}>+</button>
    </div>
  )
}

// 组件只会在 count 变化时重渲染
function UserName() {
  const snap = useSnapshot(state)
  return <p>{snap.user.name}</p>
}
```

## 派生状态

```typescript
import { derive } from 'valtio/utils'

const state = proxy({
  firstName: 'John',
  lastName: 'Doe',
  age: 30
})

// 创建派生状态
const derivedState = derive({
  fullName: (get) => `${get(state).firstName} ${get(state).lastName}`,
  isAdult: (get) => get(state).age >= 18
})

// 在组件中使用
function UserInfo() {
  const snap = useSnapshot(derivedState)
  return <div>{snap.fullName} - {snap.isAdult ? 'Adult' : 'Minor'}</div>
}
```

## 订阅和监听

```typescript
import { subscribe } from 'valtio'

// 监听整个状态
subscribe(state, () => {
  console.log('State changed:', state)
})

// 监听特定路径
subscribe(state.user, () => {
  console.log('User changed:', state.user)
})

// 获取不可变快照（用于比较或序列化）
import { snapshot } from 'valtio'
const snap = snapshot(state)
```

## 与 Zustand/Redux 对比

| 特性 | Valtio | Zustand | Redux (RTK) |
|-----|--------|---------|-------------|
| **更新方式** | 直接修改（可变） | 通过 set 函数 | 不可变更新 |
| **API 复杂度** | 极简 | 极简 | 中等 |
| **学习曲线** | 极低 | 低 | 中等 |
| **不可变性** | 不强制 | 推荐 | 强制 |
| **DevTools** | 基础 | 基础 | 强大 |
| **TypeScript** | 良好 | 优秀 | 优秀 |
| **适用场景** | 快速原型、可变状态 | 通用 | 大型应用 |

### 代码风格对比

```typescript
// Valtio - 直接修改
state.count++
state.nested.obj.value = 'new'

// Zustand - 通过 set
set(state => ({ 
  count: state.count + 1,
  nested: { ...state.nested, obj: { ...state.nested.obj, value: 'new' } }
}))

// Redux - 不可变
state.count += 1  // RTK 用 Immer 允许这种写法，但底层仍不可变
```

## 适用场景

✅ **选择 Valtio 当：**
- 喜欢直接修改状态的开发体验（类似 Vue）
- 嵌套对象需要频繁更新
- 快速原型开发
- 从 Vue 迁移到 React 的团队

❌ **选择 Zustand/Redux 当：**
- 需要严格的不变性约束
- 团队协作需要明确的更新规范
- 需要强大的调试工具

## 最佳实践

### 1. 状态组织

```typescript
// ✅ 模块化组织
export const userState = proxy({
  profile: null,
  preferences: {}
})

export const cartState = proxy({
  items: [],
  total: 0
})

// 在组件中按需订阅
const UserProfile = () => {
  const user = useSnapshot(userState)
  return <div>{user.profile?.name}</div>
}
```

### 2. Action 封装

虽然可以直接修改状态，但建议封装 action：

```typescript
// actions.ts
export const userActions = {
  setName: (name: string) => {
    userState.profile.name = name
  },
  
  async fetchProfile(id: string) {
    const response = await fetch(`/api/users/${id}`)
    userState.profile = await response.json()
  }
}
```

### 3. 避免在渲染中修改状态

```tsx
// ❌ 错误 - 渲染中修改状态
function BadComponent() {
  const snap = useSnapshot(state)
  state.count++  // 会导致无限重渲染
  return <div>{snap.count}</div>
}

// ✅ 正确 - 在事件中修改
function GoodComponent() {
  const snap = useSnapshot(state)
  return <button onClick={() => state.count++}>{snap.count}</button>
}
```

## 高级特性

### 持久化

```typescript
import { proxyWithStorage } from 'valtio/utils'

// 自动同步到 localStorage
const state = proxyWithStorage('my-app-state', {
  theme: 'light',
  language: 'zh-CN'
})
```

### 计算属性缓存

```typescript
import { derive } from 'valtio/utils'

// derive 会自动缓存计算结果
const expensiveState = derive({
  expensiveValue: (get) => {
    const state = get(baseState)
    // 这个计算只会在 baseState 变化时执行
    return expensiveComputation(state)
  }
})
```

## 相关概念

- [[Zustand]] - 同作者开发的不可变状态管理
- [[MobX]] - 另一个响应式状态管理
- [[Proxy]] - JavaScript Proxy API
- [[不可变性]] - 传统 React 状态管理原则

## 参考

- [Valtio 官方文档](https://valtio.pmnd.rs/)
- [GitHub](https://github.com/pmndrs/valtio)
- [Proxy API MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy)
