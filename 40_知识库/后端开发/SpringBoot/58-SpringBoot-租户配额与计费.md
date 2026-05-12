---
title: SpringBoot 租户配额与计费
date: 2026-05-11
tags:
  - springboot
  - java
  - 多租户
  - 计费
module: 58-SpringBoot-tenant-quota-billing
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 租户配额与计费

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/58-SpringBoot-tenant-quota-billing`

## 核心思路

本模块演示 SaaS 租户配额与计量计费原型：为租户配置套餐和账期，记录用量，计算预估费用，并根据软限制和硬限制返回 `ALLOW`、`WARN` 或 `BLOCK` 决策。

## 能力点

- 租户配额配置
- 用量计量
- 费用预估
- 软限制预警
- 硬限制阻断
- 账期重置
- 业务决策解释

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 租户配额与计费 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。
- 认证/上下文类案例要特别关注“在哪里写入、在哪里校验、在哪里清理”。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/TenantQuotaBillingController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/TenantQuotaBillingController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/tenant-billing")
public class TenantQuotaBillingController {
    private final TenantQuotaBillingService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public TenantQuotaBillingController(TenantQuotaBillingService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "58-SpringBoot-tenant-quota-billing");
        data.put("desc", "租户配额、用量计量、软硬限制和账期重置");
        data.put("apis", new String[]{
                "GET /api/tenant-billing",
                "POST /api/tenant-billing/quotas",
                "GET /api/tenant-billing/quotas",
                "POST /api/tenant-billing/usages",
                "GET /api/tenant-billing/usages/{tenantId}",
                "POST /api/tenant-billing/tenants/{tenantId}/reset-period"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/quotas")
    public ApiResult<TenantUsageSummary> configureQuota(@RequestBody TenantQuota quota) {
        return ApiResult.success(service.configureQuota(quota));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/quotas")
    public ApiResult<List<TenantQuota>> quotas() {
        return ApiResult.success(service.quotas());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/usages")
    public ApiResult<TenantUsageSummary> recordUsage(@RequestBody UsageRecordRequest request) {
        return ApiResult.success(service.recordUsage(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/usages/{tenantId}")
    public ApiResult<TenantUsageSummary> summary(@PathVariable String tenantId) {
        return ApiResult.success(service.summary(tenantId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/tenants/{tenantId}/reset-period")
    public ApiResult<TenantUsageSummary> resetPeriod(@PathVariable String tenantId,
                                                     @RequestBody ResetBillingPeriodRequest request) {
        request.setTenantId(tenantId);
        return ApiResult.success(service.resetPeriod(request));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/TenantQuotaBillingService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/TenantQuotaBillingService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class TenantQuotaBillingService {
    private final TenantBillingRepository repository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public TenantQuotaBillingService(TenantBillingRepository repository) {
        this.repository = repository;
    }

    public TenantUsageSummary configureQuota(TenantQuota quota) {
        validateQuota(quota);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveQuota(quota);
        TenantUsageSummary summary = new TenantUsageSummary(
                quota.getTenantId(),
                quota.getPlanName(),
                quota.getMetricCode(),
                quota.getPeriodStart(),
                quota.getPeriodEnd(),
                0,
                money(BigDecimal.ZERO),
                decide(quota, 0)
        );
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.saveSummary(summary);
    }

    public TenantUsageSummary recordUsage(UsageRecordRequest request) {
        validateUsage(request);
        TenantQuota quota = findQuota(request.getTenantId());
        TenantUsageSummary summary = repository.findSummary(request.getTenantId())
                .orElseGet(() -> emptySummary(quota));
        int usedQuantity = summary.getUsedQuantity() + request.getQuantity();
        summary.setUsedQuantity(usedQuantity);
        summary.setEstimatedCharge(calculateCharge(quota, usedQuantity));
        summary.setDecision(decide(quota, usedQuantity));
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.saveSummary(summary);
    }

    public TenantUsageSummary summary(String tenantId) {
        if (isBlank(tenantId)) throw new IllegalArgumentException("tenantId 不能为空");
        findQuota(tenantId);
        return repository.findSummary(tenantId).orElseThrow(() -> new NoSuchElementException("用量汇总不存在: " + tenantId));
    }

    public List<TenantQuota> quotas() {
        return repository.quotas().stream().sorted(Comparator.comparing(TenantQuota::getTenantId)).toList();
    }

    public List<TenantUsageSummary> summaries() {
        return repository.summaries().stream().sorted(Comparator.comparing(TenantUsageSummary::getTenantId)).toList();
    }

    public TenantUsageSummary resetPeriod(ResetBillingPeriodRequest request) {
        validateReset(request);
        TenantQuota quota = findQuota(request.getTenantId());
        quota.setPeriodStart(request.getPeriodStart());
        quota.setPeriodEnd(request.getPeriodEnd());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveQuota(quota);

        // Period rollover keeps the plan configuration but clears metered usage for the new cycle.
        TenantUsageSummary summary = emptySummary(quota);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.saveSummary(summary);
    }

    private TenantUsageSummary emptySummary(TenantQuota quota) {
        return new TenantUsageSummary(
                quota.getTenantId(),
                quota.getPlanName(),
                quota.getMetricCode(),
                quota.getPeriodStart(),
                quota.getPeriodEnd(),
                0,
                money(BigDecimal.ZERO),
                decide(quota, 0)
        );
    }

    private QuotaDecision decide(TenantQuota quota, int usedQuantity) {
        int remaining = Math.max(0, quota.getHardLimit() - usedQuantity);
        // Soft limit warns the caller; only usage above the hard limit blocks new expensive work.
        if (usedQuantity > quota.getHardLimit()) {
            return new QuotaDecision(QuotaStatus.BLOCK, "HARD_LIMIT_EXCEEDED", "用量已超过硬限制", remaining);
        }
        if (usedQuantity >= quota.getSoftLimit()) {
            return new QuotaDecision(QuotaStatus.WARN, "SOFT_LIMIT_REACHED", "用量已达到软限制", remaining);
        }
        return new QuotaDecision(QuotaStatus.ALLOW, "UNDER_LIMIT", "用量低于软限制", remaining);
    }

    private BigDecimal calculateCharge(TenantQuota quota, int usedQuantity) {
        return money(quota.getUnitPrice().multiply(BigDecimal.valueOf(usedQuantity)));
    }

    private BigDecimal money(BigDecimal value) {
        return value.setScale(2, RoundingMode.HALF_UP);
    }

    private TenantQuota findQuota(String tenantId) {
        return repository.findQuota(tenantId).orElseThrow(() -> new NoSuchElementException("租户配额不存在: " + tenantId));
    }

    private void validateQuota(TenantQuota quota) {
        if (quota == null) throw new IllegalArgumentException("quota 不能为空");
        if (isBlank(quota.getTenantId())) throw new IllegalArgumentException("tenantId 不能为空");
        if (isBlank(quota.getPlanName())) throw new IllegalArgumentException("planName 不能为空");
        if (isBlank(quota.getMetricCode())) throw new IllegalArgumentException("metricCode 不能为空");
        if (quota.getSoftLimit() < 0) throw new IllegalArgumentException("softLimit 不能小于 0");
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/billing/TenantBillingRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/billing/TenantBillingRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class TenantBillingRepository {
    private final Map<String, TenantQuota> quotas = new ConcurrentHashMap<>();
    private final Map<String, TenantUsageSummary> summaries = new ConcurrentHashMap<>();

    public TenantQuota saveQuota(TenantQuota quota) {
        quotas.put(quota.getTenantId(), quota);
        return quota;
    }

    public Optional<TenantQuota> findQuota(String tenantId) {
        return Optional.ofNullable(quotas.get(tenantId));
    }

    public List<TenantQuota> quotas() {
        return new ArrayList<>(quotas.values());
    }

    public TenantUsageSummary saveSummary(TenantUsageSummary summary) {
        summaries.put(summary.getTenantId(), summary);
        return summary;
    }

    public Optional<TenantUsageSummary> findSummary(String tenantId) {
        return Optional.ofNullable(summaries.get(tenantId));
    }

    public List<TenantUsageSummary> summaries() {
        return new ArrayList<>(summaries.values());
    }
}
```

