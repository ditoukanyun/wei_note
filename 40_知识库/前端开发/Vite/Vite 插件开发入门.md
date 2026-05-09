---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Vite
  - 插件
created: 2026-05-08
---
# Vite 插件开发入门

## 定义

Vite 插件通过 Rollup 插件钩子和 Vite 专属钩子扩展构建、转换和开发服务器能力。

## 常用钩子

- `config`：修改 Vite 配置。
- `resolveId`：自定义模块解析。
- `load`：加载虚拟模块。
- `transform`：转换模块代码。
- `configureServer`：扩展开发服务器。

## 相关概念

- [[Vite 原理与插件机制总览]]
- [[Webpack]]
- [[模块化]]

## 开发流程

```mermaid
flowchart LR
  A[明确扩展目标] --> B[选择插件钩子]
  B --> C[实现转换或服务扩展]
  C --> D[在示例项目验证]
  D --> E[覆盖 dev 和 build]
```

## 实践检查清单

- 插件是否同时考虑开发服务器和生产构建。
- 钩子选择是否最小化，避免在全局 transform 中做重活。
- 虚拟模块命名是否有命名空间，避免冲突。
- 是否处理 sourcemap，方便调试。
- 插件配置是否有默认值和类型定义。

## 案例

生成虚拟配置模块时，可以在 `resolveId` 中识别虚拟模块 ID，在 `load` 中返回代码。这样业务代码可以像普通模块一样导入配置。

## 常见误区

- 在 transform 中处理所有文件，导致开发环境变慢。
- 只验证 `vite dev`，没有验证 `vite build`。
- 插件副作用依赖执行顺序，却没有声明清楚。
