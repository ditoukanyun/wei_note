---
title: React 性能优化完全指南
description: 从编译阶段到运行时的全方位 React 性能优化策略，包含 Vercel 最佳实践和现代 React 模式
date: 2026-02-10
tags:
  - react
  - performance
  - optimization
  - frontend
category: 前端开发
status: completed
reference:
  - https://juejin.cn/post/6908895801116721160
  - https://vercel.com/engineering/react-best-practices
---

# React 性能优化完全指南

React 性能优化是构建高性能前端应用的核心技能。本文从**编译阶段** → **构建阶段** → **路由阶段** → **渲染阶段** → **状态管理** → **大数据处理**六个维度，系统性地梳理 React 性能优化的核心策略和实战技巧。

## 一、编译与构建阶段优化

### 1.1 Webpack 构建优化

在实际项目中，随着代码量增加，构建时间和打包体积会迅速膨胀。以下是关键的构建优化策略：

#### 1.1.1 限制 Loader 范围

```js
{
    test: /\.jsx?$/,
    exclude: /node_modules/,  // 排除 node_modules
    include: path.resolve(__dirname, '../src'),  // 只处理 src 目录
    use: ['babel-loader?cacheDirectory=true']  // 启用缓存
}
```

#### 1.1.2 多进程编译（HappyPack/Thread-loader）

```js
const HappyPack = require('happypack');

// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        use: 'happypack/loader?id=babel'
      }
    ]
  },
  plugins: [
    new HappyPack({
      id: 'babel',
      loaders: ['babel-loader?cacheDirectory=true'],
      threads: 4  // 使用4个线程
    })
  ]
};
```

#### 1.1.3 Tree Shaking 移除冗余代码

确保使用 ES6 模块语法并配置正确的 `sideEffects`：

```json
// package.json
{
  "sideEffects": [
    "*.css",
    "*.scss",
    "*.less"
  ]
}
```

### 1.2 UI 库按需加载

使用 Ant Design 等 UI 库时，按需引入可以显著减小打包体积：

**优化前：**
```js
import { Button, Input } from 'antd';  // 引入整个库
```

**优化后：**
```js
// .babelrc 配置
{
  "plugins": [
    ["import", {
      "libraryName": "antd",
      "libraryDirectory": "es",
      "style": true
    }]
  ]
}

// 业务代码
import Button from 'antd/es/button';
import Input from 'antd/es/input';
```

### 1.3 现代构建工具推荐

> [!tip] 推荐使用
> - **Vite**: 原生 ESM，启动速度极快
> - **Turbopack**: Next.js 官方支持，Webpack 的继任者
> - **SWC**: Rust 编写的编译器，比 Babel 快 20 倍

---

## 二、路由阶段优化

### 2.1 路由懒加载

对于大型应用，一次性加载所有路由会导致首屏加载缓慢。使用 `React.lazy` 和动态导入实现按需加载：

```jsx
import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// 路由懒加载
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/dashboard/*" element={<Dashboard />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

### 2.2 高级路由懒加载 HOC

如果需要更细粒度的路由控制（如路由守卫、加载状态监听），可以封装一个高阶组件：

```jsx
import React, { Component } from 'react';

const routerObserveQueue = []; /* 存放路由守卫钩子 */

export const RouterHooks = {
  beforeRouterComponentLoad(callback) {
    routerObserveQueue.push({ type: 'before', callback });
  },
  afterRouterComponentDidLoaded(callback) {
    routerObserveQueue.push({ type: 'after', callback });
  }
};

export default function AsyncRouter(loadRouter) {
  return class AsyncComponent extends Component {
    state = { Component: null };

    componentDidMount() {
      this.dispatchRouterQueue('before');
      
      loadRouter()
        .then(module => module.default)
        .then(Component => {
          this.setState({ Component }, () => {
            this.dispatchRouterQueue('after');
          });
        });
    }

    dispatchRouterQueue(type) {
      const { history } = this.props;
      routerObserveQueue.forEach(item => {
        if (item.type === type) item.callback(history);
      });
    }

    render() {
      const { Component } = this.state;
      return Component ? <Component {...this.props} /> : null;
    }
  };
}

// 使用方式
const Detail = AsyncRouter(() => import('./pages/Detail'));

