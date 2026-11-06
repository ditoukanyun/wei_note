---
type: reference
created: 2026-11-06
updated: 2026-11-06
area: "[[后端开发]]"
tags: [ZooKeeper, 分布式, 一致性, ZAB]
---
# 02 ZooKeeper 原理

> 这一章不碰代码，先把 ZooKeeper 这个东西本身讲清楚。
> 读完你应该能回答：它到底存了什么？为什么能保证顺序？三台机器挂一台为什么还能写？会话超时到底意味着什么？

## 本章解决什么问题

很多教程把 ZooKeeper 讲成「一个树形结构的 key-value」。这个说法能让你跑通 demo，但解释不了三个现象：

1. 为什么 `create` 不能覆盖已有节点，改数据必须用 `setData`？
2. 为什么节点会有「版本号」，而且更新时可以带版本做校验？
3. 为什么临时节点能实现分布式锁，而且客户端崩了锁会自动释放？

答案都在它的数据模型和会话模型里。

---

## 结论先行

| 问题 | 一句话答案 |
| --- | --- |
| 它是什么 | 分布式协调服务：用一棵小树存放**少量、关键、需要强一致**的元数据 |
| 它不是什么 | 不是数据库、不是缓存、不是消息队列；单节点数据上限约 1MB |
| 为什么有序 | 所有写请求由 Leader 分配全局递增的 zxid，按 zxid 顺序提交 |
| 为什么高可用 | 写操作只需要过半节点确认；3 台容忍 1 台故障 |
| 读为什么可能旧 | 读请求由各节点本地响应，不经过 Leader；需要最新值要先 `sync` |
| 临时节点为什么能自动释放 | 节点归属某个 session，session 过期服务端就删掉它名下所有临时节点 |

---

## 1. 定位：协调，不是存储

ZooKeeper 的典型数据量是「几百个到几万个 znode，每个几十字节到几 KB」。它被设计用来回答这类问题：

- 当前哪个实例是主节点？
- 配置项 `db.url` 现在是什么？
- 服务 `order-service` 有哪些存活实例？
- 谁先拿到这把锁？

这些问题共同的特点是：**数据量小、读多写少、但不能出错**。ZooKeeper 用「所有数据放内存 + 写操作过半确认 + 全局顺序」来换这个「不能出错」。

反过来说，下面这些事不要用它做：

| 想做的事 | 为什么不适合 |
| --- | --- |
| 存业务订单 | 单 znode 上限约 1MB（`jute.maxbuffer` 默认 1MB），全量数据放内存 |
| 按条件查询 | 没有查询语言、没有二级索引，只能按路径取 |
| 高频写入 | 每次写都要广播 + 过半落盘，吞吐远低于数据库 |
| 当缓存 | 没有淘汰策略、没有 TTL 语义（TTL 节点是另一回事）、容量太小 |
| 当消息队列 | 没有消费位点、没有堆积能力；虽然能做简单队列，但不是它的强项 |

一句话：**ZooKeeper 存的是「协调所需的元数据」，不是业务数据。**

---

## 2. 数据模型：一棵 znode 树

### 2.1 结构

```
/
├── zookeeper                 # 系统保留
├── learn-zk
│   ├── demo
│   │   ├── users
│   │   │   ├── u001
│   │   │   └── u003
│   │   └── sessions
│   │       └── session-001   # 临时节点
│   └── lock
│       ├── task-locks        # 锁目录，子节点是临时顺序节点
│       └── inventory
│           └── stock
```

每个节点叫 **znode**，由三部分组成：

| 组成 | 说明 |
| --- | --- |
| path | 唯一标识，如 `/learn-zk/demo/users/u001` |
| data | 字节数组，ZK 不关心内容，序列化方式由业务决定（本项目存 UTF-8 字符串） |
| stat | 元数据：版本、时间戳、子节点数、临时节点归属等 |

### 2.2 路径规则

- 必须以 `/` 开头；
- 不能以 `/` 结尾（根节点 `/` 本身除外）；
- 不能有 `//`、`.`、`..`；
- 父节点必须存在才能创建子节点（除非客户端用 `creatingParentsIfNeeded` 逐级创建）。

本项目的路径规整逻辑在 `src/main/java/com/example/learnzk/service/ZkPath.java:12-27`。注意根节点 `/` 是合法路径——可以读、可以列子节点，只是不能删（`service/ZkService.java:115-117` 单独拦了删除）。

