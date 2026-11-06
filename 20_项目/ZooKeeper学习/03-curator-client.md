---
type: reference
created: 2026-11-06
updated: 2026-11-06
area: "[[后端开发]]"
tags: [ZooKeeper, Curator, Java, 客户端]
---
# 03 Curator 客户端

> 上一章讲的是服务端。这一章讲客户端：为什么不用 ZooKeeper 原生 API？连接参数每一项在管什么？断线重连时到底发生了什么？

## 本章解决什么问题

原生 ZooKeeper 客户端能用，但直接写业务会遇到一堆重复劳动：重连、重试、watch 重注册、临时节点在 LOST 状态下的处理……Curator 把这些封装掉，并额外提供了「recipe」（分布式锁、选主、缓存等现成组件）。

本章只讲本项目实际用到的部分：连接管理 + 重试 + 状态机 + namespace。

---

## 结论先行

| 问题 | 答案 |
| --- | --- |
| 为什么用 Curator | 内置重连/重试/watch 管理，提供 `InterProcessMutex` 等成熟 recipe，避免手写坑 |
| 一个应用建几个客户端 | 一个，`CuratorFramework` 是线程安全的 |
| `sessionTimeout` 管什么 | 会话多久没心跳算过期；决定临时节点和锁的「故障发现延迟」 |
| `connectionTimeout` 管什么 | 建立 TCP 连接等多久；本项目用它做启动阻塞上限 |
| namespace 是什么 | **纯客户端路径前缀**，服务端数据仍在完整路径下 |
| 连接断了数据会丢吗 | 会话内重连不丢；会话过期（LOST）才会丢临时节点和 watch |

---

## 1. 原生 API 的五个坑

先看不用 Curator 时要自己处理什么：

| 坑 | 具体表现 | Curator 的做法 |
| --- | --- | --- |
| 重连 | `CONNECTIONLOSS` 后要自己重建连接、恢复 watch | 内置 `ConnectionStateManager`，自动重连 |
| 重试 | 哪些错误可重试、退避多久、重试几次 | `RetryPolicy` 统一配置 |
| watch 一次性 | 每次触发都要重新注册，且不能在事件线程里做重活 | recipe / Cache 帮你管理 |
| 临时节点状态 | 重连期间不确定自己是否还持有临时节点 | `ConnectionStateListener` + recipe 处理 |
| 分布式锁 | 临时顺序节点 + 前驱监听的逻辑要自己写对 | `InterProcessMutex` |

本项目只用了「框架 + 锁」两个模块：

```xml
<artifactId>curator-framework</artifactId>
<artifactId>curator-recipes</artifactId>
```

`pom.xml:38-45`。

---

## 2. 客户端的创建

```java
@Bean(destroyMethod = "close")
public CuratorFramework curatorFramework(ZkProperties props) throws InterruptedException {
    String namespace = StringUtils.hasText(props.getNamespace()) ? props.getNamespace() : null;

    CuratorFramework client = CuratorFrameworkFactory.builder()
            .connectString(props.getConnectString())
            .sessionTimeoutMs((int) props.getSessionTimeout().toMillis())
            .connectionTimeoutMs((int) props.getConnectionTimeout().toMillis())
            .namespace(namespace)
            .retryPolicy(new ExponentialBackoffRetry(
                    (int) props.getBaseSleepTime().toMillis(), props.getMaxRetries()))
            .build();

    client.getConnectionStateListenable().addListener((c, newState) ->
            log.info("[ZK] 连接状态变化 -> {}", describe(newState)));

    client.start();

    int waitMs = (int) props.getConnectionTimeout().toMillis();
    if (!client.blockUntilConnected(waitMs, TimeUnit.MILLISECONDS)) {
        throw new IllegalStateException("连接 ZooKeeper 超时(" + waitMs + "ms)...");
    }
    return client;
}
```

`src/main/java/com/example/learnzk/config/ZkConfig.java:23-53`。

逐个参数解释：

### 2.1 `connectString`

```
127.0.0.1:2185,127.0.0.1:2186,127.0.0.1:2187
```

逗号分隔的地址列表。客户端会随机选一个建立连接，失败则换下一个，并记住可用的节点。**不需要写全所有节点**，但写全可以加快故障切换。

### 2.2 `sessionTimeoutMs`

会话超时，本项目 30s（`application.yml:13`）。

它的作用不是「连接多久超时」，而是「服务端多久收不到心跳就认为你死了」。这个值同时决定：

- 客户端崩溃后，临时节点多久被清理（锁多久自动释放）；
- 网络抖动时，会不会被误判为死亡；
- 客户端在 `LOST` 状态下多久能恢复。

