---
title: "Recoil"
date: 2026-02-11
tags: [前端框架, 状态管理, React, 概念, 原子化]
category: 前端开发
status: active
---

# Recoil

## 定义

Recoil 是 Facebook (Meta) 开发的 React 状态管理库，采用**原子化状态管理**理念。它是 React 官方推荐的实验性状态管理方案，与 React 的并发特性（Concurrent Features）深度集成。

> ⚠️ **注意**: Recoil 目前仍处于 **experimental**（实验性）状态，不建议在生产环境的关键业务中使用。

## 核心概念

| 概念 | API | 说明 |
|-----|-----|------|
| **Atom** | `atom({ key, default })` | 状态的最小单位，需要唯一的 key |
| **Selector** | `selector({ key, get })` | 派生状态，可以同步或异步 |
| **useRecoilState** | `useRecoilState(atom)` | 读写原子状态 |
| **useRecoilValue** | `useRecoilValue(atom/selector)` | 只读状态 |
| **useSetRecoilState** | `useSetRecoilState(atom)` | 只写状态 |

## 基础用法

### 1. 配置 Provider

```tsx
import { RecoilRoot } from 'recoil'

function App() {
  return (
    <RecoilRoot>
      <MyApp />
    </RecoilRoot>
  )
}
```

### 2. 创建 Atom

```typescript
import { atom } from 'recoil'

const countState = atom({
  key: 'countState',  // 唯一标识符
  default: 0          // 默认值
})

const userState = atom({
  key: 'userState',
  default: null
})
```

### 3. 创建 Selector（派生状态）

```typescript
import { selector } from 'recoil'

// 同步 Selector
const doubleCountState = selector({
  key: 'doubleCountState',
  get: ({ get }) => {
    const count = get(countState)
    return count * 2
  }
})

// 异步 Selector
const userDataState = selector({
  key: 'userDataState',
  get: async ({ get }) => {
    const userId = get(userIdState)
    const response = await fetch(`/api/users/${userId}`)
    return response.json()
  }
})
```

### 4. 在组件中使用

```tsx
import { useRecoilState, useRecoilValue, useSetRecoilState } from 'recoil'

function Counter() {
  const [count, setCount] = useRecoilState(countState)
  const doubleCount = useRecoilValue(doubleCountState)
  
  return (
    <div>
      <p>Count: {count}</p>
      <p>Double: {doubleCount}</p>
      <button onClick={() => setCount(c => c + 1)}>+</button>
    </div>
  )
}

// 只写组件（性能优化）
function IncrementButton() {
  const setCount = useSetRecoilState(countState)
  return <button onClick={() => setCount(c => c + 1)}>+</button>
}
```

## 高级特性

### Atom Family（动态 Atom）

```typescript
import { atomFamily } from 'recoil'

// 创建参数化的 Atom
const todoAtomFamily = atomFamily({
  key: 'todoAtomFamily',
  default: (id) => ({
    id,
    text: '',
    completed: false
  })
})

// 使用
function TodoItem({ id }) {
  const [todo, setTodo] = useRecoilState(todoAtomFamily(id))
  return <div>{todo.text}</div>
}
```

### Selector Family

```typescript
import { selectorFamily } from 'recoil'

const userDataSelectorFamily = selectorFamily({
  key: 'userDataSelectorFamily',
  get: (userId) => async () => {
    const response = await fetch(`/api/users/${userId}`)
    return response.json()
  }
})
```

### 读写 Selector

```typescript
const editableCountState = selector({
  key: 'editableCountState',
  get: ({ get }) => get(countState),
  set: ({ set }, newValue) => {
    set(countState, newValue)
    // 可以同时更新其他 atom
    set(lastUpdatedState, Date.now())
  }
})
```

## 与 Jotai 对比

| 特性 | Recoil | Jotai |
|-----|--------|-------|
| **出品方** | Facebook (Meta) | Poimandres (社区) |
| **稳定性** | 实验性 | 稳定 |
| **Provider** | 必需 | 可选 |
| **Atom Key** | 必需（全局唯一） | 不需要 |
| **TypeScript** | 良好 | 优秀 |
| **包体积** | ~18KB | ~1KB |
| **并发特性** | 深度集成 | 支持 |
| **生态成熟度** | 较小 | 丰富 |

### 代码风格对比

```typescript
// Recoil - 需要 key 和 Provider
const countState = atom({ key: 'count', default: 0 })

// Jotai - 更简洁
const countAtom = atom(0)
```

## 适用场景

✅ **考虑 Recoil 当：**
- 在 Facebook 生态内开发
- 需要与 React 并发特性深度集成
- 状态结构适合原子化管理
- 能够接受实验性 API 的风险

❌ **选择 Jotai 当：**
- 需要稳定可靠的方案
- 追求极简 API
- 不想管理 Atom Key
- 需要更小的包体积

## 实验性风险

使用 Recoil 前需要了解：

1. **API 可能大幅改变** - 由于是实验性，API 不保证向后兼容
2. **生产环境谨慎** - Facebook 内部使用，但外部生态系统不成熟
3. **替代方案成熟** - Jotai 提供了类似的API，但更稳定

## 相关概念

- [[Jotai]] - 类似但更稳定的原子化方案
- [[原子化状态管理]] - 原子化范式详解
- [[React 并发特性]] - React 18 新特性
- [[Zustand]] - 极简集中式方案

## 参考

- [Recoil 官方文档](https://recoiljs.org/)
- [GitHub](https://github.com/facebookexperimental/Recoil)
- [Why I Switched from Recoil to Jotai](https://blog.bitsrc.io/why-i-switched-from-recoil-to-jotai-8a1e66c4b4da)
