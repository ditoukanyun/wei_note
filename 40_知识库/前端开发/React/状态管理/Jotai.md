---
title: "Jotai"
date: 2026-02-11
tags: [前端框架, 状态管理, React, 概念, 原子化]
category: 前端开发
status: active
---

# Jotai

## 定义

Jotai（日语「状态」的发音）是一个基于**原子化状态管理**理念的 React 状态管理库。它采用自下而上的方式，将状态分解为最小的独立单元（Atoms），通过组合这些原子来构建应用状态。

**核心理念**: Primitive and flexible state management for React.

## 核心概念

| 概念 | API | 说明 |
|-----|-----|------|
| **Atom** | `atom(defaultValue)` | 状态的最小单位 |
| **Derived Atom** | `atom(read, write)` | 基于其他原子的派生状态 |
| **useAtom** | `useAtom(atom)` | 读写原子的 Hook |
| **useAtomValue** | `useAtomValue(atom)` | 只读原子的 Hook |
| **useSetAtom** | `useSetAtom(atom)` | 只写原子的 Hook |

## 基础用法

### 1. 创建原子

```typescript
import { atom } from 'jotai'

// 基础原子
const countAtom = atom(0)
const userAtom = atom({ name: '', email: '' })

// 派生原子（只读）
const doubleCountAtom = atom(
  get => get(countAtom) * 2
)

// 可写派生原子
const decrementCountAtom = atom(
  get => get(countAtom),
  (get, set, newValue: number) => {
    set(countAtom, get(countAtom) - newValue)
  }
)
```

### 2. 在组件中使用

```tsx
import { useAtom, useAtomValue, useSetAtom } from 'jotai'

// 读写原子
function Counter() {
  const [count, setCount] = useAtom(countAtom)
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(c => c + 1)}>+</button>
    </div>
  )
}

// 只读派生状态
function DoubleCounter() {
  const doubleCount = useAtomValue(doubleCountAtom)
  return <p>Double: {doubleCount}</p>
}

// 只写（性能优化）
function IncrementButton() {
  const setCount = useSetAtom(countAtom)
  // 这个组件不会因为 count 变化而重渲染
  return <button onClick={() => setCount(c => c + 1)}>+</button>
}
```

### 3. 异步原子

```typescript
const userIdAtom = atom(1)

// 异步派生原子
const userAtom = atom(async (get) => {
  const userId = get(userIdAtom)
  const response = await fetch(`/api/users/${userId}`)
  return response.json()
})

// 在组件中使用 Suspense
function UserProfile() {
  const user = useAtomValue(userAtom)
  return <div>{user.name}</div>
}

// 配合 Suspense
<Suspense fallback={<Loading />}>
  <UserProfile />
</Suspense>
```

## 原子组合

Jotai 的优势在于原子的灵活组合：

```typescript
// 基础原子
const firstNameAtom = atom('John')
const lastNameAtom = atom('Doe')
const ageAtom = atom(30)

// 派生原子组合
const fullNameAtom = atom(
  get => `${get(firstNameAtom)} ${get(lastNameAtom)}`
)

// 复杂对象组合
const personAtom = atom(
  get => ({
    fullName: get(fullNameAtom),
    age: get(ageAtom),
    isAdult: get(ageAtom) >= 18
  })
)

// 可写组合原子
const updatePersonAtom = atom(
  null,
  (get, set, update: { firstName?: string; lastName?: string; age?: number }) => {
    if (update.firstName) set(firstNameAtom, update.firstName)
    if (update.lastName) set(lastNameAtom, update.lastName)
    if (update.age) set(ageAtom, update.age)
  }
)
```

## 与 Zustand/Redux 对比