调大：更能容忍网络抖动和 GC 停顿，但故障发现慢、锁释放慢。
调小：故障发现快，但更容易误判，尤其在 Full GC 或网络拥塞时。

服务端会把它夹在 `[2×tickTime, 20×tickTime]` 之间，默认 `tickTime=2000ms`，即 4s~40s。写 30s 是合法的；写 3s 会被服务端提升到 4s。

### 2.3 `connectionTimeoutMs`

建立连接的等待上限，本项目 15s（`application.yml:14`）。它只影响「连不上时等多久」，不影响已建立连接的存活。

本项目还把它复用为启动阻塞的上限（见 2.6）。

### 2.4 `namespace`

见第 3 节。

### 2.5 `retryPolicy`

见第 4 节。

### 2.6 `blockUntilConnected`

`client.start()` 是异步的：它会立刻返回，连接在后台进行。如果不阻塞，应用可能已经对外提供服务，但第一个请求到达时客户端还没连上。

所以这里主动等：

```java
if (!client.blockUntilConnected(waitMs, TimeUnit.MILLISECONDS)) {
    throw new IllegalStateException("连接 ZooKeeper 超时...");
}
```

注意 Curator 5.7.1 的 `blockUntilConnected` 只有 `(int, TimeUnit)` 重载，没有 `long` 版本——这也是为什么这里要 `(int)` 强转。

**取舍**：启动即失败，适合演示和「没有 ZK 就不能工作」的服务。如果你的服务允许降级运行，应该改成不阻塞、在状态监听里做懒加载。

### 2.7 `destroyMethod = "close"`

```java
@Bean(destroyMethod = "close")
```

`@Bean` 默认就会调用 `close()`/`shutdown()`，这里显式写出来是为了可读性。容器关闭时调用 `CuratorFramework.close()`，会：

1. 主动断开连接；
2. 服务端立即删除该会话的临时节点（不用等 30s 超时）；
3. 释放后台线程。

这对分布式锁很重要：正常停机 = 立即释放锁；`kill -9` = 等会话超时。

---

## 3. namespace：客户端侧的前缀

这是最容易误解的一个配置。

```yaml
zk:
  namespace: ""      # 本项目默认为空
```

### 3.1 它做了什么

如果设成 `learn-zk`，代码里：

```java
client.create().forPath("/foo", data);
```

实际写到服务端的路径是 `/learn-zk/foo`。但客户端后续所有操作都可以继续用 `/foo`。

本项目用一行日志说明这件事：

```java
log.info("namespace 生效后，逻辑路径 /foo 实际落在 znode {}/foo", namespace);
```

`config/ZkConfig.java:49-51`。

以及一个还原物理路径的工具方法：

```java
public static String physicalPath(String namespace, String logicalPath) {
    ...
    return ZKPaths.makePath("/" + namespace, logicalPath);
}
```

`config/ZkConfig.java:66-71`。

### 3.2 三个必须知道的细节

1. **namespace 不是服务端隔离**。服务端看到的就是 `/learn-zk/foo`，权限、配额、备份都按真实路径算。
2. **`namespace` 为空时必须传 `null`，不能传 `""`**。传空字符串会拼出 `//foo`。所以代码里先做了判断（`config/ZkConfig.java:25`）。
3. **`/` 的含义变了**。设置 namespace 后，客户端的 `/` 指向 `/learn-zk`，`getChildren("/")` 返回的是 `learn-zk` 下的子节点，而不是根节点的子节点。

### 3.3 什么时候该用

- 多个团队共用一个 ZK 集群：每人一个 namespace，避免路径撞车；
- 同一套代码部署多环境（dev/test）：namespace 跟着环境走。

代价是排查问题时容易「代码里是 `/foo`，zoonavigator 里找不到」——记得加前缀。

---

## 4. 重试策略：ExponentialBackoffRetry

```java
.retryPolicy(new ExponentialBackoffRetry(
        (int) props.getBaseSleepTime().toMillis(), props.getMaxRetries()))
```

本项目 `baseSleepTime = 1s`、`maxRetries = 3`（`application.yml:16-17`）。

### 4.1 退避算法

第 n 次重试前等待：

```
sleep = base × max(1, random(0, 2^(n+1)))
```

即：

| 重试次数 | 等待范围 |
| --- | --- |
| 第 1 次 | 约 1s |
| 第 2 次 | 1s ~ 3s |
| 第 3 次 | 1s ~ 7s |

随机抖动的作用是避免大量客户端在服务端恢复的同一瞬间一起重连（惊群）。