// 添加路由监听
RouterHooks.beforeRouterComponentLoad((history) => {
  console.log('路由加载前:', history.location.pathname);
  // 可以在这里做权限验证、埋点等
});
```

### 2.3 预加载路由

利用浏览器的空闲时间预加载可能访问的路由：

```jsx
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import(/* webpackPrefetch: true */ './pages/About'));
// ^ webpackPrefetch 会在浏览器空闲时自动预加载
```

---

## 三、渲染阶段优化（核心）

### 3.1 组件颗粒化与职责分离

#### 问题场景

当父组件包含受控组件时，每次输入都会触发整个父组件重新渲染：

```jsx
// ❌ 不推荐：所有子组件都会因 input 更新而重新渲染
function Parent() {
  const [inputValue, setInputValue] = useState('');
  
  return (
    <div>
      <ChildA />
      <ChildB />
      <ChildC />
      <input 
        value={inputValue} 
        onChange={e => setInputValue(e.target.value)} 
      />
    </div>
  );
}
```

#### 解决方案

将受控组件封装为独立单元：

```jsx
// ✅ 推荐：独立的状态管理
const ControlledInput = React.memo(({ onChange }) => {
  const [value, setValue] = useState('');
  
  const handleChange = useCallback((e) => {
    const newValue = e.target.value;
    setValue(newValue);
    onChange?.(newValue);
  }, [onChange]);

  return <input value={value} onChange={handleChange} />;
});

function Parent() {
  const formData = useRef({});
  
  return (
    <div>
      <ChildA />
      <ChildB />
      <ChildC />
      <ControlledInput 
        onChange={value => { formData.current.inputValue = value; }} 
      />
    </div>
  );
}
```

### 3.2 独立的数据请求单元

将数据请求逻辑封装在独立的组件中，避免不必要的级联渲染：

```jsx
// ❌ 不推荐：所有数据在一个组件中请求
function Page() {
  const [dataA, setDataA] = useState(null);
  const [dataB, setDataB] = useState(null);
  const [dataC, setDataC] = useState(null);

  useEffect(() => {
    Promise.all([
      fetchDataA().then(setDataA),
      fetchDataB().then(setDataB),
      fetchDataC().then(setDataC)
    ]);
  }, []);

  return (
    <div>
      <SectionA data={dataA} />
      <SectionB data={dataB} />
      <SectionC data={dataC} />
    </div>
  );
}
```

```jsx
// ✅ 推荐：每个组件独立管理自己的数据
function DataSectionA() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchDataA().then(setData);
  }, []);
  
  return <SectionA data={data} />;
}

function DataSectionB() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchDataB().then(setData);
  }, []);
  
  return <SectionB data={data} />;
}

function Page() {
  return (
    <div>
      <DataSectionA />
      <DataSectionB />
      <DataSectionC />
    </div>
  );
}
```

### 3.3 React.memo 和 PureComponent

#### PureComponent（类组件）

```jsx
// 自动进行浅比较
class MyComponent extends React.PureComponent {
  render() {
    console.log('render');
    return <div>{this.props.data.name}</div>;
  }
}

// ❌ 注意：深层对象变更不会被检测到
const data = { user: { name: 'John' } };
<MyComponent data={data} />
// 修改 data.user.name 不会触发重新渲染
```

#### React.memo（函数组件）

```jsx
const MyComponent = React.memo(({ data }) => {
  console.log('render');
  return <div>{data.name}</div>;
}, (prevProps, nextProps) => {
  // 自定义比较函数，返回 true 表示不重新渲染
  return prevProps.data.id === nextProps.data.id;
});
```

### 3.4 shouldComponentUpdate

类组件中精确控制渲染：

```jsx
class MyComponent extends React.Component {
  shouldComponentUpdate(nextProps, nextState) {
    // 只在特定状态变化时更新
    return nextState.data !== this.state.data;
  }
}
```

### 3.5 useMemo 与 useCallback

#### useMemo：缓存计算结果

```jsx
function ProductList({ products, filter }) {
  const filteredProducts = useMemo(() => {
    console.log('过滤计算...');
    return products.filter(p => 
      p.name.toLowerCase().includes(filter.toLowerCase())
    );
  }, [products, filter]);

  return (
    <ul>
      {filteredProducts.map(product => (
        <ProductItem key={product.id} product={product} />
      ))}
    </ul>
  );
}
```

#### useCallback：缓存函数引用

```jsx
function Parent() {
  const [count, setCount] = useState(0);
  
  // ❌ 每次渲染都创建新函数
  const handleClick = () => {
    console.log('clicked');
  };
  
  // ✅ 缓存函数，配合 memo 使用
  const handleClickMemoized = useCallback(() => {
    console.log('clicked');
  }, []);
  
  return (
    <div>
      <Child onClick={handleClickMemoized} />
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
    </div>
  );
}

const Child = React.memo(({ onClick }) => {
  console.log('Child render');
  return <button onClick={onClick}>Click me</button>;
});
```

> [!warning] 注意事项
> 不要滥用 useMemo/useCallback，对于简单的计算，直接使用可能更有性能（没有缓存开销）

---

## 四、避免不必要的渲染

### 4.1 批量更新（Batching）

React 18 自动批处理所有状态更新：

```jsx
function App() {
  const [count, setCount] = useState(0);
  const [flag, setFlag] = useState(false);

  const handleClick = () => {
    // React 18：自动批处理为一次渲染
    setCount(c => c + 1);
    setFlag(f => !f);
  };

  return <button onClick={handleClick}>Update</button>;
}
```

在 React 17 或异步代码中手动批处理：

```jsx
import { unstable_batchedUpdates } from 'react-dom';

