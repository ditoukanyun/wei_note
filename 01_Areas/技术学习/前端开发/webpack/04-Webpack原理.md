# Webpack 原理详解

## 1. Webpack 构建流程

### 1.1 整体流程

webpack 构建过程可以划分为三个阶段：

```
初始化阶段 → 构建阶段 → 生成阶段
```

#### 初始化阶段

1. **合并配置**：从配置文件、Shell 参数中读取并合并配置
2. **创建 Compiler**：使用配置初始化 Compiler 对象
3. **加载插件**：执行所有配置的插件的 `apply()` 方法
4. **确定入口**：根据 `entry` 配置找到所有入口文件

#### 构建阶段

1. **编译模块**：从入口文件开始，调用 Loader 转译模块
2. **解析依赖**：使用 Acorn 将代码转为 AST，分析模块依赖
3. **递归处理**：对依赖模块递归执行上述操作
4. **构建完成**：得到每个模块的转译后内容和依赖关系图

#### 生成阶段

1. **生成 Chunk**：根据入口和依赖关系，将模块组织成 Chunk
2. **代码转译**：处理 Chunk 代码（Tree Shaking、代码分割等）
3. **资源输出**：将 Chunk 转换为 Asset 资源
4. **写入文件**：根据输出配置，将资源写入文件系统

### 1.2 详细流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    初始化阶段                                 │
├─────────────────────────────────────────────────────────────┤
│ 1. 读取配置（webpack.config.js + CLI 参数）                   │
│ 2. 创建 Compiler 实例                                        │
│ 3. 执行 plugin.apply(compiler)                               │
│ 4. 解析 entry，创建 Dependency 对象                          │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    构建阶段（make）                           │
├─────────────────────────────────────────────────────────────┤
│ 1. 根据 Dependency 创建 Module 对象                          │
│ 2. 读取模块内容 → 调用 Loader 转译                            │
│ 3. 使用 Acorn 解析为 AST                                     │
│ 4. 遍历 AST 收集依赖                                         │
│ 5. 对依赖模块递归执行 1-4                                    │
│ 6. 构建 ModuleGraph（模块依赖图）                            │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    生成阶段（seal）                           │
├─────────────────────────────────────────────────────────────┤
│ 1. 根据 ModuleGraph 构建 ChunkGraph                          │
│ 2. 执行代码优化（Tree Shaking、Scope Hoisting）              │
│ 3. 生成 Chunk 代码                                           │
│ 4. 创建 Assets 资源                                          │
│ 5. 执行 emit 钩子                                            │
│ 6. 写入文件系统                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. HMR（热模块替换）原理

### 2.1 什么是 HMR

HMR（Hot Module Replacement）允许在运行时更新模块，而无需完全刷新页面。

### 2.2 工作流程

```
1. 启动 webpack-dev-server（WDS）
   ↓
2. WDS 注入 HMR 客户端代码到 bundle
   ↓
3. 浏览器加载页面，与 WDS 建立 WebSocket 连接
   ↓
4. 文件变化 → Webpack 增量构建 → 生成新的 hash
   ↓
5. WDS 通过 WebSocket 发送 hash 到浏览器
   ↓
6. 浏览器请求 manifest 文件获取变更范围
   ↓
7. 浏览器加载变更的模块
   ↓
8. 执行 module.hot.accept 回调，更新页面
```

### 2.3 核心概念

```javascript
// 启用 HMR
module.exports = {
  devServer: {
    hot: true  // 开启热更新
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin()
  ]
};

// 在代码中使用 HMR
if (module.hot) {
  module.hot.accept('./module.js', function() {
    // 模块更新时的回调
    console.log('模块已更新');
  });
}
```

### 2.4 HMR 的局限

- **入口文件**：不支持 HMR（因为入口文件变化会导致整个依赖树变化）
- **需要手动处理**：JS 文件默认不支持 HMR，需要编写 `module.hot.accept`
- **状态丢失**：更新后组件状态可能丢失（可配合 React Fast Refresh 解决）

---

## 3. Tree Shaking 原理

### 3.1 什么是 Tree Shaking

Tree Shaking 是一种基于 **ES Module** 规范的 **Dead Code Elimination**（死代码消除）技术，用于移除未使用的代码。

### 3.2 工作原理

```
标记阶段（seal）                    清除阶段（minimize）
    ↓                                    ↓
1. 分析模块导出                        1. Terser 删除标记的未使用代码
2. 标记哪些导出被使用                  2. 生成优化后的代码
3. 在依赖图中标记引用关系
```

### 3.3 开启条件

```javascript
// 必要条件：
// 1. 使用 ES Module（import/export）
// 2. 启用代码优化

module.exports = {
  mode: 'production',  // 自动启用
  // 或手动配置
  optimization: {
    usedExports: true,  // 标记未使用的导出
    minimize: true      // 压缩代码
  }
};
```

### 3.4 副作用处理

```javascript
// package.json
{
  "sideEffects": false
  // 或指定有副作用的文件
  "sideEffects": [
    "*.css",
    "*.scss"
  ]
}
```

### 3.5 优化技巧

