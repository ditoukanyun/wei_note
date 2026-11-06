---
type: reference
created: 2026-11-06
updated: 2026-11-06
area: "[[后端开发]]"
tags: [ZooKeeper, 排错, FAQ]
---
# 07 常见问题与排错

> 按「现象 → 原因 → 处理」组织。每条都标注了对应的代码位置，方便你改的时候知道动哪里。

## 快速定位表

| 现象 | 跳到 |
| --- | --- |
| 应用起不来，报「连接 ZooKeeper 超时」 | 1.1 |
| 8088 端口被占用 | 1.2 |
| `400 不允许对根节点 / 做该操作` | 2.1 |
| `409 NODEEXISTS` | 2.2 |
| `409 BADVERSION` | 2.3 |
| `404 NONODE` | 2.4 |
| `400 NOTEMPTY` | 2.5 |
| `503 CONNECTIONLOSS` / `SESSIONEXPIRED` | 2.6 |
| watch 注册了没反应 | 3.1 |
| watch 事件重复 | 3.2 |
| 应用重启后监听没了 | 3.4 |
| 锁演示抢锁超时 | 4.1 |
| 每次跑锁实验数字都不一样 | 4.2 |
| 加锁后慢得离谱 | 4.4 |
| 找不到锁日志文件 | 4.5 |
| zoonavigator 里看不到代码里的路径 | 5.1 |

---

## 1. 启动阶段

### 1.1 「连接 ZooKeeper 超时(15000ms)」

```
java.lang.IllegalStateException: 连接 ZooKeeper 超时(15000ms)，请检查 127.0.0.1:2185,...
```

**原因**：`ZkConfig` 在 Bean 创建阶段调用了 `blockUntilConnected`，连不上就直接让应用启动失败（`config/ZkConfig.java:41-45`）。

**排查顺序**：

```bash
# 1. ZK 容器起来了吗
docker ps | grep zoo

# 2. 宿主机端口通吗
nc -vz 127.0.0.1 2185

# 3. 容器内集群健康吗
docker exec zoo1 /apache-zookeeper-3.9.5-bin/bin/zkServer.sh status

# 4. 地址写对了吗（application.yml:10）
```

**处理**：

- 容器没起：`docker compose up -d`；
- 端口映射不对：检查 `docker-compose.yml`，宿主机应是 2185/2186/2187；
- 只想先启动应用、不看 ZK：`mvn spring-boot:run -Dspring-boot.run.arguments=--zk.demo.enabled=false` 仍然会连 ZK（连接是必需的），只是跳过启动演示。要完全跳过连接，需要改 `ZkConfig`，本项目没做这个开关。

### 1.2 8088 端口被占用

```
Web server failed to start. Port 8088 was already in use.
```

**原因**：已经有一个实例在跑（可能是 IDEA 里的旧进程，或上一个 `mvn spring-boot:run` 没退干净）。

**处理**：

```bash
lsof -i :8088          # 找到 PID
kill <PID>
```

或者换个端口启动：

```bash
mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=18088
```

> 建议：临时验证用 18088，避免和常驻实例抢端口；验证完记得停掉。

### 1.3 启动演示报错但不影响服务

日志里出现：

```
演示中断（不影响服务启动）: ...
```

**原因**：`ZkCrudDemoRunner` 的演示逻辑包了 try/catch（`demo/ZkCrudDemoRunner.java:37-47`），任何异常都只告警。

**常见触发**：

- 上一次演示留下的节点结构异常；
- 权限不足；
- 连接在演示途中断开。

**处理**：先确认 `/api/zk/health` 正常；然后手动删掉 `/learn-zk/demo` 再重启。

---

## 2. CRUD 报错

### 2.1 `400 不允许对根节点 / 做该操作`

**如果你看到这条消息，说明跑的是旧版本代码。** 早期版本的 `ZkPath.normalize` 对所有操作都拒绝 `/`，导致「树形浏览默认从 `/` 开始」直接报错。

