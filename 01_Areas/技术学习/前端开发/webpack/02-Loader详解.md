# Loader 详解

## 1. Loader 是什么？

Loader 是 webpack 的核心概念之一，它负责将**非 JavaScript 文件**转换为 webpack 能够处理的模块。

### Loader 特点

- **函数本质**：本质上是一个函数，接收源文件内容，返回转换后的内容
- **链式调用**：支持多个 loader 链式处理，从右到左（从后到前）执行
- **单一职责**：每个 loader 只负责单一转换功能
- **无状态**：不应该在 loader 中保存状态

---

## 2. 常见 Loader 及作用

### 2.1 JavaScript 相关

| Loader | 作用 |
|--------|------|
| `babel-loader` | 将 ES6+ 转译为 ES5 |
| `ts-loader` | 将 TypeScript 转换为 JavaScript |
| `eslint-loader` | 使用 ESLint 检查代码规范 |

```javascript
// babel-loader 配置
{
  test: /\.js$/,
  exclude: /node_modules/,
  use: {
    loader: 'babel-loader',
    options: {
      presets: ['@babel/preset-env'],
      cacheDirectory: true // 启用缓存
    }
  }
}
```

### 2.2 CSS 相关

| Loader | 作用 |
|--------|------|
| `css-loader` | 解析 CSS 文件，支持模块化、压缩、导入 |
| `style-loader` | 将 CSS 注入到 DOM 中 |
| `sass-loader` | 将 SCSS/SASS 编译为 CSS |
| `less-loader` | 将 LESS 编译为 CSS |
| `postcss-loader` | 使用 PostCSS 处理 CSS（ autoprefixer 等） |

```javascript
// CSS 处理链
{
  test: /\.scss$/,
  use: [
    'style-loader',  // 3. 创建 style 标签注入 CSS
    'css-loader',    // 2. 解析 CSS 为 JS 模块
    'postcss-loader',// 1.5 添加浏览器前缀
    'sass-loader'    // 1. 编译 SCSS 为 CSS
  ]
}
```

### 2.3 资源文件相关

> Webpack 5 已内置 asset 模块，可替代 file-loader/url-loader/raw-loader

| Loader | 作用 | Webpack 5 替代方案 |
|--------|------|-------------------|
| `file-loader` | 复制文件到输出目录 | `type: 'asset/resource'` |
| `url-loader` | 小文件转 base64，大文件复制 | `type: 'asset'` |
| `raw-loader` | 以字符串形式导入文件 | `type: 'asset/source'` |

```javascript
// Webpack 5 资源处理
module: {
  rules: [
    {
      test: /\.(png|jpg|gif)$/,
      type: 'asset',
      parser: {
        dataUrlCondition: {
          maxSize: 8 * 1024 // 8kb 以下转 base64
        }
      },
      generator: {
        filename: 'images/[name].[contenthash:8][ext]'
      }
    }
  ]
}
```

### 2.4 其他常用 Loader

| Loader | 作用 |
|--------|------|
| `html-loader` | 处理 HTML 文件中的图片等资源 |
| `vue-loader` | 解析 Vue 单文件组件 |
| `markdown-loader` | 将 Markdown 转换为 HTML |
| `thread-loader` | **多线程打包**，将 loader 放在单独 worker 池中运行 |
| `cache-loader` | **缓存 loader 结果**到磁盘，提高二次构建速度 |

---

## 3. Loader 配置详解

### 基本配置

```javascript
module: {
  rules: [
    {
      // 匹配文件类型
      test: /\.css$/,
      
      // 使用 loader（字符串或数组）
      use: ['style-loader', 'css-loader'],
      
      // 排除的目录
      exclude: /node_modules/,
      
      // 只处理的目录
      include: path.resolve(__dirname, 'src'),
      
      // 执行顺序控制
      enforce: 'pre'  // 'pre'(优先) | 'normal'(默认) | 'post'(延后)
    }
  ]
}
```

### 带参数的 Loader 配置

```javascript
{
  test: /\.js$/,
  use: [
    {
      loader: 'babel-loader',
      options: {
        presets: ['@babel/preset-env'],
        plugins: ['@babel/plugin-proposal-class-properties']
      }
    }
  ]
}
```

---

## 4. Loader 执行顺序

