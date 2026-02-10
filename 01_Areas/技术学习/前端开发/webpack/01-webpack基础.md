# Webpack 基础

## 1. Webpack 是什么？

Webpack 是一种用于构建 JavaScript 应用程序的**静态模块打包器(module bundler)**，它能够以一种相对一致且开放的处理方式，加载应用中的所有资源文件（图片、CSS、视频、字体文件等），并将其合并打包成浏览器兼容的 Web 资源文件。

### 核心功能

- **模块打包**：通过打包整合不同的模块文件保证各模块之间的引用和执行
- **代码编译**：通过丰富的 `loader` 可以将不同格式文件如 `.sass/.vue/.jsx` 转译为浏览器可以执行的文件
- **扩展功能**：通过社区丰富的 `plugin` 可以实现多种强大的功能，例如代码分割、代码混淆、代码压缩、按需加载等

---

## 2. 核心概念

### Entry（入口）

指定 webpack 打包入口文件，webpack 从入口文件开始构建依赖关系图。

```javascript
// 单入口
entry: './src/index.js',

// 多入口
entry: {
  index: './src/index.js',
  main: './src/main.js'
},

// 数组形式（用于 HMR）
entry: ['./src/index.js', './src/main.js']
```

### Output（出口）

指定 bundle 的输出位置和文件名。

```javascript
output: {
  // 输出文件名
  filename: 'js/[name].[contenthash:8].js',
  // 输出目录
  path: path.resolve(__dirname, 'dist'),
  // 公共路径（CDN 配置）
  publicPath: '/',
  // 动态导入 chunk 文件名
  chunkFilename: 'js/[name]_chunk.js'
}
```

### Mode（模式）

指定 webpack 打包模式，影响默认优化策略。

```javascript
mode: 'development'  // 或 'production' | 'none'
```

| 模式 | 特点 |
|------|------|
| `development` | 开发模式，启用调试，不压缩代码，启用热更新 |
| `production` | 生产模式，自动压缩代码，启用 Tree Shaking 等优化 |
| `none` | 不启用任何默认优化 |

---

## 3. 配置文件结构

```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  // 入口
  entry: './src/index.js',
  
  // 出口
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  },
  
  // 模块处理
  module: {
    rules: [
      // loader 配置
    ]
  },
  
  // 插件
  plugins: [
    // 插件实例
  ],
  
  // 模式
  mode: 'development',
  
  // 开发服务器
  devServer: {
    // 服务器配置
  },
  
  // 解析配置
  resolve: {
    // 模块解析规则
  },
  
  // 优化配置
  optimization: {
    // 优化选项
  }
};
```

---

## 4. 开发环境配置

### DevServer

```javascript
devServer: {
  // 服务器根目录
  static: {
    directory: path.join(__dirname, 'dist'),
  },
  // 端口号
  port: 8080,
  // 自动打开浏览器
  open: true,
  // 启用热更新
  hot: true,
  // 启用 gzip 压缩
  compress: true,
  // 代理配置
  proxy: {
    '/api': {
      target: 'http://localhost:3000',
      pathRewrite: { '^/api': '' }
    }
  }
}
```

### Source Map

```javascript
// 开发环境推荐
devtool: 'eval-cheap-module-source-map'

// 生产环境推荐
devtool: 'hidden-source-map'
```

| 模式 | 特点 |
|------|------|
| `eval` | 速度最快，但不适合生产环境 |
| `cheap-source-map` | 较快，只能定位到行 |
| `source-map` | 完整 source map，适合生产环境 |
| `hidden-source-map` | 不添加引用注释，用于生产调试 |

---

## 5. 文件指纹（Hash）

文件指纹用于版本管理和缓存控制。

### 三种 Hash 类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `[hash]` | 每次构建生成的唯一 hash | 不推荐 |
| `[chunkhash]` | 根据 chunk 生成，同 chunk 内文件 hash 相同 | JS 文件 |
| `[contenthash]` | 根据文件内容生成 | CSS 文件（推荐） |

### 配置示例

```javascript
output: {
  filename: 'js/[name].[chunkhash:8].js',
  chunkFilename: 'js/[name].[chunkhash:8].js'
}

// CSS 使用 contenthash
new MiniCssExtractPlugin({
  filename: 'css/[name].[contenthash:8].css'
})
```

---

## 6. 多环境配置

使用 `webpack-merge` 分离不同环境的配置：

```javascript
// webpack.common.js - 公共配置
module.exports = {
  entry: './src/index.js',
  // ...
};

// webpack.dev.js - 开发配置
const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'development',
  devtool: 'eval-source-map',
  // ...
});

// webpack.prod.js - 生产配置
const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'production',
  // ...
});
```

---

## 7. 常用 npm scripts

```json
{
  "scripts": {
    "dev": "webpack serve --config webpack.dev.js",
    "build": "webpack --config webpack.prod.js",
    "build:analyze": "webpack --config webpack.prod.js --analyze"
  }
}
```
