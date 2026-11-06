---
type: reference
created: 2026-11-06
updated: 2026-11-06
area: "[[后端开发]]"
tags: [ZooKeeper, Watch, 事件监听]
---
# 05 Watch 机制

> Watch 是 ZooKeeper 最容易被误用的功能。它看起来像「事件订阅」，实际语义是「一次性通知」。本章讲清楚它保证什么、不保证什么，以及本项目的重注册实现为什么长那样。

## 本章解决什么问题

三个高频疑问：

1. 注册了监听，为什么只收到一次事件？
2. 为什么改子节点的数据，父节点的监听没反应？
3. 为什么代码里重注册要丢到另一个线程？

答案分别对应：一次性语义、监听粒度、事件线程模型。

---

## 结论先行

| 问题 | 答案 |
| --- | --- |
| watch 触发几次 | 一次。触发后自动失效，要用就重新注册 |
| 能监听子节点的数据变化吗 | 不能。父节点的 children watch 只关心「子节点列表变了」 |
| 事件会丢吗 | 会话内重连会补发；会话过期则 watch 全部失效 |
| 多次变化会收到多次事件吗 | 不保证。一次注册最多一个事件，中间变化可能被合并 |
| 回调里能直接查 ZK 吗 | 能，但不要。回调跑在单线程事件线程上，阻塞它会拖住所有事件 |
| 生产上建议手写 watch 吗 | 不建议，优先用 Curator 的 `TreeCache` / `PathChildrenCache` |

---

## 1. 为什么需要 watch

没有 watch 时，想知道节点有没有变，只能轮询：

```text
每 100ms 查一次 → 99% 的请求是无用功，且变化仍有最多 100ms 延迟
```

watch 的思路是「先登记，变了再通知我」：

```text
客户端：我关注 /config/db-url，变了叫我
服务端：记下了
...（可能很久以后）
服务端：/config/db-url 变了
```

代价是服务端要为每个会话维护 watch 列表，所以 ZK 对 watch 数量有隐式约束，设计上也选择「一次性」来限制状态规模。

---

## 2. 一次性语义

**一次 watch 注册 = 最多收到一次通知。**

```
注册 watch → 节点变化 → 收到事件 → watch 失效
                              ↓
                     想继续监听？重新注册
```

这不是 bug，是刻意的设计：

- 服务端不用为每个客户端维护长期订阅状态；
- 客户端每次收到事件后，可以重新读一次数据、重新决定是否继续关注；
- 避免「客户端已经不需要了但服务端还在推」的泄漏。

本项目的做法是**在回调里自动重新注册**，让调用方感觉像持续监听（`service/ZkWatchService.java:64-68`、`:85-92`）。

---

## 3. 三种注册入口与触发矩阵

ZK 有三个 API 可以顺带注册 watch，它们关注的事件不同：

| 注册方式 | 关注节点 | 触发事件 |
| --- | --- | --- |
| `exists(path, watch)` | 节点是否存在 | `NodeCreated`、`NodeDeleted`、`NodeDataChanged` |
| `getData(path, watch)` | 节点数据 | `NodeDeleted`、`NodeDataChanged` |
| `getChildren(path, watch)` | 子节点列表 | `NodeChildrenChanged`、`NodeDeleted` |

矩阵形式：

| 发生的变化 | exists watch | getData watch | getChildren watch |
| --- | --- | --- | --- |
| 节点被创建 | ✅ `NodeCreated` | —（注册不了） | —（注册不了） |
| 节点数据被修改 | ✅ `NodeDataChanged` | ✅ `NodeDataChanged` | ❌ |
| 子节点增删 | ❌ | ❌ | ✅ `NodeChildrenChanged` |
| 节点被删除 | ✅ `NodeDeleted` | ✅ `NodeDeleted` | ✅ `NodeDeleted` |

### 3.1 最容易踩的坑

**监听父节点，收不到子节点数据的变化。**

```
watch /users          → 子节点 u001 的 data 变了 → 没有事件
watch /users/u001     → u001 的 data 变了        → NodeDataChanged
```

因为父节点的 watch 只覆盖「子节点列表」，不覆盖子节点的内容。要监听子节点数据，必须对每个子节点单独注册。

### 3.2 本项目的组合

`watch(path)` 一次注册两类监听（`service/ZkWatchService.java:55-61`）：

- `checkExists` 的 watch：覆盖创建 / 删除 / 数据变更；
- `getChildren` 的 watch：覆盖子节点增删。

这样对一个路径，创建、删除、改数据、加子节点都能看到。

---

## 4. 事件类型

`Watcher.Event.EventType`：

