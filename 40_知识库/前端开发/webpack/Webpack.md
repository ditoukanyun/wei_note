---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - Webpack
  - 工程化
created: 2026-05-08
---
# Webpack

## 定义

Webpack 是一个模块打包工具，把 JavaScript、CSS、图片等资源视为模块，通过 Loader 和 Plugin 构建依赖图并输出浏览器可加载的产物。

## 要点

- Loader 负责把不同类型资源转换为模块。
- Plugin 参与构建生命周期，扩展打包能力。
- Code Splitting、Tree Shaking 和缓存命名影响生产性能。
- Vite 更偏开发体验和原生 ESM，Webpack 仍适合复杂定制场景。

## 构建流程

```mermaid
flowchart LR
    A["入口 entry"] --> B["解析依赖图"]
    B --> C["Loader 转换资源"]
    C --> D["Plugin 扩展构建生命周期"]
    D --> E["代码分割与优化"]
    E --> F["输出 bundle/assets"]
```

Webpack 的核心是依赖图。它从入口文件出发，递归分析模块依赖，再通过 Loader 和 Plugin 把不同资源加工成浏览器可加载的产物。

## 核心概念

- **Entry**：构建入口，决定依赖图从哪里开始。
- **Output**：输出目录、文件名和资源路径。
- **Loader**：把 TypeScript、CSS、图片等非标准资源转换为模块。
- **Plugin**：参与编译生命周期，例如注入环境变量、抽取 CSS、生成 HTML。
- **Mode**：开发和生产模式下启用不同默认优化。
- **Chunk**：代码分割后的产物单元，影响首屏加载和缓存。

## 案例

后台管理系统首屏只需要登录页和主框架，不需要一次加载所有业务页面。可以通过动态导入做 [[代码分割]]：

```ts
const UserPage = lazy(() => import("./pages/UserPage"));
const OrderPage = lazy(() => import("./pages/OrderPage"));
```

Webpack 会把这些页面拆成独立 chunk，用户进入对应路由时再加载。这样能降低首屏包体积，但也要避免拆得过碎导致请求数过多。

## 优化检查清单

- 生产产物是否启用内容哈希，支持长期缓存。
- 第三方依赖是否被合理拆分，避免业务代码小改导致 vendor 缓存失效。
- 是否开启 Tree Shaking，并避免不必要的副作用导入。
- 图片、字体、CSS 是否有合适的压缩和缓存策略。
- Bundle 分析是否定位了过大的依赖。
- 新项目是否更适合使用 [[Vite 与 Webpack 的差异对比]]。

## 相关概念

- [[webpack/README]]
- [[Vite 与 Webpack 的差异对比]]
- [[代码分割]]