### 2.3 data 的大小

服务端对单个 znode 的数据有上限，默认约 1MB（`jute.maxbuffer`）。实际使用建议控制在几 KB 以内，因为：

- 所有 znode 常驻内存；
- 每次读都要走网络传输；
- 写请求会带着完整数据广播给所有节点。

本项目在树形遍历时只读取 `dataLength <= 4096` 的节点数据（`service/ZkService.java:166-170`），就是为了避免一个页面把大节点全拉下来。

---

## 3. 节点类型：四个维度决定生命周期

创建节点时必须指定 `CreateMode`。它的取值是「是否临时」×「是否顺序」的组合，另外还有两个特殊类型。

| 类型 | 生命周期 | 名字 | 典型用途 |
| --- | --- | --- | --- |
| `PERSISTENT` | 永久，除非显式删除 | 指定名 | 配置、目录、元数据 |
| `EPHEMERAL` | 绑定 session，会话结束自动删 | 指定名 | 服务注册、存活标记、锁 |
| `PERSISTENT_SEQUENTIAL` | 永久 | 指定名 + 10 位序号 | 分布式队列、全局递增 ID |
| `EPHEMERAL_SEQUENTIAL` | 绑定 session | 指定名 + 10 位序号 | **分布式锁**、临时选主 |
| `CONTAINER` | 永久，但子节点为空时会被服务端清理 | 指定名 | 批量任务的容器目录 |
| `TTL` | 指定时间内无修改且无子节点则删除 | 指定名 | 临时元数据（需服务端开启） |

本项目的接口支持前五种（`src/main/java/com/example/learnzk/web/ZkController.java:126-137`）。

### 3.1 临时节点的两个硬约束

1. **临时节点不能有子节点**。尝试创建子节点会得到 `NOCHILDRENFOREPHEMERALS`。原因很实际：父节点随会话消失，子节点怎么办？ZK 选择直接禁止。
2. **临时节点属于创建它的 session，而不是连接**。网络闪断后如果客户端在超时时间内重连成功，会话还在，临时节点也还在；只有会话过期，节点才会被删。

### 3.2 顺序节点的序号规则

服务端在名字后面追加 10 位十进制序号，从父节点的计数器递增：

```
create /lock/task-locks/lock-  →  /lock/task-locks/lock-0000000000
create /lock/task-locks/lock-  →  /lock/task-locks/lock-0000000001
```

序号是**父节点维度**的，不是全局的。所以同一目录下的序号可以安全地用来排序。

正因为是定长 10 位，字典序等于数值序——本项目 `describeQueue` 直接字符串排序（`service/DistributedLockService.java:283-284`）。

---

## 4. Stat：每个 znode 的元数据

`stat` 是理解 ZooKeeper 并发控制的钥匙。本项目把它完整暴露成了 `StatView`：

```java
public record StatView(
        long czxid, long mzxid, String ctime, String mtime,
        int version, int cversion, int aversion,
        long ephemeralOwner, boolean ephemeral,
        int dataLength, int numChildren, long pzxid
) {}
```

`src/main/java/com/example/learnzk/model/StatView.java:10-23`。

| 字段 | 含义 | 什么时候变 |
| --- | --- | --- |
| `czxid` | 创建该节点的事务 ID | 创建时固定 |
| `mzxid` | 最后一次修改数据的事务 ID | `setData` 时更新 |
| `ctime` / `mtime` | 创建 / 修改时间的毫秒时间戳 | 同上 |
| `version` | **数据版本**，从 0 开始 | 每次 `setData` +1 |
| `cversion` | **子节点版本** | 子节点增删时 +1 |
| `aversion` | ACL 版本 | 权限变更时 +1 |
| `ephemeralOwner` | 临时节点所属的 sessionId；持久节点为 0 | 创建时确定 |
| `dataLength` | 数据字节数 | 随数据变化 |
| `numChildren` | 直接子节点数 | 子节点增删时变 |
| `pzxid` | 最后一次子节点列表变更的 zxid | 子节点增删时更新 |

### 4.1 version 和 cversion 为什么分开

因为它们是两种不同的并发冲突：

- 两个人同时改同一个节点的**数据** → 用 `version` 检测；
- 两个人同时往同一个节点下**加子节点** → 用 `cversion` 检测。