当前版本的规则是：

- `/` 是合法路径，可以读、可以列子节点、可以遍历（`service/ZkPath.java:12-27`）；
- 只有**删除**根节点被拦截（`service/ZkService.java:115-117`）；
- 写根节点数据由 ZooKeeper 自己裁决（会返回 `BADARGUMENTS`）。

处理：重新编译启动。

### 2.2 `409 NODEEXISTS`

```
NODEEXISTS: KeeperErrorCode = NodeExists for /learn-zk
→ 节点已存在。create 不会覆盖已有节点，要改数据请用 UPDATE(PUT)
```

**原因**：`create` 是插入语义，不覆盖（详见 [`04-crud-walkthrough.md`](04-crud-walkthrough.md) 3.1）。

**处理**：

| 你的目的 | 正确操作 |
| --- | --- |
| 想改数据 | `PUT /api/zk/nodes` + `version` |
| 想重建 | 先 `DELETE` 再 `POST` |
| 只是确认存在 | 用 `GET /nodes/exists`，不要重复创建 |
| 批量初始化脚本 | 先 `exists` 判断，或捕获 409 当成「已存在」 |

**注意**：创建 `/learn-zk` 时也可能遇到这个错——因为前一次运行已经建过它了。这不是 bug。

### 2.3 `409 BADVERSION`

```
BADVERSION: KeeperErrorCode = BadVersion for /learn-zk/lab/a
→ 版本冲突。这条数据在你读取之后被改过，重新 READ 拿到最新 version 再更新
```

**原因**：你传的 `version` 不是当前版本。可能是：

- 页面上的版本号是几分钟前读的，期间别人改过；
- 自己连续点了两次更新；
- 无锁演示里本来就是并发写。

**处理**：

1. 重新 `GET /api/zk/nodes?path=...`，拿最新 `stat.version`；
2. 用新版本重试；
3. 如果业务上不需要防并发，传 `version: -1`（或省略）。

### 2.4 `404 NONODE`

**原因**：节点不存在。常见于：

- 路径拼错（大小写、少了层级）；
- 父节点没建，且没传 `createParents: true`；
- 应用重启后，之前的临时节点没了。

**处理**：

```bash
curl -s "$B/nodes/exists?path=/learn-zk/xxx"   # 先确认
curl -s "$B/nodes/children?path=/learn-zk"     # 看看到底有什么
```

### 2.5 `400 NOTEMPTY`

**原因**：节点下还有子节点，`delete` 默认只能删空节点。

**处理**：勾选「递归删除」，或传 `recursive=true`：

```bash
curl -X DELETE "$B/nodes?path=/learn-zk/lab&recursive=true"
```

注意递归删除不是原子操作，中途失败会留下部分删除的状态（[`04-crud-walkthrough.md`](04-crud-walkthrough.md) 6.3）。

### 2.6 `400 NOCHILDRENFOREPHEMERALS`

**原因**：试图给临时节点创建子节点。ZK 禁止这样做，因为父节点随会话消失，子节点没有归宿。

**处理**：把父节点改成 `PERSISTENT`，只让叶子节点是临时的。

### 2.7 `503 CONNECTIONLOSS` / `SESSIONEXPIRED`

**原因**：客户端与服务端的连接断了，或会话已过期。

**处理**：

1. 看应用日志里的连接状态：`[ZK] 连接状态变化 -> SUSPENDED / LOST`（`config/ZkConfig.java:36-37`）；
2. `SUSPENDED`：等重连，不要立刻做业务决策；
3. `LOST`：会话已过期，临时节点已被删除，需要重建；
4. 检查网络和 ZK 集群健康。

---

## 3. Watch

### 3.1 注册了监听，没有任何事件

按这个顺序排查：

