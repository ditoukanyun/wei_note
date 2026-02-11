---
title: "TanStack Query (React Query)"
date: 2026-02-11
tags: [前端框架, 状态管理, React, 服务器状态, 数据获取]
category: 前端开发
status: active
---

# TanStack Query (React Query)

## 定义

**TanStack Query** (前身为 React Query) 是一个用于 React、Solid、Vue 和 Svelte 的强大的**异步状态管理库**。它主要用于管理**服务器状态**（Server State），即那些持久化在服务器上、通过异步 API 获取、可能被其他人修改的数据。

### 服务器状态 vs 客户端状态

| 特性 | 服务器状态 (Server State) | 客户端状态 (Client State) |
| :--- | :--- | :--- |
| **来源** | 远程服务器 (DB/API) | 本地 (UI 组件/用户交互) |
| **控制权** | 半控制 (可能被他人修改) | 完全控制 (由当前用户拥有) |
| **特性** | 异步、需缓存、需更新、可能过期 | 同步、即时更新 |
| **工具** | **TanStack Query**, SWR, Apollo | **Zustand**, Redux, Context API |
| **示例** | 用户列表、商品详情、订单状态 | 模态框开关、侧边栏折叠、表单输入 |

## 核心概念

### 1. Stale-While-Revalidate (SWR)
这是 TanStack Query 的核心缓存策略。
-   **Stale (陈旧)**: 数据在获取后立即（或在 `staleTime` 后）被标记为"陈旧"。
-   **Revalidate (重新验证)**: 当数据被标记为陈旧且组件重新挂载、窗口重新聚焦或网络重连时，库会在后台自动重新获取最新数据。
-   **Cache (缓存)**: 在重新获取期间，UI 会立即展示缓存中的"陈旧"数据，提供快速响应的用户体验。

### 2. Query Key (查询键)
唯一标识一个查询的数组。
-   类似于依赖数组，当 Key 中的值变化时，查询会自动重新触发。
-   示例: `['todos']`, `['todos', { status: 'done' }]`, `['user', userId]`.

### 3. Mutation (变更)
用于创建/更新/删除数据或执行服务器副作用的操作。

## 核心 Hooks

### `useQuery` - 获取数据
用于读取服务器数据。

```tsx
import { useQuery } from '@tanstack/react-query'

function TodoList() {
  const { isPending, error, data } = useQuery({
    queryKey: ['todos'],
    queryFn: () => fetch('/api/todos').then((res) => res.json()),
  })

  if (isPending) return '加载中...'
  if (error) return '出错了: ' + error.message

  return (
    <ul>
      {data.map((todo) => (
        <li key={todo.id}>{todo.title}</li>
      ))}
    </ul>
  )
}
```

### `useMutation` - 修改数据
用于写入服务器数据。

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'

function AddTodo() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (newTodo) => {
      return axios.post('/todos', newTodo)
    },
    onSuccess: () => {
      // 成功后使 'todos' 查询失效，触发重新获取
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })

  return (
    <button onClick={() => mutation.mutate({ title: '新任务' })}>
      添加任务
    </button>
  )
}
```

## 与 Zustand/Redux 配合

在现代 React 应用中，推荐**职责分离**模式：

-   **TanStack Query**: 负责所有**API 数据**（获取、缓存、同步、错误处理）。
-   **Zustand/Redux**: 负责**UI 状态**（主题、侧边栏开关、复杂表单草稿）或**跨组件通信**。

**不推荐的做法**: 将 API 返回的数据存入 Redux/Zustand。这会导致数据同步困难和样板代码膨胀。

**完整示例: TanStack Query + Zustand**

```tsx
// 1. Zustand Store: 仅管理过滤条件 (Client State)
import { create } from 'zustand'

const useFilterStore = create((set) => ({
  filter: 'all',
  setFilter: (filter) => set({ filter }),
}))

// 2. Component: 结合使用
function TodoList() {
  // 从 Zustand 获取 UI 状态
  const filter = useFilterStore((state) => state.filter)
  
  // 使用 TanStack Query 获取数据，依赖于 filter
  const { data } = useQuery({
    queryKey: ['todos', filter], // filter 变化自动触发重新获取
    queryFn: () => fetchTodos(filter),
  })

  return <div>...</div>
}
```

## 优势

1.  **代码量减少**: 极其显著地减少了 `useEffect`, `isLoading` state, `try/catch` 等样板代码。
2.  **自动缓存**: 开箱即用的智能缓存和垃圾回收。
3.  **用户体验**: 窗口聚焦自动刷新、网络重连刷新、后台更新。
4.  **DevTools**: 强大的调试工具，可视化查看缓存状态。

## 高级示例：乐观更新 (Optimistic Updates)

在服务器响应之前立即更新 UI，如果失败则回滚。

```tsx
const mutation = useMutation({
  mutationFn: updateTodo,
  // 变更发生前立即执行
  onMutate: async (newTodo) => {
    // 1. 取消相关的正在进行的查询
    await queryClient.cancelQueries({ queryKey: ['todos'] })

    // 2. 保存旧数据快照 (用于回滚)
    const previousTodos = queryClient.getQueryData(['todos'])

    // 3. 乐观更新缓存
    queryClient.setQueryData(['todos'], (old) => [...old, newTodo])

    // 4. 返回上下文
    return { previousTodos }
  },
  // 发生错误时回滚
  onError: (err, newTodo, context) => {
    queryClient.setQueryData(['todos'], context.previousTodos)
  },
  // 无论成功失败，都重新验证以确保数据一致
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] })
  },
})
```

## 相关笔记
- [[Zustand]]: 推荐配合使用的轻量级客户端状态库
- [[React-源码-Hooks]]: React Hooks 机制基础
