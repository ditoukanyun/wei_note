---
type: reference
created: 2026-11-06
updated: 2026-11-06
area: "[[后端开发]]"
tags: [ZooKeeper, CRUD, 乐观锁]
---
# 04 CRUD 全链路走读

> 这一章把「节点 CRUD」页签里的每个按钮拆开：前端发了什么、后端做了什么、ZooKeeper 返回什么、失败时为什么是那个状态码。

## 本章解决什么问题

`create` / `getData` / `setData` / `delete` 四个 API 看起来和普通 KV 存储差不多，但 ZooKeeper 的语义有几处关键差异：

- `create` **不会覆盖**已有节点；
- 改数据不是 `create`，而是 `setData`；
- 每个节点带版本号，可以当乐观锁用；
- 删除有子节点的节点会失败，必须显式递归。

这些差异正是最常见的报错来源。本章按「C → R → U → D」顺序讲，每条都对应本项目的一个方法。

---

## 结论先行

| 操作 | ZooKeeper 原语 | 关键语义 |
| --- | --- | --- |
| 创建 | `create` | 节点已存在直接失败（`NODEEXISTS`），从不覆盖 |
| 读取 | `getData` | 同时返回数据和 `Stat`；节点不存在报 `NONODE` |
| 判断存在 | `exists` | 不存在返回 `null`，不抛异常 |
| 更新 | `setData` | 可带 `version` 做 CAS，版本不符报 `BADVERSION` |
| 删除 | `delete` | 默认只能删空节点，有子节点报 `NOTEMPTY` |
| 列举 | `getChildren` | 只返回子节点名字，不返回数据 |

---

## 1. 一条创建请求的完整链路

```
POST /api/zk/nodes
{ "path": "/learn-zk/api/order-1", "data": "{}", "mode": "PERSISTENT", "createParents": true }
```

```
ZkController.create                          web/ZkController.java:55-63
  ├─ @Valid 校验 CreateNodeRequest
  ├─ parseMode("PERSISTENT")                 web/ZkController.java:126-137
  └─ ZkService.create(path, data, mode, createParents)
       ├─ ZkPath.normalize(path)             service/ZkPath.java:12-27
       ├─ data.getBytes(UTF_8)
       └─ client.create()
            .creatingParentsIfNeeded()       service/ZkService.java:50-54
            .withMode(mode)
            .forPath(path, payload)
```

返回的是**服务端实际创建的路径**。对顺序节点来说，这个值和传入的 path 不同：

```
传入 /learn-zk/seq/task-
返回 /learn-zk/seq/task-0000000003
```

所以业务代码一定要用返回值，而不是自己拼路径。

---

## 2. 路径规整

```java
public static String normalize(String raw) {
    if (raw == null || raw.isBlank()) {
        throw new IllegalArgumentException("path 不能为空");
    }
    String path = raw.trim();
    if (!path.startsWith("/")) {
        path = "/" + path;
    }
    while (path.length() > 1 && path.endsWith("/")) {
        path = path.substring(0, path.length() - 1);
    }
    if (path.contains("//")) {
        throw new IllegalArgumentException("path 不能包含连续的 /: " + raw);
    }
    return path;
}
```

`src/main/java/com/example/learnzk/service/ZkPath.java:12-27`。

做四件事：

1. 空值拒绝；
2. 自动补前导 `/`（`learn-zk/foo` → `/learn-zk/foo`）；
3. 去掉尾部 `/`（但根节点 `/` 保留）；
4. 拒绝 `//`。

**为什么不在规整阶段禁止 `/`**：根节点是合法路径，读数据、列子节点、遍历树都要用。只有删除根节点是不允许的，所以那条校验放在 `delete` 里（`service/ZkService.java:115-117`）。

---

## 3. Create

```java
public String create(String path, String data, CreateMode mode, boolean createParents) throws Exception {
    String p = ZkPath.normalize(path);
    byte[] payload = data == null ? new byte[0] : data.getBytes(StandardCharsets.UTF_8);

    if (createParents) {
        created = client.create().creatingParentsIfNeeded().withMode(mode).forPath(p, payload);
    } else {
        created = client.create().withMode(mode).forPath(p, payload);
    }
    return created;
}
```

