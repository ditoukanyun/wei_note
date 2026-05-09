---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - TypeScript
  - 工程化
created: 2026-05-08
---
# TypeScript tsconfig 配置详解

## 定义

`tsconfig.json` 是 TypeScript 项目的编译配置文件，用于定义目标版本、模块系统、类型检查严格度、路径别名和输出行为。

## 常见配置

- `target`：输出 JavaScript 语法版本。
- `module`：模块格式。
- `strict`：启用严格类型检查。
- `paths`：配置路径别名。
- `noEmit`：只做类型检查，不输出文件。

## 相关概念

- [[TypeScript 工程实践总览]]
- [[Vite 原理与插件机制总览]]

## 配置流程

```mermaid
flowchart LR
  A[确定运行环境] --> B[设置 target 和 module]
  B --> C[开启 strict]
  C --> D[配置路径和类型]
  D --> E[接入构建和 CI]
```

## 实践检查清单

- `strict` 是否开启，并逐步处理历史项目问题。
- `target` 是否匹配浏览器或 Node 运行环境。
- `moduleResolution` 是否匹配 Vite、NodeNext 或 Bundler 模式。
- `paths` 是否和构建工具、测试工具同步配置。
- CI 是否运行 `tsc --noEmit` 作为类型门禁。

## 案例

Vite React 项目通常由 Vite 负责打包，TypeScript 只做类型检查，因此可配置 `noEmit: true`，并在 CI 中单独运行 `tsc --noEmit`。

## 常见误区

- 只配置 `paths`，忘记同步 Vite、Jest 或 Vitest alias。
- 关闭严格模式，后续类型债越来越难还。
- 不理解 `target` 和 polyfill 的关系，导致旧浏览器运行失败。
