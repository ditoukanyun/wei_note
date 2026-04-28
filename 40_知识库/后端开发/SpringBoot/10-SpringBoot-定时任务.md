---
title: SpringBoot 定时任务
date: 2026-04-20
tags:
  - springboot
  - java
  - 定时任务
  - schedule
module: 10-SpringBoot-schedule-async
---
# SpringBoot 定时任务

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/10-SpringBoot-schedule-async`

## 项目结构

```
10-SpringBoot-schedule-async/
└── src/main/java/com/cloud/
    ├── config/SchedulingConfig.java     # 调度配置
    ├── task/
    │   ├── HeartbeatTask.java           # fixedRate 心跳
    │   ├── CleanupTask.java             # fixedDelay 清理
    │   └── ReportTask.java             # cron 报表
    ├── service/TaskLogService.java      # 任务日志（内存）
    ├── controller/TaskDemoController.java
    └── vo/TaskLogVO.java
```

## 开启调度

启动类加 `@EnableScheduling`：

```java
@EnableScheduling
@SpringBootApplication
public class Application { ... }
```

## 三种调度方式

### 配置

```yaml
demo:
  task:
    enabled: true
    heartbeat:
      fixed-rate: 10000      # 10秒
    cleanup:
      fixed-delay: 15000     # 15秒
    report:
      cron: "0/30 * * * * ?" # 每30秒
```

### fixedRate — 固定频率

```java
@Scheduled(fixedRateString = "${demo.task.heartbeat.fixed-rate}")
public void schedule() { ... }
```

- 从**上一次开始时间**算起，每隔 N ms 执行
- 不等待上次完成，任务可能重叠
- 适合：心跳、轮询等频率固定的场景

### fixedDelay — 固定延迟

```java
@Scheduled(fixedDelayString = "${demo.task.cleanup.fixed-delay}")
public void schedule() { ... }
```

- 上次执行**完成后**等待 N ms 再执行
- 不会重叠
- 适合：清理、同步等必须顺序执行的任务

### cron — 表达式调度

```java
@Scheduled(cron = "${demo.task.report.cron}")
public void schedule() { ... }
```

Cron 表达式格式：`秒 分 时 日 月 周`

| 表达式 | 说明 |
|--------|------|
| `0/30 * * * * ?` | 每 30 秒 |
| `0 0 2 * * ?` | 每天凌晨 2 点 |
| `0 0 9-17 * * ?` | 每小时整点（9-17点） |
| `0 0/5 * * * ?` | 每 5 分钟 |
| `0 0 0 1 * ?` | 每月 1 日零点 |

### 对比

| 方式 | 计算基准 | 是否重叠 | 适用场景 |
|------|----------|---------|---------|
| `fixedRate` | 上次开始时间 | 可能 | 固定频率巡检 |
| `fixedDelay` | 上次结束时间 | 不会 | 顺序型清理 |
| `cron` | 时间表达式 | 可能 | 定时报表 |

## 配置外部化

```java
@Scheduled(fixedRateString = "${demo.task.heartbeat.fixed-rate}")
```

- `fixedRateString` / `fixedDelayString` 支持从配置文件读取
- 比硬编码 `fixedRate = 10000` 更灵活，不同环境可配不同值

## 任务开关

```java
@Value("${demo.task.enabled:true}")
private boolean taskEnabled;

@Scheduled(fixedRateString = "...")
public void schedule() {
    if (!taskEnabled) return;  // 配置关闭则跳过
    runTask("AUTO");
}
```

## 手动触发

定时任务类注入 Controller，公开 `runTask` 方法：

```java
@PostMapping("/run/heartbeat")
public ApiResult<Void> runHeartbeat() {
    heartbeatTask.runTask("MANUAL");   // 手动触发，区分触发类型
    return ApiResult.success();
}
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/logs` | 查看任务执行日志 |
| POST | `/api/tasks/run/heartbeat` | 手动触发心跳 |
| POST | `/api/tasks/run/cleanup` | 手动触发清理 |
| POST | `/api/tasks/run/report` | 手动触发报表 |

## 要点总结

1. **`@EnableScheduling`**：启动类必须加，否则 `@Scheduled` 不生效
2. **三种调度**：fixedRate（频率）、fixedDelay（延迟）、cron（表达式）
3. **配置外部化**：`fixedRateString` 从 yml 读取，避免硬编码
4. **任务开关**：配置 `enabled` 字段控制是否执行
5. **手动触发**：公开方法供 API 调用，区分 AUTO/MANUAL 触发类型