| 特性 | Jotai | Zustand | Redux (RTK) |
|-----|-------|---------|-------------|
| **哲学** | 原子化（自下而上） | 极简 Store | 集中式 Store |
| **API 复杂度** | 低 | 极低 | 中等 |
| **Provider** | 可选 | 不需要 | 需要 |
| **更新粒度** | 细粒度（原子级） | 选择器级 | 分支级 |
| **TypeScript** | 优秀 | 良好 | 良好 |
| **中间件** | 少量 | 丰富 | 非常丰富 |
| **DevTools** | 基础 | 基础 | 强大 |
| **包体积** | 极小 (~1KB) | 极小 (~1KB) | 中等 |

### 代码风格对比

```typescript
// Jotai - 分散的原子
const countAtom = atom(0)
const userAtom = atom(null)
// 组件中使用 useAtom(countAtom)

// Zustand - 单一的 Store
const useStore = create(set => ({
  count: 0,
  user: null,
  increment: () => set(state => ({ count: state.count + 1 }))
}))
// 组件中使用 useStore(state => state.count)

// Redux - 单一的状态树
// store = { counter: { value: 0 }, user: { data: null } }
// 组件中使用 useSelector(state => state.counter.value)
```

## 适用场景

✅ **选择 Jotai 当：**
- 喜欢函数式编程和组合思想
- 需要极致的性能（细粒度更新）
- 状态高度分散，难以组织成统一的 Store
- 需要使用 Suspense 进行异步状态管理
- 希望避免 Prop Drilling 但不想引入 Provider

❌ **选择 Zustand/Redux 当：**
- 需要全局统一的 Store 结构
- 团队更习惯集中式管理
- 需要强大的调试工具
- 复杂的中间件需求

## 最佳实践

### 1. 原子拆分原则

```typescript
// ✅ 拆分为独立原子
const userIdAtom = atom(null)
const userProfileAtom = atom(null)
const userPreferencesAtom = atom({})

// ❌ 避免嵌套对象原子
const userAtom = atom({
  id: null,
  profile: null,
  preferences: {}
})
```

### 2. 使用 Provider 隔离状态

```tsx
import { Provider } from 'jotai'

// 为特定子树提供独立的状态上下文
function FeatureModule() {
  return (
    <Provider>
      <FeatureComponents />
    </Provider>
  )
}
```

### 3. 原子派生优于重复状态

```typescript
// ✅ 使用派生原子
const firstNameAtom = atom('John')
const lastNameAtom = atom('Doe')
const fullNameAtom = atom(
  get => `${get(firstNameAtom)} ${get(lastNameAtom)}`
)

// ❌ 避免重复存储
const fullNameAtom = atom('John Doe')  // 需要手动同步
```

## 高级特性

### Atom Family（动态原子）

```typescript
import { atomFamily } from 'jotai/utils'

// 创建参数化的原子
const todoAtomFamily = atomFamily((id: string) =>
  atom({ id, text: '', completed: false })
)

// 使用
const todo1 = todoAtomFamily('1')
const todo2 = todoAtomFamily('2')
```

### 存储和持久化

```typescript
import { atomWithStorage } from 'jotai/utils'

// 自动同步到 localStorage
const darkModeAtom = atomWithStorage('darkMode', false)
```

### 与 React Query 配合

```typescript
import { atomWithQuery } from 'jotai-tanstack-query'

const userAtom = atomWithQuery(get => ({
  queryKey: ['user', get(userIdAtom)],
  queryFn: async ({ queryKey }) => {
    const res = await fetch(`/api/user/${queryKey[1]}`)
    return res.json()
  }
}))
```

## 相关概念

- [[原子化状态管理]] - 原子化范式详解
- [[Recoil]] - Facebook 的原子化方案
- [[Zustand]] - 极简集中式方案
- [[Redux]] - 传统集中式方案
- [[Suspense]] - React 异步边界

## 参考

- [Jotai 官方文档](https://jotai.org/)
- [GitHub](https://github.com/pmndrs/jotai)
- [Jotai 生态系统](https://jotai.org/docs/extensions)