| 类型 | 含义 |
| --- | --- |
| `None` | 不是节点事件，通常是连接状态变化（配合 `KeeperState` 使用） |
| `NodeCreated` | 监听的节点被创建 |
| `NodeDeleted` | 被删除 |
| `NodeDataChanged` | 数据变化（包括 `setData` 写入相同内容） |
| `NodeChildrenChanged` | 子节点列表变化（增或删） |

注意 `None`：会话状态变化也会走 watcher 回调。本项目在 `record` 里把它当作普通事件记录下来，你能在事件列表里看到 `state=SyncConnected` 这类信息（`service/ZkWatchService.java:104-109`）。

---

## 5. ZooKeeper 的三条保证与三条不保证

### 5.1 保证

1. **事件有序**：watch 事件相对于其他事件、其他 watch、异步响应是有序的。
2. **先事件后数据**：客户端会先看到 watch 事件，再看到对应的新数据。
3. **会话内补发**：断线重连且会话未过期时，挂起的事件会被补发。

### 5.2 不保证

1. **不保证每次变化一个事件**：从注册到触发之间的多次修改，可能只产生一个事件。事件只告诉你「变了」，不告诉你「变了几次、变成什么」——所以收到事件后必须**重新读数据**。
2. **不保证跨会话保留**：会话过期后，所有 watch 失效。重连后必须重新注册，并做一次全量同步（因为期间的变化你已经错过了）。
3. **不保证实时**：事件从服务端到客户端有网络延迟，不构成任何时限承诺。

### 5.3 由此得出的正确用法

```
收到事件
  → 不要假设事件里带着新值（它只有类型和路径）
  → 重新 getData / getChildren
  → 根据最新状态做业务
  → 重新注册 watch
```

---

## 6. 事件线程：为什么重注册要换个线程

### 6.1 回调运行在哪

ZooKeeper 客户端内部有一个专门的 **EventThread**，所有 watcher 回调都在这一条线程上串行执行。这意味着：

- 回调 A 阻塞，回调 B、C、D 全部排队；
- 回调里做耗时的网络请求、数据库查询，会拖慢整个客户端的事件处理；
- 在 Curator 的连接状态监听里做重入的同步调用，某些场景下会死锁。

### 6.2 本项目的做法

```java
private final ExecutorService reRegisterExecutor = Executors.newSingleThreadExecutor(r -> {
    Thread t = new Thread(r, "zk-watch-reregister");
    t.setDaemon(true);
    return t;
});
```

`service/ZkWatchService.java:45-49`。

回调只做两件事：记录事件、把「重新注册」投递给这个线程池：

```java
Watcher watcher = event -> {
    record(event, path);
    reRegisterExecutor.execute(() -> registerExists(path));
};
```

`service/ZkWatchService.java:64-68`。

于是 EventThread 立刻返回去处理下一个事件，真正的 ZK 调用在 `zk-watch-reregister` 线程上同步执行。

**为什么用单线程池而不是多线程**：同一路径的重复注册需要串行化，避免并发注册出多份 watch。

### 6.3 这条规则的通用版本

> **在事件回调里只做「记下来 + 投递」，不要在回调里做业务。**

适用于：ZK watcher、Curator `ConnectionStateListener`、Netty handler、前端 `MutationObserver`……凡是由框架单线程分发的回调，都遵循这个原则。

---

## 7. 本项目的实现细节

### 7.1 exists 监听

```java
private void registerExists(String path) {
    Watcher watcher = event -> {
        record(event, path);
        reRegisterExecutor.execute(() -> registerExists(path));
    };
    try {
        Stat stat = client.checkExists().usingWatcher(watcher).forPath(path);
        if (stat != null) {
            registerChildrenIfNeeded(path);
        }
    } catch (Exception e) {
        record(new WatchEventRecord(..., "REGISTER_FAILED", describe(e)));
    }
}
```

`service/ZkWatchService.java:64-78`。

注意 `stat != null` 这一段：如果注册时节点已经存在，顺便把 children 监听也挂上；如果节点还不存在，就等 `NodeCreated` 事件触发后，重新注册时再挂。

### 7.2 children 监听与去重

```java
private void registerChildrenIfNeeded(String path) {
    if (childrenArmed.putIfAbsent(path, Boolean.TRUE) != null) {
        return;
    }
    Watcher watcher = event -> {
        childrenArmed.remove(path);
        if (event.getType() == Watcher.Event.EventType.NodeChildrenChanged) {
            record(event, path);
        }
        reRegisterExecutor.execute(() -> registerChildrenIfNeeded(path));
    };
    ...
}
```

`service/ZkWatchService.java:81-102`。

三个设计点：

**① `childrenArmed` 防重复注册**

每次 `getChildren().usingWatcher(...)` 都会在服务端登记一份新 watch。如果同一路径登记了两份，一次变化会收到两个事件。`putIfAbsent` 保证每个路径最多一份。