| 检查项 | 说明 |
| --- | --- |
| 变化的是不是「同一层级」 | 监听父节点，不会收到子节点数据变化（[`05-watch-mechanism.md`](05-watch-mechanism.md) 3.1） |
| 节点在注册时存在吗 | 不存在也能注册 `exists` watch，等创建事件；但 `getChildren` 注册会失败 |
| 事件列表清空了吗 | `DELETE /api/zk/events` 会清空历史，别把「清空后没变化」误认为「监听失效」 |
| 应用重启过吗 | watch 不持久化，重启后全部失效（3.4） |
| 会话过期了吗 | 过期后 watch 全部失效，日志里会有 `LOST` |

### 3.2 同一事件出现两次

**历史原因**：早期版本在每次数据变化时都重新注册 children watch，导致服务端挂了多份 watch，一次变化推多个事件。

**当前实现**用 `childrenArmed` 去重（`service/ZkWatchService.java:44,82`），并且 children 监听只记录 `NodeChildrenChanged`，把 `NodeDeleted` 留给 exists 监听（`:87-90`）。

如果你仍然看到重复，检查是不是**注册了两次**：页面上重复点「注册监听」会调用两次 `watch(path)`，但 `childrenArmed` 会拦住重复的 children 注册；exists 监听则会真的注册多份（每次 `checkExists` 都是一份新 watch）。

**是否需要修**：演示场景可以接受；生产上应该用 `TreeCache`。

### 3.3 事件列表一直在涨

事件列表上限 200 条（`service/ZkWatchService.java:39,113-115`），超出后从队尾丢弃，不会无限增长。页面上可以手动清空。

### 3.4 应用重启后，之前的监听没了

**原因**：watch 是**会话级**的，存在服务端内存里，不持久化。应用重启 = 新会话 = 没有 watch。

**这正是 watch 和「配置订阅」的区别**：watch 不是消息队列，不保存历史。要「重启后继续监听」，必须在启动时重新注册，并做一次全量同步。

---

## 4. 分布式锁

### 4.1 抢锁超时

日志：

```
worker-3 #12 抢锁超时（30s），放弃任务
```

**原因**：

- 持锁者卡住了（死循环、慢 RPC、GC）；
- 线程数太多，排队超过 30s；
- 上一次演示的锁节点没释放（只可能发生在会话未过期的短时间内）。

**处理**：

1. 调小 `threads` / `tasksPerThread`；
2. 看 `GET /api/zk/lock/status` 里的队列长度和持锁者；
3. 确认没有别的实例在用同一个 `lockPath`。

### 4.2 每次实验结果数字都不一样

**这是正常的。** 无锁模式的丢失次数取决于线程调度、机器负载、`sleep` 的随机值。实测出现过 94/34、95/35、96/36 等结果。

稳定的结论是：

- 无锁：`lostUpdates > 0`；
- 加锁：`lostUpdates == 0`。

如果你想让它更稳定地「丢很多」，可以调大 `threads`；想让它「丢得少」，调小到 2~3 个线程。

### 4.3 队列里怎么有带 uuid 的长名字

```
_c_3f2a...-lock-0000000040
```

这是 Curator `withProtection()` 的命名，前缀用来防重复创建。**排序时只能看最后 10 位序号**，否则 uuid 会打乱顺序——本项目 `describeQueue` 已经处理了（`service/DistributedLockService.java:272-291`）。

### 4.4 加锁后慢了很多

**预期行为**。加锁把并行变成了串行：40 个任务 × 每个 10~40ms 的临界区，总耗时自然从 200ms 涨到 1.5s 左右。

优化方向：缩小临界区、减小 `sleep`、按资源分锁，而不是去掉锁。

### 4.5 找不到 `logs/zk-lock-demo.log`

**排查**：

