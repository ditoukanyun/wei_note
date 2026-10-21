---
type: reference
status: archived
created: 2026-10-21
area: "[[后端开发]]"
tags: [Java, 技术分享, ElasticJob, 前端类比]
---
# ElasticJob 分享讲稿：从前端定时器到分片任务

> [!info] 本篇定位
> 这是独立的一篇定时任务分享，面向有 Java 基础的同事。建议 30 分钟，包含演示与问答。通过前端定时器建立直觉，使用两个实例补偿 12 笔订单，最后带走任务代码模板。

## 分享节奏

| 环节 | 时间 |
| --- | --- |
| 前端定时器与多实例问题 | 3 分钟 |
| 最小 Job 与业务分层 | 4 分钟 |
| Cron 和公共参数 | 3 分钟 |
| 分片编号、分片参数与数据范围 | 5 分钟 |
| 双实例与失败重跑演示 | 8 分钟 |
| 故障恢复与幂等 | 4 分钟 |
| 任务模板 | 1 分钟 |
| 问答 | 2 分钟 |

## 第一部分：从前端定时器开始（3 分钟）

展示熟悉的轮询：

```javascript
// refreshOrders 代表业务函数，示意代码不需要在案例中运行。
setInterval(() => refreshOrders(), 5000);
```

“定时器决定什么时候调用，回调决定执行什么。打开两个标签页，每个页面注册一套定时器，就会各自发起请求。独立运行的环境有独立触发逻辑。”

接着展示 Node.js：

```javascript
import schedule from 'node-schedule';
schedule.scheduleJob('0 0 * * *', () => compensateOrders());
```

“如果两个 Node.js 进程都注册补偿任务，又都扫描全部订单，仍要解决重复处理。Java 服务部署两份也会遇到同类问题。”