const handleAsyncUpdate = () => {
  Promise.resolve().then(() => {
    unstable_batchedUpdates(() => {
      setCount(c => c + 1);
      setFlag(f => !f);
    });
  });
};
```

### 4.2 状态合并

```jsx
// ❌ 多次 setState
const handleUpdate = () => {
  setLoading(true);
  fetchData().then(data => {
    setLoading(false);
    setData(data);
    setError(null);
  });
};

// ✅ 合并为单次更新
const handleUpdate = () => {
  setLoading(true);
  fetchData().then(data => {
    setState(prev => ({
      ...prev,
      loading: false,
      data,
      error: null
    }));
  });
};
```

### 4.3 使用 useRef 缓存非响应式数据

对于不需要触发渲染的数据，使用 ref 而不是 state：

```jsx
function Timer() {
  const [displayTime, setDisplayTime] = useState(0);
  const actualTime = useRef(0);  // 不需要触发渲染
  const timerId = useRef(null);

  useEffect(() => {
    timerId.current = setInterval(() => {
      actualTime.current += 1;
      // 每秒只更新一次显示
      if (actualTime.current % 1 === 0) {
        setDisplayTime(actualTime.current);
      }
    }, 100);

    return () => clearInterval(timerId.current);
  }, []);

  return <div>{displayTime}</div>;
}
```

### 4.4 正确使用 key

```jsx
// ❌ 错误：使用 index 作为 key
{items.map((item, index) => (
  <ListItem key={index} {...item} />
))}

// ✅ 正确：使用唯一标识
{items.map(item => (
  <ListItem key={item.id} {...item} />
))}
```

> [!danger] 使用 index 作为 key 的问题
> 1. 列表重新排序时性能差
> 2. 组件状态可能错乱
> 3. 动画效果异常

---

## 五、状态管理优化

### 5.1 何时使用状态管理

状态管理应该用于：
- ✅ 跨层级共享的**全局状态**
- ✅ 多个组件依赖的**公共数据**
- ✅ 需要**持久化**的会话状态

不应将以下数据放入状态管理：
- ❌ 仅在单个组件内使用的局部状态
- ❌ 可从其他状态派生的计算值
- ❌ 频繁更新的临时数据（如表单输入）

### 5.2 合理的状态结构

```jsx
// ❌ 嵌套过深，难以更新
const state = {
  user: {
    profile: {
      info: {
        name: ''
      }
    }
  }
};

// ✅ 扁平化结构
const state = {
  user: {
    id: '',
    name: '',
    email: ''
  },
  profile: {
    userId: '',
    avatar: ''
  }
};
```

### 5.3 使用选择器优化

```jsx
// ❌ 每次返回新对象，导致不必要的重渲染
const mapStateToProps = (state) => ({
  user: {
    name: state.user.name,
    email: state.user.email
  }
});

// ✅ 使用记忆化选择器
import { createSelector } from 'reselect';

const getUser = state => state.user;
const getUserInfo = createSelector(
  [getUser],
  (user) => ({
    name: user.name,
    email: user.email
  })
);
```

---

## 六、大数据量渲染优化

### 6.1 虚拟列表

对于长列表，只渲染可见区域的内容：

```jsx
import { FixedSizeList as List } from 'react-window';

