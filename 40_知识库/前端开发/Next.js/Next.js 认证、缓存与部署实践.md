---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Next.js
  - 部署
created: 2026-05-08
---
# Next.js 认证、缓存与部署实践

## 定义

Next.js 认证、缓存与部署实践关注 App Router 应用在登录态、数据缓存、运行时选择和生产发布中的工程边界。

## 要点

- 认证要区分服务端读取 Cookie、客户端会话状态和后端授权。
- 缓存策略需要明确页面、请求和 CDN 层级。
- 部署前要确认 Node/Edge Runtime、环境变量和日志监控。

## 相关概念

- [[Next.js App Router 总览]]
- [[前端鉴权与 Token 存储安全]]
- [[云原生部署总览：Docker、Kubernetes 与 CI-CD]]

## 落地流程

```mermaid
flowchart LR
  A[确认认证模式] --> B[设计缓存边界]
  B --> C[选择运行时]
  C --> D[配置环境变量]
  D --> E[部署和监控]
```

## 实践检查清单

- 服务端组件读取 Cookie 后是否影响缓存策略。
- 登录态页面是否避免被错误静态缓存。
- API 请求是否区分用户级缓存、页面缓存和 CDN 缓存。
- Edge Runtime 使用的依赖是否兼容。
- 部署后是否能查看日志、错误率、冷启动和缓存命中率。

## 案例

用户中心页面需要读取 Cookie 并展示个人信息，不能按公共静态页面缓存；博客详情页则可以使用静态生成或 ISR，提高访问性能。

## 常见误区

- 登录态数据被静态缓存，造成用户数据串扰。
- 所有请求都禁用缓存，浪费 Next.js 的性能优势。
- 依赖 Node API 的代码被放到 Edge Runtime 中运行失败。

## 复盘问题

- 这个页面是否依赖用户身份、Cookie、Header 或实时数据。
- 缓存失效后是否能解释数据何时更新、谁触发更新、用户会看到什么。
- 部署环境是否已经覆盖日志、错误上报、环境变量和运行时兼容性验证。

## 掘金文章补充

掘金文章《【Next.js】Caching》把 App Router 缓存拆成四层：Request Memoization、Data Cache、Full Route Cache 和 Router Cache。Request Memoization 是 React 渲染期间对相同 GET `fetch` 的去重，只在一次服务端组件树渲染生命周期内有效；Data Cache 是 Next.js 服务端持久缓存，可通过 `revalidate`、`revalidatePath`、`revalidateTag` 控制；Full Route Cache 缓存静态渲染结果；Router Cache 是客户端内存里的 RSC Payload 缓存，用于加速导航。

认证页面要特别小心：一旦读取 Cookie、Header 或用户身份，页面通常不应被当作公共静态结果缓存。可以用 `cache: 'no-store'`、`revalidate = 0`、`dynamic = 'force-dynamic'` 或按用户隔离的服务端逻辑控制缓存边界。博客、文档、营销页可以利用 Data Cache/ISR；用户中心、订单、权限页则优先保证隔离和实时性。

来源：[【Next.js】Caching](https://juejin.cn/post/7474019962719780890)