`setData` 只增加 `version`，`create`/`delete` 子节点只增加父节点的 `cversion`。互不干扰。

### 4.2 version 是乐观锁的核心

```
客户端 A：getData → version=3
客户端 B：getData → version=3
客户端 A：setData(dataA, version=3) → 成功，version 变成 4
客户端 B：setData(dataB, version=3) → 失败，BADVERSION
```

B 必须重新读一次，拿到 version=4，再决定怎么改。这就是 CAS（compare-and-swap），也是本项目 `update` 接口 `version` 参数的语义（`service/ZkService.java:92-105`）。

---

## 5. zxid 与全局顺序

**zxid（ZooKeeper Transaction ID）是 64 位整数**，结构是：

```
┌──────────────┬──────────────┐
│  epoch (32)  │  counter (32)│
└──────────────┴──────────────┘
```

- `epoch`：Leader 的任期号。每次选出新 Leader，epoch +1；
- `counter`：该任期内的写操作计数器，从 0 递增。

所以 zxid 全局单调递增。ZK 的所有写操作都按 zxid 排序、提交、应用。这带来两个结果：

1. 任意两个客户端看到的事务顺序一致；
2. 比较两个 zxid 就能知道谁先谁后——`czxid`/`mzxid`/`pzxid` 都是这个用途。

### 5.1 为什么读请求可以乱序

写请求需要 Leader 和过半确认，但**读请求由每个节点用自己的内存数据直接回答**，不经过 Leader，也不产生 zxid。因此：

- 你刚写完，立刻去另一个节点读，可能读到旧值（复制还没到）；
- 同一个客户端会保证「读到自己写过的值」（会话保证单调读）；
- 需要强一致读时，先调 `sync()` 再读。

这是 ZooKeeper 用「读性能」换「写一致性」的设计。

---

## 6. 集群：角色、过半与写流程

### 6.1 两种角色 + 观察者

| 角色 | 投票 | 处理写 | 处理读 | 说明 |
| --- | --- | --- | --- | --- |
| Leader | ✅ | ✅ | ✅ | 唯一，负责分配 zxid、广播提案 |
| Follower | ✅ | 转发给 Leader | ✅ | 参与选举和过半确认 |
| Observer | ❌ | 转发给 Leader | ✅ | 只读扩展，不参与投票，不拖慢写 |

### 6.2 过半（quorum）

写操作需要 **`n/2 + 1` 个节点确认**（不含 Observer）：

| 集群规模 | 过半 | 最多容忍故障 |
| --- | --- | --- |
| 3 | 2 | 1 |
| 5 | 3 | 2 |
| 7 | 4 | 3 |

这就是为什么生产环境一般用奇数台：4 台的过半是 3，和 3 台的容错能力一样，却多花一台机器。

本项目 `docker-compose.yml` 起的是 3 节点，挂 1 台仍可读写。

### 6.3 一次写请求的完整流程

```
Client
  │ 1. 连接任意一台（可能是 Follower）
  ▼
Follower
  │ 2. 发现自己不是 Leader，把请求转发给 Leader
  ▼
Leader
  │ 3. 分配 zxid，生成 PROPOSAL，广播给所有 Follower
  ▼
Follower ×N
  │ 4. 写入本地事务日志（fsync）
  │ 5. 回 ACK
  ▼
Leader
  │ 6. 收到过半 ACK → 广播 COMMIT
  ▼
所有节点
  │ 7. 应用事务到内存数据树
  ▼
Client 收到成功响应
```

关键点：**第 6 步过半就返回**，不等所有节点。慢节点不会拖死整个集群，但会在之后通过同步追上来。

### 6.4 一次读请求

```
Client → 任意节点 → 直接读内存 → 返回
```

不写日志、不广播、不经过 Leader。所以读的吞吐可以靠加 Observer 横向扩展，写不行。

---

## 7. ZAB：崩溃恢复 + 消息广播

ZAB（ZooKeeper Atomic Broadcast）是 ZK 保证一致性的协议，可以理解成两个阶段：

### 7.1 消息广播（正常运行时）

Leader 把每个写请求包装成 proposal，按 zxid 顺序广播；过半 ACK 后提交。Follower 严格按 zxid 顺序应用，所以所有节点的状态机演进顺序一致。

### 7.2 崩溃恢复（Leader 挂掉时）

