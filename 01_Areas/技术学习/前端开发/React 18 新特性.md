---
tags: [learning, react, frontend, hooks]
date: 2024-02-09
source: React 官方文档 + 实战经验
difficulty: 中级
category: 前端
status: 学习中
---

# React 18 新特性

## 🎯 学习目标
- 理解 React 18 的主要新特性
- 掌握并发渲染的概念
- 学会使用新 Hooks

## 📚 核心概念

### 概念1：并发渲染 (Concurrent Rendering)
**定义**：React 18 引入了并发渲染机制，允许 React 中断渲染工作以处理更高优先级的更新。

**理解要点**：
- 不是并行执行，而是可中断的渲染
- 允许 React 准备多个版本的 UI
- 用户交互可以优先于后台渲染

**代码示例**：
```javascript
// 使用 useTransition 标记非紧急更新
import { useTransition } from 'react';

function App() {
  const [isPending, startTransition] = useTransition();
  const [count, setCount] = useState(0);

  const handleClick = () => {
    startTransition(() => {
      setCount(c => c + 1);
    });
  };

  return (
    <div>
      {isPending && <Spinner />}
      <button onClick={handleClick}>{count}</button>
    </div>
  );
}
```

### 概念2：自动批处理 (Automatic Batching)
**定义**：React 18 自动将多个状态更新合并为一次重新渲染，提高性能。

**理解要点**：
- 在事件处理函数中自动批处理
- 在 setTimeout、Promise 中也支持批处理
- 减少了不必要的渲染次数

**代码示例**：
```javascript
// React 18 之前：会触发 2 次渲染
setTimeout(() => {
  setCount(c => c + 1);
  setFlag(f => !f);
}, 1000);

// React 18：只会触发 1 次渲染（自动批处理）
```

### 概念3：Suspense 改进
**定义**：更好的 Suspense 支持，包括服务器端渲染和错误处理。

**理解要点**：
- 可以在组件树任意位置使用
- 更好的 SSR 支持
- 配合数据获取使用

**代码示例**：
```javascript
import { Suspense } from 'react';

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <ProfileData />
      <Suspense fallback={<PostsSkeleton />}>
        <PostsData />
      </Suspense>
    </Suspense>
  );
}
```

## 🛠 实践应用

### 使用场景
1. **大数据列表渲染** - 使用 useTransition 保持界面响应
2. **搜索过滤** - 使用 useDeferredValue 延迟更新搜索结果
3. **数据获取** - 使用 Suspense 处理加载状态

### 最佳实践
- ✅ **应该做的**：
  - 使用 useTransition 标记非紧急更新
  - 使用 useDeferredValue 延迟不重要的 UI 更新
  - 合理使用 Suspense 组织加载状态

- ❌ **避免的**：
  - 不要滥用并发特性
  - 不要在 useTransition 中执行同步的昂贵计算
  - 不要忽略 fallback UI 的设计

## 🔗 相关链接

### 官方文档
- [React 18 发布说明](https://react.dev/blog/2022/03/29/react-v18)
- [并发模式文档](https://react.dev/blog/2022/03/29/react-v18#what-is-concurrent-react)

### 推荐文章
- [React 18 完整指南](https://www.sitepoint.com/react-18-whats-new/)

## 🧠 深入理解

### 常见问题
**Q1：并发渲染会影响现有代码吗？**
**A：** 不会，React 18 是向后兼容的。只有在使用新特性时才会启用并发模式。

**Q2：什么时候应该使用 useTransition？**
**A：** 当某个状态更新可以延迟，且不阻塞用户交互时使用，如搜索过滤、列表排序等。

### 易错点
- 误认为并发渲染是并行执行
- 在 useTransition 中执行同步阻塞操作
- 过度使用导致代码复杂度增加

## 📝 个人笔记

### 关键收获
- React 18 的并发特性是可选的，不会破坏现有代码
- useTransition 和 useDeferredValue 是解决不同场景的工具
- Suspense 的改进使数据获取更加声明式

### 待深入研究
- [ ] React 18 的 SSR 改进
- [ ] useId Hook 的使用场景
- [ ] useSyncExternalStore 的应用

### 相关笔记
- [[React Hooks]]
- [[React 性能优化]]
- [[React 项目实战]]