`service/ZkService.java:45-62`。

### 3.1 为什么 create 不会覆盖

这是 ZooKeeper 的写语义：**`create` 是「插入一个不存在的 key」，不是 upsert**。节点已存在时直接返回 `KeeperException.NodeExistsException`。

对比常见 KV 存储：

| 系统 | `put(k, v)` 语义 |
| --- | --- |
| Redis `SET` | 覆盖 |
| ZooKeeper `create` | 不覆盖，已存在就报错 |
| ZooKeeper `setData` | 覆盖（但可带版本校验） |

所以第二次对同一路径执行创建，会得到 409：

```json
{ "code": 409, "message": "NODEEXISTS: KeeperErrorCode = NodeExists for /learn-zk\n→ 节点已存在。create 不会覆盖已有节点，要改数据请用 UPDATE(PUT)" }
```

（提示语来自 `web/ZkExceptionHandler.java:36`。）

### 3.2 createParents 做了什么

`creatingParentsIfNeeded()` 会从根开始逐级检查并创建缺失的父节点：

```
要创建 /a/b/c，但 /a 不存在
→ 自动创建 /a（PERSISTENT）
→ 自动创建 /a/b（PERSISTENT）
→ 创建 /a/b/c（你指定的 mode）
```

注意：**自动创建的父节点永远是持久节点**，即使你请求的是临时节点。而且如果父节点是临时节点，会直接失败（临时节点不能有子节点）。

### 3.3 版本从 0 开始

新创建节点的 `version = 0`。这不是「还没改过所以是 -1」，而是第一次创建就算第 0 版。后续每 `setData` 一次 +1。

---

## 4. Read / Exists / Children

### 4.1 读数据和 Stat 一次拿回

```java
Stat stat = new Stat();
byte[] data = client.getData().storingStatIn(stat).forPath(p);
```

`service/ZkService.java:66-73`。

`storingStatIn` 让 Curator 把服务端返回的 Stat 填进这个对象，避免「先读数据再 stat」两次请求。

节点不存在时抛 `NoNodeException`，映射成 HTTP 404。

### 4.2 exists：不存在时返回 null

```java
public StatView exists(String path) throws Exception {
    Stat stat = client.checkExists().forPath(p);
    return StatView.of(stat);
}
```

`service/ZkService.java:75-79`。

`checkExists` 在节点不存在时返回 `null`，**不抛异常**。这是它和 `getData` 最大的区别：

| | 节点存在 | 节点不存在 |
| --- | --- | --- |
| `getData` | 返回数据和 Stat | 抛 `NONODE` |
| `checkExists` | 返回 Stat | 返回 `null` |

所以「判断存在」用 `exists`，「读内容」用 `read`。用 `read` 做存在判断会让「不存在」变成异常，控制流很别扭。

### 4.3 children：只返回名字

```java
List<String> children = client.getChildren().storingStatIn(stat).forPath(p);
Collections.sort(children);
```

`service/ZkService.java:81-88`。

两点：

- 返回的是**名字**（`u001`），不是完整路径；
- ZK 不保证顺序，本项目做了字典序排序，便于展示。

要拿子节点数据，得对每个名字再发一次 `getData`——这是 N+1 查询，节点多时要注意。树形接口因此加了节点上限（见第 7 节）。

---

## 5. Update：版本号就是乐观锁

```java
if (version == null || version < 0) {
    stat = client.setData().forPath(p, payload);
} else {
    stat = client.setData().withVersion(version).forPath(p, payload);
}
```

`service/ZkService.java:92-105`。

### 5.1 两种模式

| 传入 version | 行为 | 适用场景 |
| --- | --- | --- |
| `null` 或 `-1` | 无条件覆盖，不管当前是第几版 | 演示、后台强制修正 |
| `>= 0` | 只有当前版本等于它才写入 | 并发更新、需要防丢失的业务 |

### 5.2 CAS 的完整用法

带版本的更新不是一次调用就完事，而是一个循环：