Node Schedule 属于进程内调度；浏览器计时也有执行延迟和生命周期限制。类比用于解释触发，跨实例的工作归属需要继续设计。依据：[Node Schedule](https://github.com/node-schedule/node-schedule)、[MDN 定时器](https://developer.mozilla.org/en-US/docs/Web/API/Window/setInterval)。

本篇用 ElasticJob 将任务划分为逻辑分片，协调到应用实例执行。

## 第二部分：写一个最小 Job（4 分钟）

| 熟悉的写法 | ElasticJob 中的角色 |
| --- | --- |
| 定时回调 | `SimpleJob.execute(context)` |
| 业务函数 | Service 的业务方法 |
| 注册调度 | `JobConfiguration` 与 `ScheduleJobBootstrap` |
| 任务标识 | `jobName` |

实际入口：

```java
@Override
public void execute(ShardingContext context) {
    var result = service.execute(context.getShardingItem(),
            context.getShardingParameter(), context.getJobParameter());
    if (result.failed() > 0) {
        throw new IllegalStateException("分片存在失败订单，请查看业务执行记录");
    }
}
```

“Job 是一个薄入口，提取上下文并交给 Service。按区域查询、处理订单、记录失败都在业务层，便于复用与验证。”

打开案例三个文件：

- `JobInfrastructure.java`：定义和注册任务。
- `CompensationJob.java`：调度入口。
- `CompensationService.java` / `OrderProcessor.java`：分批业务与单笔事务。

本案例参数来自本地 `application.yaml`，并在 `TaskSettings` 中校验。今天不讲运行时动态刷新，操作任务无需启动配置中心。

接口依据：[ElasticJob 作业开发](https://shardingsphere.apache.org/elasticjob/current/en/user-manual/usage/job-api/job-interface/)。

## 第三部分：何时触发、传什么参数（3 分钟）

```java
JobConfiguration config = JobConfiguration.newBuilder("order-compensation-job", 3)
    .cron("0 0 0 * * ?")
    .timeZone("GMT+08:00")
    .shardingItemParameters("0=华东,1=华南,2=华北")
    .jobParameter("pending")
    .monitorExecution(true).failover(false).misfire(false)
    .jobErrorHandlerType("LOG").overwrite(true).build();
```

“这里固定每天北京时间零点触发。现场使用手动触发，不用等到明天。`pending` 是我们自行约定的公共参数，代表只处理待补偿订单，不是框架内置业务模式。”

Node 示例使用五字段 Cron，本例使用带秒的六字段表达式，不能直接复制；案例固定为 ElasticJob 3.0.4，显式时区使用 GMT 格式。`overwrite=true` 表示示例以代码任务定义为准，实际团队要统一配置权威来源。

依据：[Java 调度 API](https://shardingsphere.apache.org/elasticjob/current/en/user-manual/usage/job-api/java-api/)、[任务配置](https://shardingsphere.apache.org/elasticjob/current/en/user-manual/configuration/)。

## 第四部分：分片怎样变成数据分工（5 分钟）

用前端分组处理建立直觉：

```javascript
const regions = ['华东', '华南', '华北'];
const region = regions[shardIndex];
const currentOrders = orders.filter(order => order.region === region);
```

“数组有三个工作单元，但不一定要三个执行者。框架将三份工作分给两个实例，一个实例可能承担多个分片。”

| 名称 | 本例 | 作用 |
| --- | --- | --- |
| `shardingTotalCount` | 3 | 逻辑工作单元数量 |
| `shardingItem` | 0 / 1 / 2 | 当前分片编号 |
| `getShardingParameter()` | 华东 / 华南 / 华北 | 对应分片的业务范围 |
| `getJobParameter()` | pending | 所有分片共用的业务参数 |

框架分配分片，业务必须真的按范围查询：

```sql
SELECT order_id FROM compensation_order
WHERE region = ? AND status = 'PENDING'
ORDER BY order_id LIMIT ?;
```

“如果没有这个区域条件，每个分片仍可能处理全量数据。分片数量也不能等同于线程数或机器数。”

按区域有数据倾斜的可能，生产环境可按 ID、租户等划分。`Promise.all` 可以帮助解释并行处理，但单进程并行与跨实例协调是不同能力。更完整类比见 [[前端定时器与ElasticJob类比讲解]]。

协调能力依据：[ElasticJob 弹性调度](https://shardingsphere.apache.org/elasticjob/current/en/features/elastic/)。

## 第五部分：双实例执行与失败补偿（8 分钟）

按 [[ElasticJob演示手册]] 操作：

1. 展示两个任务实例、12 笔待补偿订单，订单按三个区域分布。
2. 点击“触发一次任务”，观察两个实例分担三个分片。
3. 结果为 11 笔成功、1005 待补偿、11 条业务流水。
4. 指出失败分片中的其他订单已经成功，1005 保留失败原因。
5. 点击“恢复模拟依赖”，再次触发。
6. 结果为 12 笔成功、12 条流水。1005 尝试两次，其他订单各一次。
7. 再触发一次，流水与订单尝试次数保持原值。

“手动触发就像页面上点重新执行：让任务现在进入处理路径。究竟补哪些订单，由本例的待补偿状态决定，不是自动回放历史失败输入。”

中文演示台通过真实 `JobOperateAPI.trigger()` 触发框架；本例没有打包官方 ElasticJob UI，执行记录由业务自行持久化。参考：[操作 API](https://shardingsphere.apache.org/elasticjob/current/en/user-manual/usage/operation-api/)。

## 第六部分：失败恢复和幂等分别解决什么（4 分钟）

| 问题 | 机制 |
| --- | --- |
| 下游超时，某笔业务失败 | 保留失败状态，受控重试或修复后补偿 |
| 执行实例宕机 | 根据配置使用 failover，或后续调度重新分配 |
| 上一轮过长，错过触发 | 根据需求使用 misfire |
| 同一订单再次进入处理 | 幂等保护 |

“前端按钮置灰或 `inFlight` 标记只能保护当前页面的入口，换个标签页仍可能再次请求。幂等需要保护业务操作本身。”

展示 `OrderProcessor.java`：

1. 事务中锁定订单行。
2. 拿锁后重新检查是否已成功。
3. 写入以订单号为唯一键的业务流水。
4. 更新成功状态，与流水在同一事务提交。

本例用同库流水表示业务效果，事务可以覆盖；换成真实退款或发消息时，需要下游幂等键、Outbox 或对账恢复设计。

错误处理器 `LOG` 不代表业务自动重试；failover、misfire 和业务失败补偿也不能混为一谈。主演示关闭 failover / misfire，便于稳定观察手动补偿。依据：[failover](https://shardingsphere.apache.org/elasticjob/current/en/features/failover/)、[misfire](https://shardingsphere.apache.org/elasticjob/current/en/features/misfire/)、[错误处理器](https://shardingsphere.apache.org/elasticjob/current/en/user-manual/configuration/built-in-strategy/error-handler/)。

## 第七部分：带走任务模板（1 分钟）

展示 [[ElasticJob任务代码模板]]：注册配置 → Job 入口 → Service 分批处理 → 单笔事务 → 执行记录与补偿说明。

“新增任务时，先替换业务范围与处理逻辑，再验证正常执行、失败恢复、重复执行和分片范围。”

## 问答（2 分钟）

**一个分片是不是只会执行一次？**

正常协调安排实例归属，故障和重跑仍可能重复进入业务处理，业务效果需要幂等。

**`setInterval(async () => ...)` 会等上一次完成吗？**

不会自动等待返回的 Promise，异步操作可能重叠。递归 `setTimeout` 配合 `await` 可以做完成后再等待的轮询，它仍不等同于多实例协调。参考：[MDN 执行耗时说明](https://developer.mozilla.org/en-US/docs/Web/API/Window/setInterval#ensure_that_execution_duration_is_shorter_than_interval_frequency)。

**控制台重跑是不是只跑失败订单？**

本例重新调度所有分片，由业务查询筛出待补偿订单。指定历史日期等能力需要额外参数设计。