```javascript
// ✅ 推荐：细粒度导出
export const add = (a, b) => a + b;
export const sub = (a, b) => a - b;

// ❌ 不推荐：默认导出对象
export default {
  add: (a, b) => a + b,
  sub: (a, b) => a - b
};

// ✅ 使用 #__PURE__ 标记纯函数
const result = /*#__PURE__*/ pureFunction();
```

---

## 4. Scope Hoisting（作用域提升）

### 4.1 什么是 Scope Hoisting

将符合条件的多个模块合并到同一个函数作用域中，减少函数声明和闭包，优化代码体积。

### 4.2 开启方式

```javascript
module.exports = {
  mode: 'production',  // 自动启用
  // 或手动配置
  optimization: {
    concatenateModules: true
  }
};
```

### 4.3 效果对比

```javascript
// 开启前（每个模块一个函数）
(function(module, exports) {
  module.exports = 'hello';
})(module1, exports1);

(function(module, exports) {
  var msg = require('./msg');
  console.log(msg);
})(module2, exports2);

// 开启后（合并为一个函数）
(function() {
  var msg = 'hello';
  console.log(msg);
})();
```

---

## 5. 代码分割（Code Splitting）

### 5.1 分割方式

| 方式 | 配置 | 场景 |
|------|------|------|
| 多入口 | `entry: {a,b}` | 多页面应用 |
| 动态导入 | `import()` | 路由懒加载 |
| SplitChunks | `optimization.splitChunks` | 提取公共代码 |

### 5.2 SplitChunks 配置

```javascript
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',  // 对所有 chunk 生效
      minSize: 20000, // 最小分割大小（20KB）
      minChunks: 1,   // 最少被引用次数
      maxAsyncRequests: 30,
      maxInitialRequests: 30,
      cacheGroups: {
        // 提取第三方库
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10  // 优先级
        },
        // 提取公共代码
        common: {
          minChunks: 2,
          chunks: 'all',
          enforce: true
        }
      }
    }
  }
};
```

### 5.3 动态导入

```javascript
// 路由懒加载
const Home = () => import(/* webpackChunkName: 'home' */ './Home.vue');

// 点击加载
button.addEventListener('click', () => {
  import(/* webpackPrefetch: true */ './modal.js').then(module => {
    module.showModal();
  });
});
```

---

## 6. 模块联邦（Module Federation）

### 6.1 什么是 Module Federation

Webpack 5 引入的新特性，允许多个独立构建的应用共享模块。

### 6.2 配置示例

```javascript
// 主应用（Host）
const { ModuleFederationPlugin } = require('webpack').container;

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      remotes: {
        // 远程应用别名: '远程应用名@远程地址'
        app1: 'app1@http://localhost:3001/remoteEntry.js'
      },
      shared: ['react', 'react-dom']  // 共享依赖
    })
  ]
};

// 远程应用（Remote）
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'app1',
      filename: 'remoteEntry.js',
      exposes: {
        // 暴露的模块
        './Button': './src/Button.js'
      },
      shared: ['react', 'react-dom']
    })
  ]
};

// 使用远程模块
import('app1/Button').then(Button => {
  // 使用 Button
});
```

---

## 7. Webpack 5 新特性

### 7.1 持久化缓存

```javascript
module.exports = {
  cache: {
    type: 'filesystem',  // 使用文件系统缓存
    buildDependencies: {
      config: [__filename]  // 配置文件变更时使缓存失效
    }
  }
};
```

### 7.2 Asset Modules

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.(png|jpg)$/,
        type: 'asset',  // 替代 url-loader
        parser: {
          dataUrlCondition: {
            maxSize: 8 * 1024
          }
        }
      }
    ]
  }
};
```

### 7.3 其他改进

- **Top Level Await**：支持顶层 await
- **Tree Shaking 增强**：支持嵌套模块的 Tree Shaking
- **更好的 Long Term Caching**：优化的 chunk id 和 module id 生成

---

## 8. 性能优化总结

### 8.1 构建速度优化

| 优化项 | 配置 | 效果 |
|--------|------|------|
| 持久化缓存 | `cache: { type: 'filesystem' }` | 二次构建速度提升 70%+ |
| 多线程打包 | `thread-loader` | 适合大型项目 |
| 缩小搜索范围 | `include/exclude` | 减少文件匹配 |
| DllPlugin | 预编译第三方库 | 减少重复编译 |
| 升级 Node/Webpack | 使用最新版本 | 利用新特性优化 |

### 8.2 产物体积优化

| 优化项 | 配置 | 效果 |
|--------|------|------|
| Tree Shaking | `usedExports: true` | 移除无用代码 |
| Scope Hoisting | `concatenateModules: true` | 合并模块作用域 |
| 代码分割 | `splitChunks` | 按需加载 |
| 压缩代码 | `minimize: true` | 减少体积 |
| CDN 引入 | `externals` | 排除第三方库 |

### 8.3 运行时性能优化

| 优化项 | 配置 | 效果 |
|--------|------|------|
| 懒加载 | `import()` | 减少首屏加载 |
| 预加载 | `webpackPrefetch` | 提前加载资源 |
| HTTP 缓存 | `contenthash` | 利用浏览器缓存 |
| Gzip 压缩 | `compression-webpack-plugin` | 减少传输体积 |
