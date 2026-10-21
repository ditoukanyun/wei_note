---
type: reference
created: 2026-10-21
area: "[[后端开发]]"
tags: [Java, ElasticJob, 代码模板, 幂等]
---
# ElasticJob 任务代码模板

这份模板直接对应 `案例/src/main/java/cn/orbit/share/` 下的可编译代码，依赖固定为 ElasticJob 3.0.4。复制到其他版本前，先核对包名与 API。

## 1. 建议分层

| 文件 | 职责 | 新增任务时替换什么 |
| --- | --- | --- |
| `JobInfrastructure.java` | 注册中心、任务名、Cron、分片与框架策略 | 调度与分片定义 |
| `CompensationJob.java` | 将 `ShardingContext` 转成业务参数 | 新任务对应的 Service |
| `CompensationService.java` | 读取快照、按范围查询、逐笔处理、汇总结果 | 业务筛选条件与结果记录 |
| `OrderProcessor.java` | 单笔事务、幂等、业务效果落库 | 真正的业务处理 |
| `TaskSettings.java` | 读取本地任务参数 | 新任务所需的本地业务参数 |

## 2. 最小 Job 入口

以下结构来自案例，完整类包含在源码中：

```java
import org.apache.shardingsphere.elasticjob.api.ShardingContext;
import org.apache.shardingsphere.elasticjob.simple.job.SimpleJob;

public class CompensationJob implements SimpleJob {
    private final CompensationService service;

    public CompensationJob(CompensationService service) {
        this.service = service;
    }

    @Override
    public void execute(ShardingContext context) {
        var result = service.execute(context.getShardingItem(),
                context.getShardingParameter(), context.getJobParameter());
        if (result.failed() > 0) {
            throw new IllegalStateException("分片存在失败订单，请查看业务执行记录");
        }
    }
}
```

Spring 场景中将 Job 注册为 Bean，通过构造器注入 Service，并传给 `ScheduleJobBootstrap`。本案例没有同时给这个 Job 添加 `@Scheduled`，避免形成两条调度路径。

## 3. 业务执行模板

每次分片调用采用以下顺序：

1. 读取不可变配置快照，生成本次分片调用的执行标识。
2. 记录任务、实例、分片、参数与配置版本。
3. 开关关闭则记录 `SKIPPED` 并返回。
4. 校验任务参数，确定业务数据范围。
5. 按范围和待处理状态查询，限制单批数量。
6. 逐笔调用独立 Bean 的事务方法，记录成功、失败与幂等跳过。
7. 汇总持久化本分片结果，失败按策略向框架暴露。

`execution_id` 在本例标识一次分片调用，同一调度触发的三个分片会有三个标识；它不承担跨分片的全局批次身份。

## 4. 单笔幂等模板

本案例在同一个数据库事务中完成：

```sql
-- 先锁定并读取，拿到锁后重新判断业务状态。
SELECT * FROM compensation_order WHERE order_id = ? FOR UPDATE;

-- 如果已成功则返回；否则完成本地业务效果与状态变更。
INSERT INTO compensation_effect(order_id, instance_id) VALUES (?, ?);
UPDATE compensation_order
SET status = 'SUCCESS', last_error = NULL, completed_by = ?
WHERE order_id = ?;
```

`compensation_effect.order_id` 有唯一约束。业务方法使用 `@Transactional`，由另一个 Bean 调用以经过事务代理。

本模板覆盖“一个订单在本数据库里产生一次补偿流水”。如果同一订单允许多种补偿事件，业务唯一键应扩展为合适的组合，例如订单号与补偿类型；如果涉及远端退款，必须设计下游幂等键和对账恢复。

## 5. 框架策略必须显式选择

| 项 | 案例取值 | 选择原因 |
| --- | --- | --- |
| 分片数 | 3 | 对应三个区域，两个实例分担 |
| Cron | 每天零点，GMT+08:00 | 北京时间；该版本显式时区要求 GMT 格式 |
| `monitorExecution` | true | 观察运行状态与避免正常调度重入 |
| `failover` | false | 主演示聚焦业务失败补偿 |
| `misfire` | false | 避免额外补触发干扰现场结果 |
| 错误处理器 | LOG | 记录汇总异常；不提供自动业务重试 |
| `overwrite` | true | 教学任务配置以代码为准 |

生产任务需要按时效、执行时长、调度密度和配置管理方式重新选择，不应直接照搬这些开关。

## 6. 迁移新任务时验证什么

- 关闭开关后没有新增业务效果。
- 同一个业务键并发执行，只产生预期的一份效果。
- 不同分片处理的数据范围不重叠，范围全集符合业务预期。
- 一笔失败后，其他数据的处理与恢复策略符合预期。
- 重跑依靠明确状态、日期或业务参数选取数据。
- 业务效果与本地状态变更发生异常时能按设计回滚或恢复。

对应测试可参考 `OrderProcessorTest.java`，端到端演示见 `scripts/验证定时任务.py`。
