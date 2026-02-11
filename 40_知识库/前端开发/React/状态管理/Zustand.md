---
title: "Zustand"
date: 2026-02-11
tags: [前端框架, 状态管理, React, 概念]
category: 前端开发
status: active
---

# Zustand

## 定义

Zustand（德语意为"状态"）是一个基于 Hooks 的小型、快速、可扩展的 React 状态管理库，采用极简 API 设计，无需 Provider 包裹即可使用。

## 核心特征

| 特征 | 说明 |
|-----|------|
| **轻量级** | 包体积极小 (~1KB gzipped) |
| **无样板代码** | 不需要 actions、reducers、action creators |
| **TypeScript 原生支持** | 无需额外类型定义 |
| **高性能** | 基于选择器的细粒度订阅 |
| **中间件生态** | devtools、persist、immer 等 |

## 核心 API

### create 函数

```typescript
const useStore = create<T>((set, get, api) => initialState)
```

- `set`：更新状态
- `get`：获取当前状态
- `api`：Store 实例

### 选择器模式

```typescript
const count = useStore((state) => state.count)
```

## 适用场景

- ✅ 中小型 React 应用
- ✅ 需要快速状态管理原型的场景
- ✅ 避免 Context API 性能陷阱
- ✅ 从 Redux 迁移的过渡方案
- ❌ 超大型应用（可考虑 Redux Toolkit）
- ❌ 需要严格数据流约束的团队

## 对比其他方案

| 特性 | Zustand | Redux | Context + useState | Recoil |
|-----|---------|-------|-------------------|--------|
| 学习成本 | 低 | 高 | 低 | 中 |
| 包体积 | 极小 | 大 | 内置 | 小 |
| 性能 | 好 | 好 | 一般 | 好 |
| DevTools | 有 | 强大 | 无 | 有 |
| 服务器状态 | 需配合 RQ | 需配合 RQ | 需配合 RQ | 需配合 RQ |

## 相关概念

- [[选择器模式]] - 精确数据提取与性能优化
- [[中间件模式]] - 扩展 Store 功能
- [[状态持久化]] - 保存和恢复应用状态
- [[React Hooks]] - 状态管理基础
- [[Redux]] - 传统状态管理方案
- [[React Query]] - 服务器状态管理

## 参考

- 主研究笔记：[[30_研究/SoftwareEngineering/Zustand/Zustand|Zustand 完整指南]]
- 官方文档：https://docs.pmnd.rs/zustand