```java
while (true) {
    NodeInfo node = zk.read(path);          // 拿到 data + version
    String newValue = transform(node.data());
    try {
        zk.update(path, newValue, node.stat().version());
        break;                              // 成功
    } catch (KeeperException.BadVersionException e) {
        // 期间被别人改过，重新读、重新算
    }
}
```

本项目为了演示，没有做自动重试：版本冲突直接返回 409，让用户看到 `BADVERSION`。真实业务里通常要加重试上限（例如 3 次），避免活锁。

### 5.3 版本冲突的时序

```
时间 →

客户端 A: 读 v0 ──────────────── 写 v0 ✅ → 变成 v1
客户端 B:        读 v0 ───────────────────── 写 v0 ❌ BADVERSION
```

B 拿到的数据已经过期。ZK 不允许它悄悄覆盖，这就是「乐观」的含义：先假设不冲突，提交时才检查。

---

## 6. Delete

```java
public String delete(String path, boolean recursive, Integer version) throws Exception {
    String p = ZkPath.normalize(path);
    if ("/".equals(p)) {
        throw new IllegalArgumentException("ZooKeeper 不允许删除根节点 /");
    }
    boolean useVersion = version != null && version >= 0;

    if (recursive && useVersion) {
        client.delete().deletingChildrenIfNeeded().withVersion(version).forPath(p);
    } else if (recursive) {
        client.delete().deletingChildrenIfNeeded().forPath(p);
    } else if (useVersion) {
        client.delete().withVersion(version).forPath(p);
    } else {
        client.delete().forPath(p);
    }
    return p;
}
```

`service/ZkService.java:113-133`。

### 6.1 为什么写了四个分支

Curator 的 builder 是**接口链**：`deletingChildrenIfNeeded()` 返回的是 `BackgroundVersionable`，类型上不再保证还能继续链式调用所有方法。条件组合只能展开写——这不是风格问题，是 Java 类型系统的限制。

### 6.2 三种失败

| 情况 | 错误码 | HTTP | 解决 |
| --- | --- | --- | --- |
| 有子节点，`recursive=false` | `NOTEMPTY` | 400 | 勾选递归删除 / 传 `recursive=true` |
| 节点不存在 | `NONODE` | 404 | 先 `exists` 确认 |
| 删根节点 `/` | `BADARGUMENTS`（被本项目提前拦截） | 400 | 根节点不可删 |

### 6.3 递归删除的实现

`deletingChildrenIfNeeded()` 不是一次原子操作，而是 Curator 帮你**后序遍历**：先删所有子节点，再删自己。中间任何一步失败都会留下部分删除的状态——ZK 没有「目录级事务」。

如果业务要求「要么全删要么全不删」，需要在应用层做补偿，或者用别的数据结构。

---

## 7. Tree：递归遍历的三个保护

```java
private TreeNode walk(String path, int remainingDepth, int[] counter) throws Exception {
    if (++counter[0] > TREE_NODE_CAP) {
        throw new IllegalStateException("节点数量超过 " + TREE_NODE_CAP + "...");
    }
    ...
    if (remainingDepth > 1) {
        for (String name : childNames) {
            children.add(walk(ZKPaths.makePath(path, name), remainingDepth - 1, counter));
        }
    }
    ...
    if (stat.getDataLength() > 0 && stat.getDataLength() <= 4096) {
        byte[] bytes = client.getData().forPath(path);
        data = new String(bytes, StandardCharsets.UTF_8);
    }
}
```

`service/ZkService.java:137-181`。

| 保护 | 值 | 作用 |
| --- | --- | --- |
| `maxDepth` | 默认 3，必须 ≥ 1 | 控制递归层数；传 1 只返回自己 |
| `TREE_NODE_CAP` | 5000（`service/ZkService.java:31`） | 防止一次请求扫穿整个集群 |
| 数据长度阈值 | 4096（`service/ZkService.java:167`） | 大节点不拉数据，只显示路径和子节点数 |

`maxDepth` 的语义容易搞错：它是「最多展开几层」，`maxDepth=1` 表示只看当前节点，`maxDepth=2` 表示当前 + 直接子节点。

树上每个节点还标注了 `ephemeral`（由 `ephemeralOwner != 0` 判断，`service/ZkService.java:176`），方便你一眼看出哪些节点会随会话消失。

