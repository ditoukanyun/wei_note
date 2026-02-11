---
title: "MobX"
date: 2026-02-11
tags: [前端框架, 状态管理, React, 概念, 响应式编程]
category: 前端开发
status: active
---

# MobX

## 定义

MobX 是一个基于**响应式编程**（Reactive Programming）的状态管理库。与 Redux 的函数式编程理念不同，MobX 采用面向对象的方式，通过自动追踪依赖关系实现状态与视图的同步更新。

**核心理念**: 任何可以从应用状态派生出来的值都应该被自动派生。

## 核心概念

| 概念 | 装饰器/API | 说明 | 类比 |
|-----|-----------|-----|-----|
| **Observable** | `@observable` / `makeObservable` | 声明可观察的状态 | 数据源 |
| **Action** | `@action` | 修改状态的方法 | 状态修改器 |
| **Computed** | `@computed` | 基于状态自动计算的派生值 | 缓存的计算结果 |
| **Observer** | `observer` HOC | 订阅可观察状态的组件 | 监听者 |
| **Reaction** | `autorun` / `reaction` | 对状态变化作出副作用响应 | 副作用执行器 |

## 基础用法

### 1. 创建 Store (装饰器语法)

```typescript
import { makeAutoObservable } from 'mobx'
import { observer } from 'mobx-react-lite'

class CounterStore {
  count = 0

  constructor() {
    makeAutoObservable(this)
  }

  increment() {
    this.count++
  }

  decrement() {
    this.count--
  }

  get doubleCount() {
    return this.count * 2
  }
}

const counterStore = new CounterStore()
```

### 2. 在 React 中使用

```tsx
import { observer } from 'mobx-react-lite'

const Counter = observer(() => {
  return (
    <div>
      <p>Count: {counterStore.count}</p>
      <p>Double: {counterStore.doubleCount}</p>
      <button onClick={() => counterStore.increment()}>+</button>
      <button onClick={() => counterStore.decrement()}>-</button>
    </div>
  )
})
```

### 3. 使用 Hooks 方式 (推荐)

```typescript
import { observable, action, computed, makeObservable } from 'mobx'
import { useLocalObservable } from 'mobx-react-lite'

// 使用 useLocalObservable 创建局部状态
function useCounterStore() {
  return useLocalObservable(() => ({
    count: 0,
    increment() {
      this.count++
    },
    get doubleCount() {
      return this.count * 2
    }
  }))
}
```

## 异步处理

MobX 天然支持异步操作，无需额外的中间件。

```typescript
class UserStore {
  users = []
  loading = false
  error = null

  constructor() {
    makeAutoObservable(this)
  }

  async fetchUsers() {
    this.loading = true
    this.error = null
    try {
      const response = await fetch('/api/users')
      const data = await response.json()
      this.users = data
    } catch (err) {
      this.error = err.message
    } finally {
      this.loading = false
    }
  }
}
```

## 响应式原理

MobX 使用 **Proxy** 对象（或 Object.defineProperty）自动追踪依赖关系：

```typescript
import { autorun } from 'mobx'

const store = new CounterStore()

// 自动追踪 store.count 的依赖
autorun(() => {
  console.log('Count changed:', store.count)
})

// 任何对 count 的修改都会触发上面的 autorun
store.increment() // 输出: Count changed: 1
store.increment() // 输出: Count changed: 2
```

## 与 Redux/Zustand 对比

| 特性 | MobX | Redux (RTK) | Zustand |
|-----|------|-------------|---------|
| **编程范式** | 响应式 / OOP | 函数式 / Flux | 极简 / Hooks |
| **状态更新** | 直接修改（可变） | 不可变更新 | 直接修改（通过 set） |
| **样板代码** | 较少 | 中等 | 极少 |
| **学习曲线** | 中等（理解响应式） | 中等（理解 Flux） | 低 |
| **性能优化** | 自动追踪依赖 | 手动优化（Selector） | 手动选择器 |
| **DevTools** | mobx-devtools | Redux DevTools（强大） | 基础 DevTools |
| **适用场景** | 复杂状态关系、OOP 偏好 | 大型应用、严格规范 | 中小型应用、快速开发 |

### 关键差异详解

**1. 可变 vs 不可变**
```typescript
// MobX - 直接修改（内部通过 Proxy 处理响应式）
store.count++

// Redux - 必须返回新对象
state.count += 1  // RTK 的 Immer 允许这种写法，但底层仍不可变

// Zustand - 通过 set 修改
set(state => ({ count: state.count + 1 }))
```

**2. 自动追踪 vs 手动选择**
```typescript
// MobX - 自动追踪，组件只会在 count 变化时重渲染
observer(() => <div>{store.count}</div>)

// Redux - 需要手动选择需要的字段
const count = useSelector(state => state.counter.count)

// Zustand - 需要手动选择器
const count = useStore(state => state.count)
```

## 适用场景

✅ **选择 MobX 当：**
- 喜欢面向对象编程风格
- 状态间有复杂的派生关系（大量 computed 值）
- 需要自动优化的性能（无需手动写 selector）
- 团队成员更熟悉 OOP 而非函数式

❌ **不选择 MobX 当：**
- 项目需要严格的不变性约束
- 需要 Redux DevTools 那样的时间旅行调试
- 状态逻辑非常简单，不需要响应式系统

## 最佳实践

### 1. 使用 makeAutoObservable

```typescript
constructor() {
  makeAutoObservable(this)
}
```

### 2. 在 Action 中修改状态

虽然 MobX 允许在任何地方修改状态，但建议只在 action 中修改：

```typescript
// ✅ 好
@action
increment() {
  this.count++
}

// ❌ 避免（虽然可以工作，但不利于调试）
store.count++
```

### 3. 使用局部状态

对于组件级别的状态，使用 `useLocalObservable`：

```tsx
const MyComponent = observer(() => {
  const store = useLocalObservable(() => ({
    count: 0,
    increment() { this.count++ }
  }))
  
  return <button onClick={store.increment}>{store.count}</button>
})
```

## 相关概念

- [[响应式原理]] - MobX 底层的依赖追踪机制
- [[Redux]] - 函数式状态管理对比
- [[Zustand]] - 极简状态管理对比
- [[Observer 模式]] - 设计模式基础

## 参考

- 官方文档：https://mobx.js.org/
- GitHub：https://github.com/mobxjs/mobx
