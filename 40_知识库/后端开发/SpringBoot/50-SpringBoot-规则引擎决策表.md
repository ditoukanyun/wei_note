---
title: SpringBoot 规则引擎决策表
date: 2026-05-11
tags:
  - springboot
  - java
  - 规则引擎
module: 50-SpringBoot-rule-engine-decision-table
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 规则引擎决策表

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/50-SpringBoot-rule-engine-decision-table`

## 核心思路

本模块演示规则引擎里的决策表原型：创建规则版本，发布某个版本为当前生效版本，按优先级匹配规则，并返回可解释的执行结果。

## 能力点

- 决策表建模
- 规则版本发布
- 单表单活跃版本
- 优先级匹配
- 条件执行解释
- 默认输出兜底

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 规则引擎决策表 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/DecisionTableController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/DecisionTableController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/rules")
public class DecisionTableController {

    private final DecisionTableService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DecisionTableController(DecisionTableService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "50-SpringBoot-rule-engine-decision-table");
        data.put("desc", "决策表规则、优先级匹配、可解释执行结果和规则版本发布");
        data.put("apis", new String[]{
                "GET /api/rules",
                "POST /api/rules/versions",
                "POST /api/rules/versions/{versionId}/publish",
                "GET /api/rules/versions",
                "GET /api/rules/tables/{tableId}/published",
                "POST /api/rules/tables/{tableId}/decisions"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/versions")
    public ApiResult<RuleVersion> createVersion(@RequestBody CreateRuleVersionRequest request) {
        return ApiResult.success(service.createVersion(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/versions/{versionId}/publish")
    public ApiResult<RuleVersion> publish(@PathVariable String versionId) {
        return ApiResult.success(service.publish(versionId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/versions")
    public ApiResult<List<RuleVersion>> versions() {
        return ApiResult.success(service.versions());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/tables/{tableId}/published")
    public ApiResult<RuleVersion> publishedVersion(@PathVariable String tableId) {
        return ApiResult.success(service.publishedVersion(tableId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/tables/{tableId}/decisions")
    public ApiResult<DecisionResult> decide(@PathVariable String tableId, @RequestBody DecisionRequest request) {
        return ApiResult.success(service.evaluate(tableId, request));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/DecisionTableService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/DecisionTableService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class DecisionTableService {

    private final DecisionTableRepository repository;
    private final Clock clock;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DecisionTableService(DecisionTableRepository repository) {
        this(repository, Clock.systemUTC());
    }

    public DecisionTableService(DecisionTableRepository repository, Clock clock) {
        this.repository = repository;
        this.clock = clock;
    }

    public RuleVersion createVersion(CreateRuleVersionRequest request) {
        validateVersion(request);
        RuleVersion version = new RuleVersion(
                UUID.randomUUID().toString(),
                request.getTableId(),
                request.getVersion(),
                request.getDescription(),
                RuleVersionStatus.DRAFT,
                request.getRules(),
                request.getDefaultOutcome() == null ? Map.of() : request.getDefaultOutcome(),
                clock.instant(),
                null
        );
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.save(version);
        return version;
    }

    public RuleVersion publish(String versionId) {
        RuleVersion version = findVersion(versionId);
        repository.findPublished(version.getTableId()).ifPresent(active -> {
            active.setStatus(RuleVersionStatus.ARCHIVED);
            active.setPublishedAt(null);
        });
        version.setStatus(RuleVersionStatus.PUBLISHED);
        version.setPublishedAt(clock.instant());
        repository.publish(version);
        return version;
    }

    public RuleVersion findVersion(String versionId) {
        return repository.findById(versionId)
                .orElseThrow(() -> new NoSuchElementException("规则版本不存在: " + versionId));
    }

    public RuleVersion publishedVersion(String tableId) {
        return repository.findPublished(tableId)
                .orElseThrow(() -> new NoSuchElementException("规则表未发布: " + tableId));
    }

    public List<RuleVersion> versions() {
        return repository.findAll().stream()
                .sorted(Comparator.comparing(RuleVersion::getCreatedAt))
                .toList();
    }

    public DecisionResult evaluate(String tableId, DecisionRequest request) {
        RuleVersion version = publishedVersion(tableId);
        Map<String, Object> facts = request == null || request.getFacts() == null ? Map.of() : request.getFacts();
        List<RuleCheck> checkedRules = new ArrayList<>();

        for (DecisionRule rule : sortedRules(version)) {
            RuleCheck check = evaluateRule(rule, facts);
            checkedRules.add(check);
            if (check.isMatched()) {
                return new DecisionResult(tableId, version.getVersion(), true, rule.getRuleId(), rule.getOutcome(), checkedRules);
            }
        }

        return new DecisionResult(tableId, version.getVersion(), false, null, version.getDefaultOutcome(), checkedRules);
    }

    private List<DecisionRule> sortedRules(RuleVersion version) {
        if (version.getRules() == null) {
            return List.of();
        }
        return version.getRules().stream()
                .sorted(Comparator.comparingInt(DecisionRule::getPriority).reversed()
                        .thenComparing(DecisionRule::getRuleId))
                .toList();
    }

    private RuleCheck evaluateRule(DecisionRule rule, Map<String, Object> facts) {
        if (!rule.isEnabled()) {
            return new RuleCheck(rule.getRuleId(), rule.getName(), rule.getPriority(), false, "规则已禁用", List.of());
        }

        List<ConditionCheck> conditionChecks = new ArrayList<>();
        boolean matched = true;
        for (RuleCondition condition : rule.getConditions() == null ? List.<RuleCondition>of() : rule.getConditions()) {
            Object actual = facts.get(condition.getField());
            boolean conditionMatched = matches(condition, actual);
            conditionChecks.add(new ConditionCheck(
                    condition.getField(),
                    condition.getOperator(),
                    condition.getExpected(),
                    actual,
                    conditionMatched
            ));
            if (!conditionMatched) {
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 条件装配：Bean 是否创建由谁决定

源码位置：`src/main/java/com/cloud/rule/ConditionCheck.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/rule/ConditionCheck.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ConditionCheck {

    private String field;
    private RuleOperator operator;
    private Object expected;
    private Object actual;
    private boolean matched;
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 条件装配：Bean 是否创建由谁决定

源码位置：`src/main/java/com/cloud/rule/RuleCondition.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/rule/RuleCondition.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RuleCondition {

    private String field;
    private RuleOperator operator;
    private Object expected;
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

## API 接口

- `GET /api/rules`：模块说明
- `POST /api/rules/versions`：创建规则版本
- `POST /api/rules/versions/{versionId}/publish`：发布规则版本
- `GET /api/rules/versions`：查询所有版本
- `GET /api/rules/tables/{tableId}/published`：查询规则表当前发布版本
- `POST /api/rules/tables/{tableId}/decisions`：执行决策

## 调用验证

创建规则版本：

```bash
curl -X POST "http://localhost:8130/api/rules/versions" \
  -H "Content-Type: application/json" \
  -d '{
    "tableId": "promotion",
    "version": "v1",
    "description": "promotion rules",
    "rules": [
      {
        "ruleId": "vip-big-order",
        "name": "VIP big order",
        "priority": 100,
        "enabled": true,
        "conditions": [
          {"field": "customerLevel", "operator": "EQ", "expected": "VIP"},
          {"field": "amount", "operator": "GTE", "expected": 1000}
        ],
        "outcome": {"label": "VIP_20", "discountRate": 0.20}
      }
    ],
    "defaultOutcome": {"label": "NONE", "discountRate": 0}
  }'
```

发布版本：

```bash
curl -X POST "http://localhost:8130/api/rules/versions/{versionId}/publish"
```

执行决策：

```bash
curl -X POST "http://localhost:8130/api/rules/tables/promotion/decisions" \
  -H "Content-Type: application/json" \
  -d '{"facts":{"customerLevel":"VIP","amount":1500}}'
```

## 生产映射

本模块使用内存仓储和手写匹配器。生产环境通常替换为：

- 规则存储：MySQL/PostgreSQL 规则表、版本表、发布表
- 规则引擎：Drools、Easy Rules、QLExpress，或数据库决策表 + 自研解释器
- 发布流程：草稿、审批、灰度、发布、回滚
- 缓存：Redis/Caffeine 缓存当前发布版本
- 审计：记录规则变更、发布人、执行 traceId、命中规则
- 安全：限制表达式能力，避免执行任意脚本

## 生产差距

该示例用于隔离学习 规则引擎决策表 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 50-SpringBoot-rule-engine-decision-table test
```

## 要点总结

1. 决策表建模
2. 规则版本发布
3. 单表单活跃版本
4. 优先级匹配
5. 条件执行解释

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
