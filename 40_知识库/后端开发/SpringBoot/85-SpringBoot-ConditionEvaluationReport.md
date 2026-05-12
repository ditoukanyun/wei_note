---
title: SpringBoot ConditionEvaluationReport
date: 2026-05-11
tags:
  - springboot
  - java
  - 条件装配
module: 85-SpringBoot-condition-evaluation-report
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ConditionEvaluationReport

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/85-SpringBoot-condition-evaluation-report`

## 核心思路

本模块演示 Spring Boot 的 `ConditionEvaluationReport`：查看条件装配为什么匹配或不匹配，并把诊断结果过滤成稳定 API。

## 能力点

- `ConditionEvaluationReport`
- `ConditionOutcome`
- `ConditionAndOutcomes`
- `@ConditionalOnProperty`
- positive matches / negative matches
- 按 source 前缀过滤 report
- MockMvc 验证 API 输出

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ConditionEvaluationReport 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。
- Spring 扩展点案例先判断发生在启动生命周期的哪个阶段，再看具体代码。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ConditionEvaluationReportController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ConditionEvaluationReportController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/condition-evaluation-report")
public class ConditionEvaluationReportController {
    private final ConditionReportService conditionReportService;
    private final ConfigurableApplicationContext applicationContext;

    public ConditionEvaluationReportController(
            ConditionReportService conditionReportService,
            ConfigurableApplicationContext applicationContext) {
        this.conditionReportService = conditionReportService;
        this.applicationContext = applicationContext;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "85-SpringBoot-condition-evaluation-report",
                "topic", "Spring Boot ConditionEvaluationReport",
                "apis", List.of(
                        "GET /api/condition-evaluation-report",
                        "GET /api/condition-evaluation-report/summary"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/summary")
    public ApiResult<ConditionReportView> summary() {
        return ApiResult.success(
                conditionReportService.summarizeApplicationReport(applicationContext.getBeanFactory())
        );
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/condition/ConditionReportService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/condition/ConditionReportService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ConditionReportService {
    private static final String DEMO_SOURCE_FILTER = "com.cloud.condition";

    public ConditionReportView summarizeApplicationReport(ConfigurableListableBeanFactory beanFactory) {
        // Boot stores condition diagnostics in the BeanFactory during configuration class processing.
        return summarize(ConditionEvaluationReport.find(beanFactory), DEMO_SOURCE_FILTER);
    }

    public ConditionReportView summarize(ConditionEvaluationReport report, String sourceContains) {
        List<ConditionSourceView> sources = report.getConditionAndOutcomesBySource().entrySet().stream()
                .filter(entry -> entry.getKey().contains(sourceContains))
                .sorted(Map.Entry.comparingByKey())
                .map(this::toSourceView)
                .toList();
        long positiveMatches = sources.stream().filter(ConditionSourceView::isFullMatch).count();
        return new ConditionReportView(
                sources.size(),
                positiveMatches,
                sources.size() - positiveMatches,
                sources
        );
    }

    private ConditionSourceView toSourceView(Map.Entry<String, ConditionEvaluationReport.ConditionAndOutcomes> entry) {
        List<ConditionOutcomeView> outcomes = toOutcomeViews(entry.getValue());
        return new ConditionSourceView(entry.getKey(), entry.getValue().isFullMatch(), outcomes);
    }

    private List<ConditionOutcomeView> toOutcomeViews(ConditionEvaluationReport.ConditionAndOutcomes conditionAndOutcomes) {
        return orderedOutcomes(conditionAndOutcomes).stream()
                .map(conditionAndOutcome -> new ConditionOutcomeView(
                        conditionAndOutcome.getCondition().getClass().getSimpleName(),
                        conditionAndOutcome.getOutcome().isMatch(),
                        conditionAndOutcome.getOutcome().getMessage()
                ))
                .toList();
    }

    private List<ConditionEvaluationReport.ConditionAndOutcome> orderedOutcomes(
            ConditionEvaluationReport.ConditionAndOutcomes conditionAndOutcomes) {
        return conditionAndOutcomes == null
                ? List.of()
                : java.util.stream.StreamSupport.stream(conditionAndOutcomes.spliterator(), false)
                .sorted(Comparator.comparing(outcome -> outcome.getCondition().getClass().getName()))
                .toList();
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 条件装配：Bean 是否创建由谁决定

源码位置：`src/main/java/com/cloud/condition/ConditionOutcomeView.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/condition/ConditionOutcomeView.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ConditionOutcomeView {
    private String condition;
    private boolean match;
    private String message;
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 条件装配：Bean 是否创建由谁决定

源码位置：`src/main/java/com/cloud/condition/ConditionReportView.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/condition/ConditionReportView.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ConditionReportView {
    private int sourceCount;
    private long positiveMatches;
    private long negativeMatches;
    private List<ConditionSourceView> sources;
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

- 从 README 的接口或测试名称开始，先定位入口类。
- 找 Controller、Runner、Listener 或 AutoConfiguration 作为第一阅读点。
- 沿着构造器注入的依赖继续进入 Service、Repository 或扩展点类。

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。
- 把框架扩展点当普通业务代码使用，后续排查启动问题会很困难。

## API 接口

- `GET /api/condition-evaluation-report`：模块说明
- `GET /api/condition-evaluation-report/summary`：过滤后的条件报告摘要

## 调用验证

```bash
curl "http://localhost:8165/api/condition-evaluation-report"
```

```bash
curl "http://localhost:8165/api/condition-evaluation-report/summary"
```

`/summary` 核心响应：

```json
{
  "sourceCount": 2,
  "positiveMatches": 1,
  "negativeMatches": 1,
  "sources": [
    {
      "source": "com.cloud.condition.DemoFeatureConfig#enabledFeatureBean",
      "fullMatch": true
    },
    {
      "source": "com.cloud.condition.DemoFeatureConfig#missingFeatureBean",
      "fullMatch": false
    }
  ]
}
```

## 生产映射

生产系统可以用这个模式：

- 排查某个自动配置为什么没有生效
- 解释 `@ConditionalOnClass`、`@ConditionalOnProperty`、`@ConditionalOnMissingBean` 等条件结果
- 给支持工具暴露小范围 condition report，而不是直接暴露完整 actuator conditions
- 阅读 Spring Boot 源码时定位条件结果如何被记录和汇总

如果需要完整运行时诊断，Actuator `conditions` endpoint 更完整；如果只想解释某个业务 starter 或框架模块，按 source 过滤更清晰。

## 生产差距

该示例用于隔离学习 ConditionEvaluationReport 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 85-SpringBoot-condition-evaluation-report test
```

测试覆盖：

- 手动构造 `ConditionEvaluationReport` 并解析 positive / negative source
- source 过滤排除无关 report entries
- MockMvc 验证 metadata 接口
- MockMvc 验证真实应用上下文中的 matched / unmatched demo 条件

## 要点总结

1. `ConditionEvaluationReport`
2. `ConditionOutcome`
3. `ConditionAndOutcomes`
4. `@ConditionalOnProperty`
5. positive matches / negative matches

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