关键点拆解：

- 示例里的 Repository 多半是内存实现；真实项目要替换成数据库、缓存或外部服务。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：GlobalExceptionHandler

源码位置：`src/main/java/com/cloud/exception/GlobalExceptionHandler.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/exception/GlobalExceptionHandler.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler({IllegalArgumentException.class, NoSuchElementException.class})
    @ResponseStatus(BAD_REQUEST)
    public ApiResult<Void> handleBadRequest(RuntimeException exception) {
        return ApiResult.fail(400, exception.getMessage());
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. TenantQuotaBillingController：接收 HTTP 请求并转换成 Java 方法调用
2. TenantQuotaBillingService：执行案例的核心业务规则
3. TenantBillingRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。
- 使用 `ThreadLocal` 后忘记清理，在线程池环境会造成上下文串号。

## API 接口

- `GET /api/tenant-billing`：模块说明
- `POST /api/tenant-billing/quotas`：创建或替换租户配额
- `GET /api/tenant-billing/quotas`：查询配额列表
- `POST /api/tenant-billing/usages`：记录一次用量
- `GET /api/tenant-billing/usages/{tenantId}`：查询租户当前用量汇总
- `POST /api/tenant-billing/tenants/{tenantId}/reset-period`：重置租户账期

## 调用验证

```bash
curl -X POST "http://localhost:8138/api/tenant-billing/quotas" \
  -H "Content-Type: application/json" \
  -d '{"tenantId":"tenant-a","planName":"标准版","metricCode":"api-call","softLimit":900,"hardLimit":1000,"unitPrice":0.01,"periodStart":"2026-05-01","periodEnd":"2026-05-31"}'
```

```bash
curl -X POST "http://localhost:8138/api/tenant-billing/usages" \
  -H "Content-Type: application/json" \
  -d '{"tenantId":"tenant-a","quantity":125,"source":"gateway","occurredDate":"2026-05-08"}'
```

```bash
curl -X POST "http://localhost:8138/api/tenant-billing/tenants/tenant-a/reset-period" \
  -H "Content-Type: application/json" \
  -d '{"periodStart":"2026-06-01","periodEnd":"2026-06-30"}'
```

## 生产映射

本模块使用内存仓储。生产环境通常替换为：

- 租户订阅表：套餐、账期、配额、价格
- 用量事件表：网关、任务、存储或 AI 调用产生的计量事件
- 用量汇总表：按租户、指标、账期聚合
- 幂等消费：避免重复计量
- 配额拦截：在高成本操作前检查剩余额度
- 账期任务：定时滚动账期并生成对账数据
- 下游账单：发票、收款、折扣、税费等独立处理

## 生产差距

该示例用于隔离学习 租户配额与计费 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 58-SpringBoot-tenant-quota-billing test
```

## 要点总结

1. 租户配额配置
2. 用量计量
3. 费用预估
4. 软限制预警
5. 硬限制阻断

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
