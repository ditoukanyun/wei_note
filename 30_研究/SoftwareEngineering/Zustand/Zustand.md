---
title: "Zustand"
created: 2026-02-11
type: reference
area: "[[SoftwareEngineering]]"
tags: [status/refactored, 前端框架, 状态管理, React]
source: https://juejin.cn/post/7497536634964623396
---

# Zustand

> Zustand（德语：状态）是一个小型、快速、可扩展的 React 状态管理解决方案，基于 Hooks，API 非常简洁。

## 概述

Zustand 提供了比 Redux 更简单的 API，比 Context API 更好的性能，适合中小型项目或需要快速状态管理的场景。

**核心优势：**
- 极小的包体积
- 无需 Provider 包裹
- TypeScript 原生支持
- 丰富的中间件生态
- 支持 React 18 Concurrent Features

---

## 核心概念

### 1. create 函数

一切始于 `create` 函数，用于创建 Store。

```javascript
import { create } from 'zustand'

const useStore = create((set, get) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
}))
```

**回调函数参数：**
- `set`：更新状态，支持浅合并
- `get`：获取当前状态

### 2. 状态更新

```javascript
// 函数式更新（推荐）
set((state) => ({ count: state.count + 1 }))

// 直接赋值
set({ count: 5 })

// 嵌套对象更新
set((state) => ({
  user: { ...state.user, name: newName }
}))
```

### 3. 在组件中使用

```jsx
// 获取整个 store（不推荐，会导致不必要的重渲染）
const store = useStore()

// 使用选择器（推荐）
const count = useStore((state) => state.count)
const increment = useStore((state) => state.increment)
```

---

## 选择器与性能优化

### 为什么需要选择器

不使用选择器时，任何状态变化都会触发组件重渲染。

```jsx
// ❌ 不推荐 - 任意状态变化都会触发重渲染
const store = useStore()

// ✅ 推荐 - 只有 count 变化时才会重渲染
const count = useStore((state) => state.count)
```

### 选择多个值

使用 `shallow` 进行浅比较，避免不必要的重渲染。

```jsx
import { shallow } from 'zustand/shallow'

const { count, name } = useStore(
  (state) => ({ count: state.count, name: state.name }),
  shallow
)
```

**关键点：**
- 选择器返回的对象每次渲染都是新对象
- `shallow` 比较顶层属性是否变化
- Action 函数引用稳定，选择它们不会触发重渲染

---

## 中间件

### devtools - Redux DevTools 集成

```javascript
import { devtools } from 'zustand/middleware'

const useStore = create(
  devtools(
    (set) => ({
      count: 0,
      increment: () => set((state) => ({ count: state.count + 1 })),
    }),
    { name: 'MyStore' }
  )
)
```

### persist - 状态持久化

```javascript
import { persist, createJSONStorage } from 'zustand/middleware'

const useStore = create(
  persist(
    (set) => ({
      count: 0,
      theme: 'light',
    }),
    {
      name: 'my-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ count: state.count, theme: state.theme }),
    }
  )
)
```

**配置选项：**
- `name`：存储键名（必需）
- `storage`：存储引擎（默认 localStorage）
- `partialize`：选择性持久化
- `version` + `migrate`：数据迁移

### immer - 处理嵌套状态

```javascript
import { immer } from 'zustand/middleware'

const useStore = create(
  immer((set) => ({
    user: { profile: { preferences: { theme: 'light' } } },
    setTheme: (theme) =>
      set((draft) => {
        draft.user.profile.preferences.theme = theme
      }),
  }))
)
```

**优势：**
- 直接修改嵌套属性
- 自动处理不可变性
- 代码更简洁

### 组合中间件

```javascript
const useStore = create(
  devtools(
    persist(
      immer((set) => ({ /* store */ })),
      { name: 'my-storage' }
    ),
    { name: 'MyStore' }
  )
)
```

**推荐顺序：** devtools(外) → persist(中) → immer(内)

---

## 分模块设计

### 方式一：多个独立 Store（推荐）

适合功能模块相对独立的应用。

```javascript
// store/userStore.js
const useUserStore = create((set) => ({
  user: null,
  login: (user) => set({ user }),
  logout: () => set({ user: null }),
}))

// store/cartStore.js
const useCartStore = create((set) => ({
  items: [],
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
}))
```

**优点：**
- 简单直观
- 强隔离性
- 类型安全

**缺点：**
- 跨 Store 交互稍复杂

### 方式二：Slice 模式（类似 Redux）

适合模块间有大量交互的场景。

```javascript
// slices/userSlice.js
const createUserSlice = (set, get) => ({
  user: null,
  login: (user) => set({ user }),
})

// slices/cartSlice.js
const createCartSlice = (set, get) => ({
  items: [],
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
})

// store/appStore.js
const useAppStore = create((...a) => ({
  ...createUserSlice(...a),
  ...createCartSlice(...a),
}))
```

**优点：**
- 单一 Store Hook
- 简化跨模块交互

**缺点：**
- 需要手动组合
- 注意命名冲突

---

## 与 React Query 结合

### 职责分离

| 状态类型 | 工具 | 说明 |
|---------|------|------|
| 服务器状态 | React Query | API 数据、缓存、加载/错误状态 |
| 客户端状态 | Zustand | UI 状态、主题、模态框、表单 |

### 示例模式

```jsx
function UserProfile({ userId }) {
  // React Query 管理服务器状态
  const { data: user, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  })

  // Zustand 管理客户端状态
  const theme = useUIStore((state) => state.theme)
  const setEditing = useUIStore((state) => state.setEditing)

  if (isLoading) return <Spinner />

  return (
    <div className={theme}>
      <h1>{user.name}</h1>
      <button onClick={() => setEditing(true)}>编辑</button>
    </div>
  )
}
```

---

## 最佳实践

### 1. 始终使用选择器

```jsx
// ✅ 好
const count = useStore((state) => state.count)

// ❌ 坏
const { count } = useStore()
```

### 2. 选择性持久化敏感数据

```javascript
partialize: (state) => ({
  settings: state.settings,
  // ❌ 不要持久化敏感信息如 token
})
```

### 3. 使用 devtools 命名 action

```javascript
set((state) => ({ count: state.count + 1 }), false, 'increment')
// 第三个参数是 action 名称，会显示在 Redux DevTools 中
```

### 4. 大型状态使用 immer

嵌套层级超过 2 层时，考虑使用 immer 中间件。

### 5. Store 结构清晰

```
store/
├── index.js          # 统一导出
├── userStore.js      # 用户相关
├── cartStore.js      # 购物车
└── uiStore.js        # UI 状态
```

---

## 常见误区

1. **在整个应用中传递 store 对象** - 使用选择器只取需要的数据
2. **在 set 中直接修改状态** - 除非使用 immer
3. **过度使用单一 Store** - 大型应用建议分模块
4. **持久化所有状态** - 只持久化真正需要的数据

---

## 相关概念

- [[选择器模式]] - 精确数据提取与性能优化
- [[中间件模式]] - 扩展 Store 功能
- [[状态持久化]] - 保存和恢复应用状态
- [[React状态管理]] - React 状态管理总览
- [[Redux]] - 传统状态管理方案
- [[React Query]] - 服务器状态管理
- [[Immer]] - 不可变性辅助库

---

## 参考资料

- [Zustand 官方文档](https://docs.pmnd.rs/zustand)
- [掘金教程](https://juejin.cn/post/7497536634964623396)