---

## 8. 错误码 → HTTP 状态码

```java
HttpStatus status = switch (code) {
    case NONODE -> HttpStatus.NOT_FOUND;
    case NODEEXISTS, BADVERSION -> HttpStatus.CONFLICT;
    case NOAUTH, AUTHFAILED -> HttpStatus.FORBIDDEN;
    case BADARGUMENTS, NOTEMPTY, NOCHILDRENFOREPHEMERALS -> HttpStatus.BAD_REQUEST;
    case CONNECTIONLOSS, SESSIONEXPIRED, SESSIONMOVED -> HttpStatus.SERVICE_UNAVAILABLE;
    default -> HttpStatus.INTERNAL_SERVER_ERROR;
};
```

`src/main/java/com/example/learnzk/web/ZkExceptionHandler.java:20-27`。

为什么要映射，而不是统一 500：前端可以根据状态码决定是「提示用户改参数」（400/404/409）还是「稍后重试」（503）。

完整对照：

| KeeperException.Code | HTTP | 含义 |
| --- | --- | --- |
| `NONODE` | 404 | 节点不存在 |
| `NODEEXISTS` | 409 | 节点已存在 |
| `BADVERSION` | 409 | 版本冲突 |
| `NOTEMPTY` | 400 | 还有子节点 |
| `NOCHILDRENFOREPHEMERALS` | 400 | 临时节点不能有子节点 |
| `BADARGUMENTS` | 400 | 参数非法（如删根节点） |
| `NOAUTH` / `AUTHFAILED` | 403 | 权限不足 |
| `CONNECTIONLOSS` / `SESSIONEXPIRED` | 503 | 连接或会话问题，可重试 |
| 其他 | 500 | 未预期 |

---

## 9. 动手实验

以下命令假设应用跑在 8088：

```bash
B=http://localhost:8088/api/zk
```

### 实验 1：create 不覆盖

```bash
curl -s -X POST $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/lab/a","data":"v1","createParents":true}'

# 再来一次，故意重复
curl -s -X POST $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/lab/a","data":"v2","createParents":true}'
```

第二次返回 409 `NODEEXISTS`，且节点数据仍是 `v1`。

### 实验 2：父节点不存在

```bash
# 不自动建父节点
curl -s -X POST $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/lab/x/y/z","data":"1"}'
# → 404 NONODE

# 自动建父节点
curl -s -X POST $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/lab/x/y/z","data":"1","createParents":true}'
# → 成功
```

### 实验 3：版本乐观锁

```bash
# 读，记下 version
curl -s "$B/nodes?path=/learn-zk/lab/a"

# 用版本 0 更新（假设刚创建，version=0）
curl -s -X PUT $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/lab/a","data":"v2","version":0}'
# → 成功，version 变成 1

# 再用过期版本 0 更新
curl -s -X PUT $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/lab/a","data":"v3","version":0}'
# → 409 BADVERSION
```

### 实验 4：删除有子节点的目录

```bash
curl -s -X DELETE "$B/nodes?path=/learn-zk/lab"
# → 400 NOTEMPTY

curl -s -X DELETE "$B/nodes?path=/learn-zk/lab&recursive=true"
# → 成功
```

### 实验 5：临时节点随会话消失

```bash
curl -s -X POST $B/nodes -H 'Content-Type: application/json' \
  -d '{"path":"/learn-zk/lab/tmp","data":"alive","mode":"EPHEMERAL"}'

# 正常停掉应用（Ctrl+C / kill，不是 kill -9），再启动
# 节点已不在
curl -s "$B/nodes/exists?path=/learn-zk/lab/tmp"
```

---

## 10. 自检

1. 为什么第二次 `create` 同一路径会失败，而不是覆盖？
2. `exists` 和 `read` 在「节点不存在」时的行为有什么不同？
3. `withVersion(-1)` 和 `withVersion(0)` 分别是什么语义？
4. 递归删除是原子操作吗？
5. `tree(path, 2)` 会展开几层？

参考：3.1、4.2、5.1、6.3、7。

---

下一篇：[`05-watch-mechanism.md`](05-watch-mechanism.md)