### 默认执行顺序

- **从右到左**，**从下到上**（数组中）

```javascript
{
  test: /\.scss$/,
  use: ['style-loader', 'css-loader', 'sass-loader']
}
// 执行顺序：sass-loader → css-loader → style-loader
```

### enforce 控制顺序

```javascript
module: {
  rules: [
    {
      test: /\.js$/,
      enforce: 'pre',  // 在所有普通 loader 之前执行
      loader: 'eslint-loader'
    },
    {
      test: /\.js$/,
      loader: 'babel-loader'  // normal，默认
    },
    {
      test: /\.js$/,
      enforce: 'post',  // 在所有普通 loader 之后执行
      loader: 'some-loader'
    }
  ]
}
```

### 完整执行顺序

```
Pitching 阶段（从左到右）：
post-loader.pitch → inline-loader.pitch → normal-loader.pitch → pre-loader.pitch

Normal 阶段（从右到左）：
pre-loader → normal-loader → inline-loader → post-loader
```

---

## 5. 如何编写 Loader

### 5.1 Loader 基础结构

```javascript
// my-loader.js
module.exports = function(source) {
  // source: 源文件内容
  
  // 处理逻辑
  const result = source.replace(/console\.log\(.*\);?/g, '');
  
  // 返回处理结果
  return result;
};
```

### 5.2 使用 this.callback

```javascript
module.exports = function(source, sourceMap, meta) {
  // source: 源文件内容
  // sourceMap: 可选的 source map
  // meta: 可选的元数据
  
  const result = doSomething(source);
  
  // 返回多个值时使用 this.callback
  this.callback(null, result, sourceMap, meta);
  // 第一个参数为错误对象，无错误时为 null
};
```

### 5.3 Pitch Loader

```javascript
module.exports = function(source) {
  return source;
};

// Pitch 方法，在正常 loader 之前执行
module.exports.pitch = function(remainingRequest, precedingRequest, data) {
  console.log('Pitch 阶段执行');
  // 如果返回非 undefined，会短路后续 loader
};
```

### 5.4 使用工具库

```javascript
const { getOptions } = require('loader-utils');
const { validate } = require('schema-utils');

const schema = {
  type: 'object',
  properties: {
    name: { type: 'string' }
  }
};

module.exports = function(source) {
  // 获取 options
  const options = getOptions(this);
  
  // 校验参数
  validate(schema, options, { name: 'My Loader' });
  
  // 启用/禁用缓存
  this.cacheable && this.cacheable(true);
  
  return source;
};
```

---

## 6. Loader 与 Plugin 的区别

| 特性 | Loader | Plugin |
|------|--------|--------|
| **本质** | 函数，负责文件转换 | 类/对象，监听 webpack 事件 |
| **作用** | 将非 JS 文件转为 JS 模块 | 扩展 webpack 功能 |
| **配置** | `module.rules` | `plugins` 数组 |
| **执行时机** | 模块加载时 | 构建生命周期各阶段 |
| **职责** | 单一（文件转换） | 丰富多样（优化、压缩等） |

---

## 7. 性能优化技巧

### 7.1 缩小 Loader 搜索范围

```javascript
{
  test: /\.js$/,
  include: path.resolve(__dirname, 'src'),  // 只处理 src 目录
  exclude: /node_modules/,                   // 排除 node_modules
  loader: 'babel-loader'
}
```

### 7.2 开启缓存

```javascript
{
  test: /\.js$/,
  loader: 'babel-loader',
  options: {
    cacheDirectory: true  // 开启 babel-loader 缓存
  }
}
```

### 7.3 多线程打包

```javascript
{
  test: /\.js$/,
  use: [
    {
      loader: 'thread-loader',
      options: {
        workers: 2  // 开启 2 个 worker
      }
    },
    'babel-loader'
  ]
}
```

### 7.4 使用 OneOf

```javascript
module: {
  rules: [
    {
      oneOf: [
        { test: /\.css$/, use: ['style-loader', 'css-loader'] },
        { test: /\.scss$/, use: ['style-loader', 'css-loader', 'sass-loader'] },
        { test: /\.js$/, loader: 'babel-loader' }
      ]
    }
  ]
}
// 每个文件只会匹配 oneOf 中的一个 loader
```