1. 日志路径是相对工作目录的（`logback-spring.xml:9`）。从项目根目录启动，文件在 `logs/` 下；从 IDEA 启动，工作目录默认也是项目根目录；
2. 只有 logger 名为 `ZK_LOCK` 的日志才写这个文件（`service/DistributedLockService.java:41`），普通应用日志只进控制台；
3. 还没跑过锁演示时，文件可能不存在——先调一次 `POST /api/zk/lock/demo`；
4. `logs/` 在 `.gitignore` 里，不会提交。

页面上「分布式锁」页签第一次打开会自动加载这个文件（`index.html:525`）。

---

## 5. 环境与观察

### 5.1 代码里写 `/foo`，zoonavigator 里找不到

**原因**：`zk.namespace` 非空时，Curator 会在客户端加前缀，服务端实际路径是 `/<namespace>/foo`。

**处理**：在 zoonavigator 里按真实路径找，或把 namespace 置空（`application.yml:12`）。

### 5.2 怎么用 zkCli 对照

```bash
docker exec -it zoo1 /apache-zookeeper-3.9.5-bin/bin/zkCli.sh -server 127.0.0.1:2181
```

```text
ls /learn-zk/demo/users
get /learn-zk/demo/users/u001
stat /learn-zk/demo/users/u001
```

`stat` 输出里的 `version`、`cversion`、`ephemeralOwner` 和页面上看到的是同一份数据。

### 5.3 重启应用后，`/learn-zk/demo` 下的数据变了

**原因**：启动演示每次都会先清理再重建（`demo/ZkCrudDemoRunner.java:52-60`），最后保留 `u001`、`u003` 和临时节点 `session-001`。

**处理**：

- 想保留自己的数据：放在 `/learn-zk/demo` 之外；
- 想彻底清空：`DELETE /api/zk/nodes?path=/learn-zk&recursive=true`；
- 不想跑演示：`--zk.demo.enabled=false`。

### 5.4 临时节点为什么重启就没了

临时节点绑定会话。应用正常关闭 → `close()` → 会话结束 → 节点删除（`config/ZkConfig.java:23` 的 `destroyMethod`）。`kill -9` 则要等 30s 会话超时。

想验证：创建一个临时节点，停应用，再 `GET /nodes/exists`。

### 5.5 怎么确认数据真的写进 ZK 了，而不是只在内存里

三个独立视角：

1. 应用接口：`GET /api/zk/nodes?path=...`；
2. ZK 原生客户端：`zkCli.sh` 的 `get` / `stat`；
3. 独立界面：zoonavigator（<http://localhost:9000>）。

三者一致，才算真的落到了集群。

---

## 6. 排错通用顺序

遇到任何问题，按这个顺序走，通常三步内能定位：

```text
1. 健康检查      GET /api/zk/health           → 连接通不通
2. 看状态码      400/404/409/503 分别对应参数/路径/冲突/连接
3. 看日志        控制台 + logs/zk-lock-demo.log
4. 看真实数据    zkCli / zoonavigator
5. 对照代码      ZkExceptionHandler 的 explain() 已经写了下一步建议
```

第 5 步很有用：`web/ZkExceptionHandler.java:34-47` 为每种错误码补了一句「该怎么办」，前端弹出的提示就是它。

---

## 7. 还没解决的问题

以下现象如果出现，属于**已知边界**，不是配置问题：

| 现象 | 原因 | 建议 |
| --- | --- | --- |
| 持锁者 GC 停顿后出现两个持锁者 | ZK 只能按心跳判活 | 加 fencing token + 业务幂等（[`06-distributed-lock.md`](06-distributed-lock.md) 6） |
| 递归删除中途失败留下半棵树 | ZK 没有目录级事务 | 应用层补偿 / 重试 |
| 手写 watch 在大规模场景下事件风暴 | 监听粒度问题 | 改用 `TreeCache` |
| 应用启动强依赖 ZK | `blockUntilConnected` 直接抛异常 | 改成懒连接 + 降级 |

---

下一篇：回到 [`00-导读.md`](00-导读.md) 选择阅读路线。
