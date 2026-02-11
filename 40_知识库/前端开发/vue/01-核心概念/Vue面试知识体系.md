# Vue 面试知识点体系

> 基于掘金文章《2024前端高频面试题之--VUE篇》整理
> 结合个人学习笔记，形成完整知识体系

---

## 📋 目录

1. [[#Vue 基础概念|Vue 基础概念]]
2. [[#Vue 实例与生命周期|Vue 实例与生命周期]]
3. [[#响应式原理|响应式原理]]
4. [[#虚拟 DOM 与 Diff 算法|虚拟 DOM 与 Diff 算法]]
5. [[#组件化开发|组件化开发]]
6. [[#组件通信方式|组件通信方式]]
7. [[#计算属性与侦听器|计算属性与侦听器]]
8. [[#Vue Router|Vue Router]]
9. [[#Vuex 状态管理|Vuex 状态管理]]
10. [[#性能优化|性能优化]]
11. [[#Vue2 vs Vue3|Vue2 vs Vue3]]

---

## Vue 基础概念

### MVVM 架构模式

```
Model（数据模型）←→ ViewModel（视图模型）←→ View（视图/DOM）
```

- **Model**: 数据模型层，负责数据存储和业务逻辑
- **View**: 视图层，负责 UI 展示
- **ViewModel**: 桥梁，实现数据双向绑定
  - 数据变化 → 自动更新视图
  - 视图操作 → 自动更新数据

> 💡 Vue 使用 MVVM 模式，通过数据劫持 + 发布订阅实现响应式

### Vue 核心特性

| 特性 | 说明 |
|------|------|
| 响应式数据绑定 | 数据变化自动更新 DOM |
| 组件化开发 | 可复用的独立组件 |
| 虚拟 DOM | 高效的 DOM 更新机制 |
| 指令系统 | v-if, v-for, v-model 等 |
| 单文件组件 | .vue 文件结构 |

---

## Vue 实例与生命周期

### 生命周期钩子函数

```
beforeCreate → created → beforeMount → mounted → 
beforeUpdate → updated → beforeDestroy → destroyed
```

#### 创建阶段

| 钩子 | 触发时机 | 可访问数据 |
|------|----------|-----------|
| `beforeCreate` | 实例初始化后，数据观测前 | ❌ 无法访问 data、methods |
| `created` | 实例创建完成，数据观测完成 | ✅ 可访问 data、methods，❌ 无法访问 DOM |

#### 挂载阶段

| 钩子 | 触发时机 | 特点 |
|------|----------|------|
| `beforeMount` | 挂载开始前，render 首次调用 | 虚拟 DOM 已创建，即将渲染 |
| `mounted` | 挂载完成，真实 DOM 已生成 | ✅ 可访问 DOM，可进行 AJAX 请求 |

#### 更新阶段

| 钩子 | 触发时机 | 注意事项 |
|------|----------|----------|
| `beforeUpdate` | 数据更新后，DOM 重新渲染前 | 可在此修改数据，不会触发重渲染 |
| `updated` | 视图更新完成后 | ⚠️ 避免在此期间修改数据，防止无限循环 |

#### 销毁阶段

| 钩子 | 触发时机 | 用途 |
|------|----------|------|
| `beforeDestroy` | 实例销毁前 | 清理定时器、取消订阅、解绑事件 |
| `destroyed` | 实例销毁后 | 只剩 DOM 空壳，组件完全拆解 |

### 特殊生命周期

- `activated`: keep-alive 组件激活时调用
- `deactivated`: keep-alive 组件停用时调用
- `errorCaptured`: 捕获子孙组件错误时调用

### 生命周期执行顺序（父子组件）

```
父 beforeCreate → 父 created → 父 beforeMount → 
子 beforeCreate → 子 created → 子 beforeMount → 子 mounted → 
父 mounted
```

---

## 响应式原理

### Vue2 响应式实现

```javascript
// Object.defineProperty 实现数据劫持
Object.defineProperty(obj, key, {
  enumerable: true,
  configurable: true,
  get() {
    // 依赖收集
    if (Dep.target) {
      dep.addSub(Dep.target)
    }
    return val
  },
  set(newVal) {
    if (val === newVal) return
    val = newVal
    // 通知更新
    dep.notify()
  }
})
```

#### 核心流程

1. **Observer**: 遍历数据对象，使用 `Object.defineProperty` 设置 getter/setter
2. **Dep**: 依赖收集器，为每个属性收集 Watcher
3. **Watcher**: 订阅者，数据变化时执行回调

#### 数组响应式处理

```javascript
// 重写数组方法
const arrayProto = Array.prototype
const arrayMethods = Object.create(arrayProto)

;['push', 'pop', 'shift', 'unshift', 'splice', 'sort', 'reverse'].forEach(method => {
  const original = arrayProto[method]
  Object.defineProperty(arrayMethods, method, {
    value: function mutator(...args) {
      const result = original.apply(this, args)
      const ob = this.__ob__
      ob.dep.notify()  // 通知更新
      return result
    }
  })
})
```

### Vue3 响应式实现

```javascript
// 使用 Proxy
const proxy = new Proxy(target, {
  get(target, key, receiver) {
    const result = Reflect.get(target, key, receiver)
    track(target, key)  // 依赖收集
    return result
  },
  set(target, key, value, receiver) {
    const result = Reflect.set(target, key, value, receiver)
    trigger(target, key)  // 触发更新
    return result
  }
})
```

#### Proxy 优势

| 特性 | Object.defineProperty | Proxy |
|------|---------------------|-------|
| 监听属性 | 需预先定义 | 动态添加/删除属性 |
| 监听数组 | 需重写方法 | 原生支持 |
| 嵌套对象 | 递归遍历 | 懒代理（使用时才代理） |
| 性能 | 较低 | 更高 |

---

## 虚拟 DOM 与 Diff 算法

### 虚拟 DOM (Virtual DOM)

```javascript
// VNode 结构示例
const vnode = {
  tag: 'div',
  props: { id: 'app', class: 'container' },
  children: [
    { tag: 'h1', props: {}, children: 'Hello' },
    { tag: 'p', props: {}, children: 'World' }
  ],
  key: undefined,
  text: undefined,
  elm: undefined  // 对应的真实 DOM
}
```

#### 为什么需要虚拟 DOM

1. **跨平台**: VNode 是平台无关的，可渲染到浏览器、Native、小程序等
2. **性能优化**: 减少直接操作 DOM 的频率
3. **批量更新**: 合并多次 DOM 操作

### Diff 算法

#### 核心策略

```
1. 同级比较，不跨级比较
2. 同类型节点才深度比较
3. 使用 key 优化列表更新
```

#### Diff 流程

```javascript
// 双端比较
function updateChildren(parentElm, oldCh, newCh) {
  let oldStartIdx = 0
  let newStartIdx = 0
  let oldEndIdx = oldCh.length - 1
  let newEndIdx = newCh.length - 1
  let oldStartVnode = oldCh[0]
  let oldEndVnode = oldCh[oldEndIdx]
  let newStartVnode = newCh[0]
  let newEndVnode = newCh[newEndIdx]
  
  while (oldStartIdx <= oldEndIdx && newStartIdx <= newEndIdx) {
    // 1. 旧头 === 新头
    if (sameVnode(oldStartVnode, newStartVnode)) {
      patchVnode(oldStartVnode, newStartVnode)
      oldStartVnode = oldCh[++oldStartIdx]
      newStartVnode = newCh[++newStartIdx]
    }
    // 2. 旧尾 === 新尾
    else if (sameVnode(oldEndVnode, newEndVnode)) {
      patchVnode(oldEndVnode, newEndVnode)
      oldEndVnode = oldCh[--oldEndIdx]
      newEndVnode = newCh[--newEndIdx]
    }
    // 3. 旧头 === 新尾（移动操作）
    else if (sameVnode(oldStartVnode, newEndVnode)) {
      patchVnode(oldStartVnode, newEndVnode)
      moveNode(parentElm, oldStartVnode.elm, oldEndVnode.elm.nextSibling)
      oldStartVnode = oldCh[++oldStartIdx]
      newEndVnode = newCh[--newEndIdx]
    }
    // 4. 旧尾 === 新头（移动操作）
    else if (sameVnode(oldEndVnode, newStartVnode)) {
      patchVnode(oldEndVnode, newStartVnode)
      moveNode(parentElm, oldEndVnode.elm, oldStartVnode.elm)
      oldEndVnode = oldCh[--oldEndIdx]
      newStartVnode = newCh[++newStartIdx]
    }
    // 5. 都不匹配，使用 key 查找
    else {
      // 通过 key 在旧节点中查找
      const idxInOld = findIdxInOld(newStartVnode, oldCh, oldStartIdx, oldEndIdx)
      if (isUndef(idxInOld)) {
        // 未找到，创建新节点
        createElm(newStartVnode)
      } else {
        // 找到，复用并移动
        const vnodeToMove = oldCh[idxInOld]
        patchVnode(vnodeToMove, newStartVnode)
        oldCh[idxInOld] = undefined
        moveNode(parentElm, vnodeToMove.elm, oldStartVnode.elm)
      }
      newStartVnode = newCh[++newStartIdx]
    }
  }
  
  // 处理剩余节点
  if (oldStartIdx > oldEndIdx) {
    // 新增节点
    addVnodes(parentElm, newCh, newStartIdx, newEndIdx)
  } else if (newStartIdx > newEndIdx) {
    // 删除节点
    removeVnodes(oldCh, oldStartIdx, oldEndIdx)
  }
}
```

#### Key 的作用

> [!important] Key 的重要性
> - 帮助 Vue 识别哪些元素被修改、添加或删除
> - 使用 key 时，Vue 基于 key 而不是位置进行元素复用
> - 列表渲染必须提供 key，且 key 应该是唯一且稳定的

**错误示例：**
```javascript
// ❌ 使用 index 作为 key
<li v-for="(item, index) in list" :key="index">{{ item.name }}</li>
```

**正确示例：**
```javascript
// ✅ 使用唯一 id 作为 key
<li v-for="item in list" :key="item.id">{{ item.name }}</li>
```

---

## 组件化开发

### 组件定义方式

```javascript
// 全局注册
Vue.component('my-component', {
  template: '<div>全局组件</div>',
  data() {
    return {}
  }
})

// 局部注册
const MyComponent = {
  template: '<div>局部组件</div>',
  data() {
    return {}
  }
}

export default {
  components: { MyComponent }
}
```

### 单文件组件 (.vue)

```vue
<template>
  <div class="example">{{ msg }}</div>
</template>

<script>
export default {
  name: 'Example',
  data() {
    return {
      msg: 'Hello Vue'
    }
  },
  methods: {},
  computed: {},
  watch: {}
}
</script>

<style scoped>
.example { color: red; }
</style>
```

### 组件的 data 必须是函数

```javascript
// ❌ 错误：使用对象
export default {
  data: {
    count: 0
  }
}

// ✅ 正确：使用函数
export default {
  data() {
    return {
      count: 0
    }
  }
}
```

> [!note] 原因
> 组件复用时，data 如果是对象，所有实例共享同一数据；
> data 是函数时，每个实例返回独立的数据对象。

### v-if vs v-show

| 特性 | v-if | v-show |
|------|------|--------|
| 渲染方式 | 条件为 false 时不渲染 DOM | 始终渲染 DOM，通过 display 控制 |
| 切换开销 | 高（创建/销毁组件） | 低（仅切换 CSS） |
| 适用场景 | 条件很少改变 | 需要频繁切换显示/隐藏 |
| 初始渲染 | 条件为 false 时无 DOM | 始终有 DOM |

### 动态组件与异步组件

```vue
<template>
  <div>
    <!-- 动态组件 -->
    <component :is="currentComponent"></component>
    
    <!-- 异步组件 -->
    <AsyncComponent />
  </div>
</template>

<script>
export default {
  components: {
    // 局部注册异步组件
    AsyncComponent: () => import('./AsyncComponent.vue')
  },
  data() {
    return {
      currentComponent: 'Home'
    }
  }
}
</script>
```

### 缓存组件 keep-alive

```vue
<template>
  <keep-alive :include="['Home', 'List']" :exclude="['Detail']">
    <component :is="currentView"></component>
  </keep-alive>
</template>
```

**属性：**
- `include`: 字符串或正则，名称匹配的组件会被缓存
- `exclude`: 字符串或正则，名称匹配的组件不会被缓存
- `max`: 数字，最多缓存多少组件实例（LRU 策略）

**生命周期：**
- `activated`: 组件被激活时调用
- `deactivated`: 组件被停用时调用

---

## 组件通信方式

### 父子组件通信

#### Props / $emit（推荐）

```vue
<!-- 父组件 -->
<template>
  <Child :message="parentMsg" @update="handleUpdate" />
</template>

<!-- 子组件 -->
<script>
export default {
  props: {
    message: {
      type: String,
      required: true,
      default: ''
    }
  },
  methods: {
    sendToParent() {
      this.$emit('update', '新数据')
    }
  }
}
</script>
```

#### $parent / $children

```javascript
// 子组件访问父组件
this.$parent.someMethod()

// 父组件访问子组件
this.$children[0].someMethod()
```

> [!warning] 不建议使用
> 耦合度高，难以追踪数据来源，Vue3 中已移除 $children

#### $refs

```vue
<template>
  <Child ref="childRef" />
</template>

<script>
export default {
  mounted() {
    // 访问子组件
    this.$refs.childRef.someMethod()
    // 访问 DOM 元素
    this.$refs.inputRef.focus()
  }
}
</script>
```

### 跨级组件通信

#### provide / inject

```javascript
// 祖先组件
export default {
  provide() {
    return {
      getMap: this.getMap,
      userInfo: this.userInfo
    }
  }
}

// 后代组件
export default {
  inject: ['getMap', 'userInfo'],
  mounted() {
    console.log(this.userInfo)
  }
}
```

#### $attrs / $listeners

```javascript
// 父组件
<Child :foo="foo" :bar="bar" @click="handleClick" />

// 子组件（中间层）
<GrandChild v-bind="$attrs" v-on="$listeners" />

// 孙组件
export default {
  mounted() {
    console.log(this.$attrs.foo)  // 访问 foo
    this.$emit('click')  // 触发父组件事件
  }
}
```

### 全局通信

#### Event Bus（Vue2）

```javascript
// eventBus.js
import Vue from 'vue'
export default new Vue()

// 组件 A
import bus from './eventBus.js'
bus.$emit('event-name', data)

// 组件 B
import bus from './eventBus.js'
bus.$on('event-name', (data) => {
  console.log(data)
})
```

> [!tip] Vue3 替代方案
> Vue3 中移除了 $on/$off/$once，可使用 mitt 库替代

---

## 计算属性与侦听器

### computed vs watch

| 特性 | computed | watch |
|------|----------|-------|
| 缓存 | ✅ 有缓存 | ❌ 无缓存 |
| 异步支持 | ❌ 不支持 | ✅ 支持 |
| 使用场景 | 根据已有数据派生新数据 | 数据变化时执行操作 |
| 返回值 | 必须有返回值 | 无需返回值 |
| 监听对象 | 多对一（多个依赖） | 一对一（单个数据） |

### computed 实现原理

```javascript
// 简化版实现
class Watcher {
  constructor(vm, getter, options) {
    this.vm = vm
    this.getter = getter
    this.lazy = options.lazy  // 懒执行
    this.dirty = this.lazy    // 脏数据标记
    this.value = this.lazy ? undefined : this.get()
  }
  
  get() {
    // 依赖收集
    pushTarget(this)
    const value = this.getter.call(this.vm)
    popTarget()
    return value
  }
  
  evaluate() {
    this.value = this.get()
    this.dirty = false  // 计算后标记为干净
  }
  
  update() {
    if (this.lazy) {
      this.dirty = true  // 标记为脏数据，下次访问时重新计算
    } else {
      this.run()
    }
  }
}

// 创建计算属性
function defineComputed(vm, key, userDef) {
  const getter = typeof userDef === 'function' ? userDef : userDef.get
  
  Object.defineProperty(vm, key, {
    get: createComputedGetter(key),
    set: userDef.set || noop
  })
}

function createComputedGetter(key) {
  return function computedGetter() {
    const watcher = this._computedWatchers[key]
    if (watcher.dirty) {
      watcher.evaluate()  // 只有脏数据时才重新计算
    }
    if (Dep.target) {
      watcher.depend()  // 收集依赖
    }
    return watcher.value
  }
}
```

### watch 使用方式

```javascript
export default {
  data() {
    return {
      message: '',
      obj: { nested: { value: '' } }
    }
  },
  watch: {
    // 基础用法
    message(newVal, oldVal) {
      console.log(newVal, oldVal)
    },
    
    // 对象写法
    message: {
      handler(newVal, oldVal) {
        console.log(newVal)
      },
      immediate: true,  // 立即执行
      deep: true        // 深度监听
    },
    
    // 监听对象属性
    'obj.nested.value'(newVal) {
      console.log(newVal)
    },
    
    // 数组方式
    message: [
      function handler1(val) {},
      function handler2(val) {}
    ]
  }
}
```

---

## Vue Router

### 路由模式

| 模式 | 原理 | 特点 | 适用场景 |
|------|------|------|----------|
| hash | location.hash | # 后有变化，不发送服务器 | 不需要 SEO |
| history | pushState/replaceState | URL 美观，需服务端支持 | 需要 SEO |
| abstract | 内存 history | 非浏览器环境 | SSR/原生应用 |

### 路由配置

```javascript
const router = new VueRouter({
  mode: 'history',
  base: '/app/',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: { requiresAuth: true }
    },
    {
      path: '/user/:id',
      component: User,
      children: [
        { path: '', component: UserHome },
        { path: 'profile', component: UserProfile }
      ]
    },
    {
      path: '/about',
      component: About,
      beforeEnter: (to, from, next) => {
        // 路由独享守卫
        next()
      }
    },
    {
      path: '*',
      component: NotFound
    }
  ]
})
```

### 导航守卫

```javascript
// 全局前置守卫
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next('/login')
  } else {
    next()
  }
})

// 全局解析守卫
router.beforeResolve((to, from, next) => {
  next()
})

// 全局后置钩子
router.afterEach((to, from) => {
  // 无 next，不能阻止导航
})

// 组件内守卫
export default {
  beforeRouteEnter(to, from, next) {
    // 组件实例未创建，不能访问 this
    next(vm => {
      // 通过回调访问组件实例
    })
  },
  beforeRouteUpdate(to, from, next) {
    // 当前路由改变但组件复用时
    next()
  },
  beforeRouteLeave(to, from, next) {
    // 离开当前路由时
    next()
  }
}
```

### 导航流程

```
1. 导航被触发
2. 调用 beforeRouteLeave（组件内）
3. 调用 beforeEach（全局）
4. 调用 beforeRouteUpdate（组件内，复用组件时）
5. 调用 beforeEnter（路由独享）
6. 解析异步路由组件
7. 调用 beforeRouteEnter（组件内）
8. 调用 beforeResolve（全局）
9. 导航被确认
10. 调用 afterEach（全局）
11. DOM 更新
12. 触发 beforeRouteEnter 的 next 回调
```

---

## Vuex 状态管理

### 核心概念

```javascript
const store = new Vuex.Store({
  state: {
    count: 0,
    todos: []
  },
  
  getters: {
    doneTodos: state => {
      return state.todos.filter(todo => todo.done)
    },
    doneTodosCount: (state, getters) => {
      return getters.doneTodos.length
    }
  },
  
  mutations: {
    increment(state, payload) {
      state.count += payload.amount
    }
  },
  
  actions: {
    incrementAsync({ commit }, payload) {
      setTimeout(() => {
        commit('increment', payload)
      }, 1000)
    }
  },
  
  modules: {
    cart: {
      namespaced: true,
      state: () => ({ items: [] }),
      mutations: {
        addItem(state, item) {
          state.items.push(item)
        }
      }
    }
  }
})
```

### State 响应式原理

```javascript
// Vuex 内部使用 Vue 实例实现响应式
function resetStoreVM(store, state) {
  store.getters = {}
  const wrappedGetters = store._wrappedGetters
  const computed = {}
  
  forEachValue(wrappedGetters, (fn, key) => {
    computed[key] = partial(fn, store)
    Object.defineProperty(store.getters, key, {
      get: () => store._vm[key],
      enumerable: true
    })
  })
  
  store._vm = new Vue({
    data: { $$state: state },
    computed
  })
}
```

### 辅助函数

```javascript
import { mapState, mapGetters, mapMutations, mapActions } from 'vuex'

export default {
  computed: {
    // 数组形式
    ...mapState(['count', 'todos']),
    
    // 对象形式
    ...mapState({
      count: state => state.count,
      aliasCount: 'count'
    }),
    
    // 命名空间
    ...mapGetters('cart', ['cartItems'])
  },
  
  methods: {
    ...mapMutations(['increment']),
    ...mapActions(['incrementAsync']),
    
    // 命名空间写法
    ...mapMutations('cart', ['addItem'])
  }
}
```

---

## 性能优化

### 编码阶段优化

| 优化项 | 说明 |
|--------|------|
| v-if vs v-show | 频繁切换用 v-show，条件渲染用 v-if |
| v-for 使用 key | 提供稳定的唯一 key |
| 避免 v-if 与 v-for 同时使用 | v-for 优先级更高 |
| 事件代理 | 大量元素绑事件时使用 |
| keep-alive | 缓存频繁切换的组件 |
| 路由懒加载 | `() => import('./Component.vue')` |
| 异步组件 | 需要时才加载 |
| 防抖/节流 | 频繁触发的事件处理 |
| Object.freeze | 冻结不需要响应式的大数据 |

### 首屏加载优化

```javascript
// 1. 路由懒加载
const Home = () => import(/* webpackChunkName: "home" */ './views/Home.vue')

// 2. 组件异步加载
components: {
  AsyncComponent: () => ({
    component: import('./AsyncComponent.vue'),
    loading: LoadingComponent,
    error: ErrorComponent,
    delay: 200,
    timeout: 3000
  })
}

// 3. 按需引入第三方库
import { Button, Select } from 'element-ui'
```

### 打包优化

| 优化项 | 配置 |
|--------|------|
| 代码分割 | splitChunks |
| Tree Shaking | 生产模式自动开启 |
| Gzip | nginx 配置 |
| CDN | externals 配置 |
| 图片压缩 | image-webpack-loader |

### 运行时优化

```javascript
// 1. 大数据列表 - 虚拟滚动
<virtual-list :size="50" :remain="10" :items="largeList">
  <template #default="{ item }">
    <div>{{ item.name }}</div>
  </template>
</virtual-list>

// 2. 图片懒加载
<img v-lazy="imageUrl" />

// 3. 函数式组件（无状态组件）
export default {
  functional: true,
  render(h, context) {
    return h('div', context.props.text)
  }
}
```

---

## Vue2 vs Vue3

### 主要区别

| 特性 | Vue2 | Vue3 |
|------|------|------|
| API 风格 | Options API | Options API + Composition API |
| 响应式 | Object.defineProperty | Proxy |
| TypeScript | 支持 | 完全重写，更好的 TS 支持 |
| 模板根节点 | 必须单根 | 允许多根（Fragments） |
| 性能 | 优秀 | 更小、更快（树摇优化） |
| 生命周期 | 8 个 | 调整，setup 替代 beforeCreate/created |
| 组件通信 | $on/$off/$once | 移除，使用 provide/inject 或 mitt |
| Filter | 支持 | 移除 |
| Teleport | 无 | 内置 |
| Suspense | 无 | 内置 |

### Composition API

```javascript
// Vue3
import { ref, reactive, computed, watch, onMounted } from 'vue'

export default {
  setup() {
    // 响应式数据
    const count = ref(0)
    const state = reactive({ name: 'Vue' })
    
    // 计算属性
    const doubleCount = computed(() => count.value * 2)
    
    // 侦听器
    watch(count, (newVal, oldVal) => {
      console.log(newVal)
    })
    
    // 方法
    const increment = () => {
      count.value++
    }
    
    // 生命周期
    onMounted(() => {
      console.log('mounted')
    })
    
    return {
      count,
      state,
      doubleCount,
      increment
    }
  }
}
```

### Vue3 新特性

```javascript
// 1. Teleport - 将组件渲染到 DOM 其他位置
<teleport to="body">
  <div class="modal">Modal content</div>
</teleport>

// 2. Suspense - 异步组件加载状态
<suspense>
  <template #default>
    <AsyncComponent />
  </template>
  <template #fallback>
    <div>Loading...</div>
  </template>
</suspense>

// 3. 多根节点
<template>
  <header>...</header>
  <main>...</main>
  <footer>...</footer>
</template>
```

---

## 其他重要知识点

### v-model 原理

```javascript
// v-model 是语法糖
<input v-model="message">

// 等价于
<input 
  :value="message" 
  @input="message = $event.target.value"
>

// 自定义组件 v-model
export default {
  props: ['value'],
  model: {
    prop: 'value',
    event: 'input'
  },
  methods: {
    updateValue(val) {
      this.$emit('input', val)
    }
  }
}

// Vue3 中 v-model 变更
// v-model:title="title"
// 等价于 :title="title" @update:title="title = $event"
```

### nextTick

```javascript
// 在下次 DOM 更新循环结束后执行回调
this.message = 'updated'
this.$nextTick(() => {
  // DOM 已更新
  console.log(this.$el.textContent)
})

// 实现原理
function nextTick(callback) {
  return Promise.resolve().then(callback)
  // 或使用 MutationObserver / setImmediate / setTimeout
}
```

### 插槽 (Slot)

```vue
<!-- 默认插槽 -->
<Child>默认内容</Child>

<!-- 具名插槽 -->
<Child>
  <template #header>头部</template>
  <template #default>主体</template>
  <template #footer>底部</template>
</Child>

<!-- 作用域插槽 -->
<Child v-slot="{ user }">
  {{ user.name }}
</Child>

<!-- 子组件定义 -->
<template>
  <div>
    <slot name="header"></slot>
    <slot :user="user"></slot>
    <slot name="footer"></slot>
  </div>
</template>
```

### Mixin 混入

```javascript
// 定义 mixin
const myMixin = {
  data() {
    return { mixinData: 'Hello' }
  },
  created() {
    console.log('mixin created')
  },
  methods: {
    mixinMethod() {}
  }
}

// 使用 mixin
export default {
  mixins: [myMixin],
  created() {
    console.log('component created')
    // 输出顺序: mixin created -> component created
  }
}

// 合并规则
// 1. 数据对象：递归合并，组件优先
// 2. 生命周期钩子：合并成数组，依次调用
// 3. 方法：组件方法覆盖 mixin 方法
```

### 指令修饰符

```vue
<!-- 事件修饰符 -->
<form @submit.prevent="onSubmit">
<a @click.stop="doThis">
<div @click.capture="doThis">
<div @click.self="doThis">
<div @click.once="doThis">
<div @scroll.passive="onScroll">

<!-- 按键修饰符 -->
<input @keyup.enter="submit">
<input @keyup.13="submit">
<input @keyup.ctrl.enter="submit">

<!-- 表单修饰符 -->
<input v-model.lazy="msg">
<input v-model.number="age">
<input v-model.trim="msg">
```

---

## 面试题汇总

### 高频面试题

1. **Vue 响应式原理是什么？**
   - Vue2: Object.defineProperty + 发布订阅模式
   - Vue3: Proxy + Reflect

2. **v-if 和 v-show 的区别？**
   - v-if 条件渲染，切换时组件销毁/重建
   - v-show 通过 display 控制，组件始终存在

3. **computed 和 watch 的区别？**
   - computed 有缓存，适用于计算值
   - watch 无缓存，适用于监听变化执行操作

4. **Vue 组件 data 为什么必须是函数？**
   - 保证每个组件实例有独立的数据对象

5. **key 的作用是什么？**
   - 帮助 diff 算法识别节点，优化列表更新性能

6. **Vue Router 导航守卫有哪些？**
   - 全局：beforeEach、beforeResolve、afterEach
   - 路由独享：beforeEnter
   - 组件内：beforeRouteEnter、beforeRouteUpdate、beforeRouteLeave

7. **Vuex 的 mutation 和 action 区别？**
   - mutation：同步，直接修改 state
   - action：可异步，通过 commit 调用 mutation

8. **Vue 生命周期钩子执行顺序？**
   - 创建 → 挂载 → 更新 → 销毁
   - 父子组件：父 beforeCreate → 父 created → 父 beforeMount → 子创建 → 子挂载 → 父 mounted

9. **nextTick 的作用？**
   - 在下次 DOM 更新循环结束后执行回调

10. **Vue2 和 Vue3 的主要区别？**
    - Composition API、Proxy 响应式、更好的 TS 支持、性能优化

---

## 相关链接

- [[response|响应式原理详解]]
- [[VDOM|虚拟 DOM 与 Diff 算法]]
- [[component|组件通信详解]]
- [[live|生命周期详解]]
- [[important|Vue 重点知识]]
- [[source-live|源码：生命周期]]
- [[source-computed|源码：Computed]]
- [[source-watch|源码：Watch]]
- [[source-patch|源码：Patch]]
- [[source-router|源码：Vue Router]]
- [[source-vuex|源码：Vuex]]