function VirtualizedList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      {items[index].name}
    </div>
  );

  return (
    <List
      height={500}
      itemCount={items.length}
      itemSize={35}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

### 6.2 时间分片

对于大数据量的 DOM 操作，使用 `requestIdleCallback` 或 `setTimeout` 分片执行：

```jsx
function TimeSlicing({ data }) {
  const [displayData, setDisplayData] = useState([]);
  const CHUNK_SIZE = 100;

  useEffect(() => {
    let index = 0;
    
    const renderChunk = () => {
      const chunk = data.slice(index, index + CHUNK_SIZE);
      setDisplayData(prev => [...prev, ...chunk]);
      index += CHUNK_SIZE;
      
      if (index < data.length) {
        requestIdleCallback(renderChunk, { timeout: 100 });
      }
    };

    renderChunk();
  }, [data]);

  return (
    <div>
      {displayData.map((item, i) => (
        <div key={i}>{item}</div>
      ))}
    </div>
  );
}
```

### 6.3 React 18 Concurrent Features

```jsx
import { useTransition, useDeferredValue } from 'react';

function SearchResults() {
  const [isPending, startTransition] = useTransition();
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);

  const handleChange = (e) => {
    // 紧急更新：输入框
    setQuery(e.target.value);
    
    // 过渡更新：搜索结果
    startTransition(() => {
      performSearch(e.target.value);
    });
  };

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <span>Loading...</span>}
      <SearchResultsList query={deferredQuery} />
    </>
  );
}
```

---

## 七、代码分割与懒加载

### 7.1 组件级懒加载

```jsx
const HeavyChart = lazy(() => import('./HeavyChart'));
const RichEditor = lazy(() => import('./RichEditor'));

function Dashboard() {
  return (
    <div>
      <Suspense fallback={<Skeleton />}>
        <HeavyChart />
      </Suspense>
      <Suspense fallback={<Skeleton />}>
        <RichEditor />
      </Suspense>
    </div>
  );
}
```

### 7.2 动态导入工具函数

```jsx
async function exportReport() {
  // 只在需要时加载导出库
  const { exportToExcel } = await import('./excelExport');
  exportToExcel(data);
}
```

---

## 八、JavaScript 性能优化

### 8.1 避免内联函数

```jsx
// ❌ 每次渲染创建新函数
function Component() {
  return <button onClick={() => handleClick()}>Click</button>;
}

// ✅ 使用 useCallback 或直接引用
function Component() {
  const handleClick = useCallback(() => {
    // 处理逻辑
  }, []);
  
  return <button onClick={handleClick}>Click</button>;
}
```

### 8.2 数据预处理

```jsx
// ❌ 在渲染中重复计算
function List({ items }) {
  return (
    <ul>
      {items
        .filter(item => item.active)
        .sort((a, b) => b.score - a.score)
        .map(item => <Item key={item.id} {...item} />)
      }
    </ul>
  );
}

// ✅ 使用 useMemo 缓存
function List({ items }) {
  const processedItems = useMemo(() => {
    return items
      .filter(item => item.active)
      .sort((a, b) => b.score - a.score);
  }, [items]);

  return (
    <ul>
      {processedItems.map(item => <Item key={item.id} {...item} />)}
    </ul>
  );
}
```

### 8.3 使用 Set/Map 优化查找

```jsx
// ❌ O(n) 查找
const hasPermission = permissions.includes('admin');

// ✅ O(1) 查找
const permissionSet = new Set(permissions);
const hasPermission = permissionSet.has('admin');
```

---

## 九、现代 React 模式（React 18+）

### 9.1 Suspense 与数据获取

```jsx
import { Suspense, use } from 'react';

function Profile() {
  const user = use(fetchUser());  // React 18.3+ 实验性功能
  return <div>{user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Profile />
    </Suspense>
  );
}
```

### 9.2 Server Components（Next.js）

```jsx
// Server Component - 零客户端 JS
async function ProductList() {
  const products = await db.products.findAll();
  
  return (
    <div>
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

---

## 十、性能检测工具

### 10.1 React DevTools Profiler

```jsx
// 使用 Profiler API
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
  console.log('Component:', id);
  console.log('Phase:', phase);
  console.log('Duration:', actualDuration);
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Layout />
    </Profiler>
  );
}
```

### 10.2 Web Vitals

```jsx
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function reportWebVitals(metric) {
  console.log(metric);
}

getCLS(reportWebVitals);
getFID(reportWebVitals);
getFCP(reportWebVitals);
getLCP(reportWebVitals);
getTTFB(reportWebVitals);
```

### 10.3 性能优化检查清单

| 类别 | 检查项 | 优先级 |
|------|--------|--------|
| 构建 | 使用代码分割 | P0 |
| 构建 | 启用 Tree Shaking | P0 |
| 渲染 | 正确使用 key | P0 |
| 渲染 | 使用 React.memo/PureComponent | P1 |
| 渲染 | 使用 useMemo/useCallback | P1 |
| 状态 | 状态扁平化 | P1 |
| 网络 | 路由懒加载 | P0 |
| 网络 | 数据请求优化 | P1 |
| 大数据 | 虚拟列表 | P0 |
| 大数据 | 时间分片 | P1 |

---

## 总结

React 性能优化是一个系统工程，需要从构建、路由、渲染、状态管理等多个维度综合考虑。核心原则包括：

1. **减少不必要的渲染** - 使用 memo、useMemo、useCallback
2. **优化构建产物** - 代码分割、懒加载、Tree Shaking
3. **合理组织状态** - 避免过度状态管理，扁平化状态结构
4. **大数据量优化** - 虚拟列表、时间分片
5. **利用现代 React 特性** - Concurrent Mode、Suspense、Server Components

## 参考资源

- [React 官方文档 - 性能优化](https://react.dev/learn/thinking-in-react)
- [Vercel Engineering - React Best Practices](https://vercel.com/engineering/react-best-practices)
- [React 18 并发特性](https://react.dev/blog/2022/03/29/react-v18)
- [Web Vitals](https://web.dev/vitals/)