**② 只记录 `NodeChildrenChanged`**

节点被删除时，exists 监听和 children 监听会同时收到 `NodeDeleted`。如果两边都记录，事件列表里会出现两条一模一样的删除事件。所以 children 监听只记录「子节点变化」，删除交给 exists 监听（`:87-90`）。

**③ 删除后能自愈**

节点被删 → children 监听触发 → 重新注册时 `getChildren` 抛 `NoNodeException` → 清掉 `childrenArmed`，等 exists 监听的 `NodeCreated` 再把它挂回来（`:95-97`）。

### 7.3 事件列表的容量

```java
private static final int MAX_EVENTS = 200;
...
events.addFirst(record);
while (events.size() > MAX_EVENTS) {
    events.pollLast();
}
```

`service/ZkWatchService.java:39,111-116`。

新事件插到队头，超过 200 条从队尾丢弃，避免长时间运行后内存无限增长。

---

## 8. 羊群效应（herd effect）

假设 1000 个客户端都监听同一个节点，等它变化后去抢活：

```
节点变化 → 服务端向 1000 个客户端推送 → 1000 个客户端同时读 ZK / 同时抢锁
```

这就是羊群效应，会把一次变化放大成一次流量尖峰。

ZK 本身没有内置去抖，解决方案在**监听粒度**上：

- 分布式锁：每个等待者只监听自己的**前一个节点**，一次释放只唤醒一个人（见下一篇）；
- 配置变更：用 Curator `TreeCache`，它在客户端合并事件，只对外抛一次「缓存变了」；
- 大规模服务发现：不要给每个实例单独 watch 全量列表，改用推送 + 本地缓存 + 定期全量对齐。

---

## 9. 生产环境：优先用 Curator Cache

手写 watch 的三个负担：

1. 重注册逻辑；
2. 断线重连后的全量同步；
3. 并发控制和去重。

Curator 提供了现成的：

| 组件 | 维护的内容 | 适用 |
| --- | --- | --- |
| `NodeCache` | 单个节点的数据 | 配置项热更新 |
| `PathChildrenCache` | 直接子节点列表 + 每个子节点数据 | 服务发现 |
| `TreeCache` | 整棵子树 | 目录型配置、权限树 |

它们内部处理了重注册、重连同步和事件合并。本项目的 `ZkWatchService` 是为了**教学**把过程摊开，真实项目不建议照抄。

---

## 10. 动手实验

打开页面「Watch 监听」页签，或直接用 curl。

### 第一步：注册

```bash
B=http://localhost:8088/api/zk
curl -s -X POST "$B/watch?path=/learn-zk/demo/users"
```

### 第二步：造事件

```bash
# 1. 创建子节点 → 父节点收到 NodeChildrenChanged
curl -s -X POST $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/demo/users/u999","data":"hello"}'

# 2. 改子节点数据 → 父节点没有任何事件（监听粒度！）
curl -s -X PUT $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/demo/users/u999","data":"world"}'

# 3. 给子节点单独注册监听，再改一次 → NodeDataChanged
curl -s -X POST "$B/watch?path=/learn-zk/demo/users/u999"
curl -s -X PUT $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/demo/users/u999","data":"again"}'

# 4. 删除子节点 → 子节点 NodeDeleted + 父节点 NodeChildrenChanged
curl -s -X DELETE "$B/nodes?path=/learn-zk/demo/users/u999"
```

### 第三步：看事件

```bash
curl -s $B/events
```

你应该看到类似：

```
NodeChildrenChanged  /learn-zk/demo/users
NodeDataChanged      /learn-zk/demo/users/u999
NodeDeleted          /learn-zk/demo/users/u999
NodeChildrenChanged  /learn-zk/demo/users
```

清空：

```bash
curl -s -X DELETE $B/events
```

### 第四步：验证「一次性」

只注册一次、只造一次变化，事件列表里只会出现一条；但再变一次，仍然会有新事件——因为代码在回调里重新注册了。把 `reRegisterExecutor.execute(...)` 那行注释掉再试，就只会收到第一条。

---

## 11. 自检

1. 一次 watch 注册能收到几次事件？
2. 监听父节点，能收到子节点数据变化吗？为什么？
3. 为什么 `NodeDeleted` 只在 exists 监听里记录一次？
4. 会话过期后，之前的 watch 还在吗？
5. 为什么重注册要放到独立线程？

参考：2、3.1、7.2、5.2、6。

---

## 12. 延伸阅读

- ZooKeeper watch 官方说明：<https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#ch_zkWatches>
- Curator Cache：<https://curator.apache.org/docs/>

下一篇：[`06-distributed-lock.md`](06-distributed-lock.md)
