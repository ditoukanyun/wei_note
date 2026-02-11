# Webpack 学习笔记

> 本文档基于掘金文章《一文带你读懂 webpack 的知识和原理，附带常见面试题！》整理，结合个人理解与实践，系统梳理 Webpack 知识体系。

---

## 📚 文档导航

### 核心基础
- [[01-webpack基础]] - Webpack 基础概念、配置结构、开发/生产环境配置
- [[02-Loader详解]] - Loader 原理、常见 Loader、如何编写 Loader
- [[03-Plugin详解]] - Plugin 原理、常见 Plugin、如何编写 Plugin
- [[04-Webpack原理]] - 构建流程、HMR、Tree Shaking、代码分割、Module Federation

### 实战与面试
- [[05-面试题汇总]] - 25+ 道高频面试题，含详细答案

---

## 🎯 学习路径

### 第一阶段：基础入门
1. 理解 Webpack 是什么、能做什么
2. 掌握 Entry、Output、Module、Plugin 基本配置
3. 熟悉常用 Loader（babel-loader、css-loader 等）
4. 配置 devServer 开发服务器

### 第二阶段：进阶配置
1. 掌握多环境配置（开发/生产分离）
2. 理解 Loader 与 Plugin 的区别
3. 学习代码分割、懒加载配置
4. 掌握 Source Map 配置与选择

### 第三阶段：原理深入
1. 理解 Webpack 构建流程
2. 掌握 HMR 热更新原理
3. 理解 Tree Shaking 机制
4. 了解 Scope Hoisting、Module Federation

### 第四阶段：优化实践
1. 构建速度优化（缓存、多线程、缩小范围）
2. 产物体积优化（压缩、分割、Tree Shaking）
3. 运行时性能优化（懒加载、预加载、CDN）
4. 性能分析与监控

---

## 📝 面试重点

### 高频必问
1. **Loader 与 Plugin 的区别**
2. **Webpack 构建流程**
3. **HMR 热更新原理**
4. **Tree Shaking 原理**
5. **如何优化 Webpack 构建速度**
6. **代码分割的实现方式**
7. **文件指纹（Hash）的类型与使用**

### 进阶问题
1. Compiler 与 Compilation 的区别
2. Tapable 钩子机制
3. Webpack 5 新特性
4. 循环依赖的处理
5. 如何编写 Loader/Plugin

---

## 🔗 参考资源

- [Webpack 官方文档](https://webpack.js.org/)
- [Webpack 中文文档](https://www.webpackjs.com/)
- [深入浅出 Webpack](http://webpack.wuhaolin.cn/)
- [Webpack 5 核心原理与应用实践](https://juejin.cn/book/7115598540721618944)

---

## 🗂️ 文件结构

```
webpack/
├── README.md                    # 本文件（目录导航）
├── 01-webpack基础.md            # Webpack 基础知识
├── 02-Loader详解.md             # Loader 详解
├── 03-Plugin详解.md             # Plugin 详解
├── 04-Webpack原理.md            # 原理深入
└── 05-面试题汇总.md             # 面试题与答案
```

---

## 📌 速查表

### 常用命令
```bash
# 开发模式
webpack --mode=development

# 生产模式
webpack --mode=production

# 启动开发服务器
npx webpack-dev-server

# 分析打包结果
webpack --analyze
```

### 常用配置速查
```javascript
// 开发环境推荐 devtool
devtool: 'eval-cheap-module-source-map'

// 生产环境推荐 devtool  
devtool: 'hidden-source-map'

// 开启缓存
module.exports = {
  cache: { type: 'filesystem' }
}

// 代码分割
optimization: {
  splitChunks: { chunks: 'all' }
}
```

---

## 📝 核心概念

- webpack 是一个现代 JavaScript 应用程序的静态模块打包器(module bundler)。当 webpack 处理应用程序时，它会递归地构建一个依赖关系图(dependency graph)，其中包含应用程序需要的每个模块，然后将所有这些模块打包成一个或多个 bundle。

> 💡 **提示**：建议按照学习路径循序渐进，先掌握基础配置，再深入原理，最后通过面试题检验学习效果。