三次全部失败后，当前操作抛 `KeeperException.ConnectionLossException`（或具体错误），交给上层处理。本项目由 `ZkExceptionHandler` 映射成 HTTP 503。

### 4.2 哪些错误会重试

- 连接类：`CONNECTIONLOSS`、`OPERATIONTIMEOUT`、`SESSIONEXPIRED`（由客户端重新建立会话后重试）；
- 明确表示「状态可能已变」的：`BADVERSION`、`NODEEXISTS` 这类**业务语义错误不会重试**，会直接抛出。

所以「重试策略」不能替代业务层的幂等设计。一个 `create` 请求重试时，如果第一次其实已经成功、只是响应丢了，第二次会拿到 `NODEEXISTS`。

### 4.3 调参直觉

| 场景 | 建议 |
| --- | --- |
| 启动阶段、短时网络抖动 | base 200~500ms，maxRetries 3~5 |
| 跨机房、网络不稳 | base 1s，maxRetries 5~10 |
| 延迟敏感接口 | 关掉自动重试，自己做超时控制 |

---

## 5. 连接状态机

Curator 把连接状态抽象成枚举，本项目在启动时注册了监听并翻译成中文日志：

```java
client.getConnectionStateListenable().addListener((c, newState) ->
        log.info("[ZK] 连接状态变化 -> {}", describe(newState)));
```

`config/ZkConfig.java:36-37`，翻译逻辑在 `:55-63`。

| 状态 | 含义 | 临时节点 | 应该做什么 |
| --- | --- | --- | --- |
| `CONNECTED` | 首次连接成功 | 正常 | 正常服务 |
| `SUSPENDED` | 连接断开，正在重连 | 仍存在（会话未过期） | 暂停写操作，等待恢复；不要立刻判死 |
| `RECONNECTED` | 重连成功，会话复用 | 仍存在 | 可以继续；但期间错过的 watch 需要重新确认 |
| `LOST` | 会话已过期 | **已被删除** | 必须重新初始化：重建临时节点、重新抢锁、重新注册 watch |
| `READ_ONLY` | 只读模式（ZK 3.4+，分区时可能出现） | 视情况 | 只能读，写会失败 |

### 5.1 最容易写错的地方

把 `SUSPENDED` 当成 `LOST` 处理：一断网就删数据、放锁。实际上会话还在，临时节点也还在，另一个客户端根本没有拿到锁。正确做法是等 `RECONNECTED` 或 `LOST` 再决策。

### 5.2 状态监听里不要做重活

状态回调运行在 Curator 的状态管理线程上。在里面做同步 ZK 请求、长时间计算，会阻塞后续状态事件的处理，严重时导致死锁。规范做法：**回调只记录状态 / 投递到队列，业务逻辑放到自己的线程池**。

---

## 6. Curator 还提供了什么（本项目未用，但值得知道）

| 组件 | 作用 |
| --- | --- |
| `InterProcessMutex` | 可重入分布式锁（本项目使用） |
| `LeaderLatch` / `LeaderSelector` | 选主 |
| `TreeCache` / `PathChildrenCache` | 自动维护本地缓存 + 持续监听，替代手写 watch |
| `PersistentNode` | 保证某节点长期存在（断线重连后自动重建） |
| `DistributedAtomicLong` | 分布式计数器 |
| `InterProcessSemaphoreV2` | 分布式信号量 / 限流 |

当你要手写 watch 时，先想想 `TreeCache` 是不是已经做了。

---

## 7. 本项目连接相关的可观测点

| 想看什么 | 怎么看 |
| --- | --- |
| 当前是否连上 | `GET /api/zk/health`（`web/ZkController.java:43-51`） |
| 连接状态变化 | 启动日志里搜 `[ZK] 连接状态变化` |
| Curator 内部在干什么 | `application.yml:26` 把 `org.apache.curator` 调成 `DEBUG` |
| 实际写到哪个路径 | 设了 namespace 时看启动日志（`config/ZkConfig.java:49-51`） |

---

## 8. 自检

1. 为什么 `blockUntilConnected` 要放在 Bean 创建方法里？
2. `sessionTimeout` 调大和调小，分别影响什么？
3. namespace 设成 `learn-zk` 后，`getChildren("/")` 返回的是什么？
4. `SUSPENDED` 状态下，本客户端的临时节点还在吗？
5. 为什么 `create` 的重试可能导致 `NODEEXISTS`？

参考：2.6、2.2、3.2、5、4.2。

---

## 9. 延伸阅读

- Curator 官方文档：<https://curator.apache.org/docs/>
- ZooKeeper 会话与超时：<https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#ch_zkSessions>

下一篇：[`04-crud-walkthrough.md`](04-crud-walkthrough.md)
