---
type: reference
created: 2026-02-11
area: "[[SoftwareEngineering]]"
tags: [research, react, state-management, tanstack-query, data-fetching]
status: complete
---

# TanStack Query (React Query) 深度研究

## 概述

TanStack Query 是目前 React 生态中最流行的数据获取和服务器状态管理库。它不仅简化了数据获取流程，还通过智能缓存、后台更新和垃圾回收机制，极大地提升了用户体验。它被誉为"用于 React 的缺失的数据获取库"。

## 核心原理：查询生命周期

理解 TanStack Query 的核心在于理解查询的状态流转：

1.  **Fresh (新鲜)**: 数据刚获取，被认为是最新状态。在此期间不会重新请求。
2.  **Stale (陈旧)**: 数据过了 `staleTime` 后变为陈旧。此时虽然可用，但下次访问时会在后台重新验证。
3.  **Fetching (获取中)**: 正在向服务器请求数据。
4.  **Inactive (非活动)**: 没有组件订阅该查询（组件卸载）。
5.  **Deleted (删除)**: 非活动时间超过 `gcTime` (默认 5 分钟)，缓存被清除。

### 关键配置

-   **`staleTime` (默认为 0)**: 数据保持新鲜的时间。设为 `Infinity` 则永不陈旧（除非手动失效）。
-   **`gcTime` (默认为 5 分钟)**: 非活动查询保留在缓存中的时间（v5 之前叫 `cacheTime`）。

## 高级用法

### 1. 并行查询 (Parallel Queries)

手动写多个 `useQuery` 也是并行执行的。对于动态数量的查询，使用 `useQueries`：

```tsx
const results = useQueries({
  queries: userIds.map((id) => ({
    queryKey: ['user', id],
    queryFn: () => fetchUser(id),
  })),
})
```

### 2. 依赖查询 (Dependent Queries)

只有当满足某些条件时才执行查询。通过 `enabled` 选项实现。

```tsx
// 1. 获取用户
const { data: user } = useQuery({
  queryKey: ['user', email],
  queryFn: getUser,
})

const userId = user?.id

// 2. 获取用户的项目 (只有当 userId 存在时才执行)
const { data: projects } = useQuery({
  queryKey: ['projects', userId],
  queryFn: getProjects,
  enabled: !!userId, // 依赖于 userId
})
```

### 3. 无限加载 (Infinite Queries)

用于实现"加载更多"或无限滚动列表。

```tsx
const {
  data,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
} = useInfiniteQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  getNextPageParam: (lastPage, allPages) => lastPage.nextCursor,
  initialPageParam: 0,
})
```

### 4. 预取数据 (Prefetching)

在用户交互之前提前加载数据，提升感知性能。常用于 `onMouseEnter`。

```tsx
const queryClient = useQueryClient()

const prefetchUser = async (id) => {
  // 此时数据已被缓存，稍后组件挂载时将立即显示
  await queryClient.prefetchQuery({
    queryKey: ['user', id],
    queryFn: () => fetchUser(id),
  })
}
```

### 5. Suspense 集成

React 18+ 的 Suspense 模式，让数据加载像同步代码一样简单。

```tsx
import { useSuspenseQuery } from '@tanstack/react-query'

function UserProfile() {
  const { data } = useSuspenseQuery({
    queryKey: ['user'],
    queryFn: fetchUser,
  })
  
  // 不需要处理 isLoading，因为 Suspense 会处理 fallback
  return <div>{data.name}</div>
}

// 父组件
<Suspense fallback={<div>Loading...</div>}>
  <UserProfile />
</Suspense>
```

## 生态系统与工具

-   **DevTools**: 必备工具。可视化查看缓存键、状态、数据内容。
-   **TypeScript**: v5 对 TypeScript 的支持非常完善，能自动推导数据类型。
-   **React Native**: 完全支持。

## 对比其他库

| 特性 | TanStack Query | SWR | RTK Query | Apollo Client |
| :--- | :--- | :--- | :--- | :--- |
| **生态** | 庞大 (React/Vue/Solid) | 专注于 React | Redux Toolkit 集成 | GraphQL 专用 |
| **缓存策略** | 极强 (GC/StaleTime) | 强 (Stale-While-Revalidate) | 强 | 强 (Normalized Cache) |
| **DevTools** | 优秀 | 无 (仅社区版) | Redux DevTools | 优秀 |
| **大小** | 中等 | 轻量 | 中等 (含 Redux) | 较重 |
| **适用场景** | 通用 REST/GraphQL | 轻量级请求 | Redux 重度用户 | GraphQL 重度用户 |

## 最佳实践总结

1.  **Query Key 设计**: 始终将依赖项包含在 Key 中 (如 `['todos', filter]`)。
2.  **默认配置**: 在 `QueryClient` 中设置全局默认 `staleTime` (如 1分钟)，避免过于频繁的后台请求。
3.  **不要在 useEffect 中请求**: 让 `useQuery` 处理数据获取，不要手动管理。
4.  **分离服务器状态**: 不要把 Query 数据同步到 Zustand/Context，直接在组件中使用 `useQuery` 读取缓存。

## 相关阅读
- [[TanStack-Query]]: 知识库原子笔记
- [[Zustand]]: 客户端状态管理
- [[React 性能优化]]: 减少渲染