1. **选举**：Follower 投票，得票过半者成为新 Leader（Fast Leader Election）；
2. **发现**：新 Leader 向所有节点收集各自最大的 zxid；
3. **同步**：新 Leader 把缺失的事务补发给落后的节点，确保过半节点数据最新；
4. **广播**：恢复对外服务。

选举时会优先选择「zxid 最大」的节点，保证新 Leader 一定拥有已提交的最新事务。

### 7.3 ZK 承诺的五条一致性

| 保证 | 含义 |
| --- | --- |
| 顺序一致性 | 同一个客户端发出的更新，按发送顺序生效 |
| 原子性 | 一次更新要么全部生效，要么完全不生效 |
| 单一视图 | 同一个客户端连到哪个节点，看到的数据视图一致 |
| 可靠性 | 一旦更新成功，就会持久保留 |
| 及时性 | 客户端看到的状态在一定时间范围内是最新的（有界，但不是实时） |

注意最后一条：**「及时」不等于「立刻」**。跨客户端的读可能短暂落后，这是设计取舍，不是 bug。

---

## 8. 会话：临时节点和锁的基础

### 8.1 会话是什么

客户端连接时，服务端创建一个 session，分配 64 位的 sessionId，并协商一个超时时间。之后：

- 客户端定期发心跳（PING）续约；
- 服务端在超时时间内没收到心跳，判定会话过期；
- 会话过期时，服务端删除该会话名下的**所有临时节点**，并让所有 watch 失效。

### 8.2 超时时间怎么定

客户端在连接时提议一个值，服务端会把它夹在 `[minSessionTimeout, maxSessionTimeout]` 之间：

```
minSessionTimeout = 2  × tickTime
maxSessionTimeout = 20 × tickTime
```

默认 `tickTime = 2000ms`，所以合法区间是 4s ~ 40s。本项目配置 30s（`application.yml:13`），在区间内。

### 8.3 30s 意味着什么

- 应用正常关闭 → `CuratorFramework.close()` → 主动断开 → 临时节点立即删除；
- 进程被 `kill -9` → 没有断开通知 → 服务端要等 30s 心跳超时后才删；
- 网络分区 → 客户端以为还连着，服务端已经判定过期 → 两边对「锁是否还持有」的认知可能不一致。

最后一条是分布式锁最危险的场景，详见 [`06-distributed-lock.md`](06-distributed-lock.md) 第 6 节。

### 8.4 会话 vs 连接

| | 连接（connection） | 会话（session） |
| --- | --- | --- |
| 范围 | 一条 TCP 连接 | 跨多条连接 |
| 断开后 | 立即消失 | 在超时时间内仍有效 |
| 临时节点 | 不直接绑定 | 绑定会话 |
| 重连 | 新建连接 | 如果还在超时内，复用原会话 |

所以「网络闪断」通常不会丢临时节点，只有「会话过期」才会。

---

## 9. 本项目用到了哪些特性

| 特性 | 用在哪 | 代码位置 |
| --- | --- | --- |
| 树形路径 | 所有 CRUD | `service/ZkService.java` |
| 版本乐观锁 | 更新接口 | `service/ZkService.java:92-105` |
| 临时节点 | 启动演示 `session-001` | `demo/ZkCrudDemoRunner.java:108-113` |
| 顺序节点 | 分布式锁 | 由 Curator `InterProcessMutex` 内部创建 |
| watch | Watch 页签 | `service/ZkWatchService.java` |
| session | 连接管理与锁释放 | `config/ZkConfig.java:27-34` |

---

## 10. 自检

1. 为什么临时节点不能有子节点？
2. `version` 和 `cversion` 分别在哪两种操作中递增？
3. 3 节点集群挂掉 1 台，还能写吗？挂掉 2 台呢？
4. 为什么读请求可能读到旧数据？需要最新值时怎么办？
5. 客户端 `kill -9` 后，它创建的临时节点会立刻消失吗？

参考答案分别在：3.1、4.1、6.2、5.1、8.3。

---

## 11. 延伸阅读

- ZooKeeper 官方程序员指南：<https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html>
- ZooKeeper 内部原理（含 ZAB）：<https://zookeeper.apache.org/doc/current/zookeeperInternals.html>
- 一致性保证原文：<https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#ch_zkGuarantees>

下一篇：[`03-curator-client.md`](03-curator-client.md)
