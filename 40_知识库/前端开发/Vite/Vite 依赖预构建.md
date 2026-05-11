---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Vite
  - 工程化
created: 2026-05-08
---
# Vite 依赖预构建

## 定义

Vite 依赖预构建是开发启动时用 esbuild 把 CommonJS 或多文件依赖转换为更适合浏览器 ESM 加载的形式。

## 要点

- 减少浏览器请求大量依赖小文件的成本。
- 统一 CommonJS 与 ESM 兼容问题。
- 依赖变化或配置变化可能触发重新预构建。

## 相关概念

- [[Vite 原理与插件机制总览]]
- [[模块化]]
- [[包管理与依赖治理]]

## 工作流程

```mermaid
flowchart LR
  A[扫描源码导入] --> B[识别第三方依赖]
  B --> C[esbuild 预构建]
  C --> D[缓存到 node_modules/.vite]
  D --> E[浏览器按 ESM 加载]
```

## 实践检查清单

- 依赖升级后是否清理 Vite 缓存验证问题。
- CommonJS 依赖是否能被正确转换为 ESM。
- monorepo 或 linked package 是否需要配置 `optimizeDeps`。
- 预构建慢时是否定位大依赖和重复依赖。
- 开发与生产构建差异是否用测试覆盖。

## 案例

本地启动时某个 CommonJS 包报导出错误，可以尝试把它显式加入 `optimizeDeps.include`，或排除后让插件转换，再验证 HMR 和生产构建是否都正常。

## 排查边界

依赖预构建主要影响开发体验，不等于生产构建结果。遇到启动慢、导出异常或依赖缓存异常时，应先确认依赖版本、锁文件、`node_modules/.vite` 缓存和 `optimizeDeps` 配置，再判断是否需要清缓存或显式 include/exclude。

monorepo、软链包和本地调试包更容易出现预构建边界问题。需要明确哪些包当作源码转换，哪些包当作第三方依赖预构建，否则 HMR、类型和打包结果可能不一致。

## 常见误区

- 把开发环境预构建问题误认为生产打包问题。
- 修改依赖版本后不清理缓存，排查方向被旧产物干扰。
- 盲目 include 所有依赖，导致启动变慢。

## 掘金文章补充

掘金文章《vite -- NPM 依赖解析和预构建 && 热更新》补充了预构建的两个核心目的：把浏览器无法直接处理的裸模块导入重写为可访问 URL，并用 esbuild 把 CommonJS/UMD 或内部模块很多的依赖转换成浏览器更容易加载的 ESM 产物。首次启动或依赖、配置变化时会触发预构建，结果通常缓存到 `node_modules/.vite`。

`optimizeDeps.include` 和 `optimizeDeps.exclude` 要按依赖形态使用：未被源码静态发现、软链包、内部模块很多或 CommonJS 依赖，通常考虑 include；已经是小而标准的 ESM 依赖，可以考虑排除，让浏览器直接加载。若某个 ESM 依赖内部还依赖 CommonJS 包，排除外层后可能仍需要把嵌套 CommonJS 显式 include。

来源：[vite -- NPM 依赖解析和预构建 && 热更新](https://juejin.cn/post/7498266812321366057)
