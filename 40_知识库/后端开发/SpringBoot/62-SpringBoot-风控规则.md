---
title: SpringBoot 风控规则
date: 2026-05-11
tags:
  - springboot
  - java
  - 风控
module: 62-SpringBoot-risk-control
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 风控规则

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/62-SpringBoot-risk-control`

## 核心思路

本模块演示风控决策的核心链路：配置风险规则，维护黑名单，接收业务事件，按规则输出 `ALLOW`、`REVIEW`、`REJECT` 决策，并返回命中规则和解释原因。

## 能力点

- 风控规则配置
- 黑名单检查
- 金额阈值检查
- 频次窗口检查
- 决策严重级别合并
- 风控事件留痕
- 可解释决策结果

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 风控规则 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/RiskControlController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/RiskControlController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/risk")
public class RiskControlController {
    private final RiskControlService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public RiskControlController(RiskControlService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "62-SpringBoot-risk-control");
        data.put("desc", "风控规则、黑名单、频次检查和可解释决策");
        data.put("apis", new String[]{
                "GET /api/risk",
                "POST /api/risk/rules",
                "GET /api/risk/rules",
                "POST /api/risk/blacklist",
                "GET /api/risk/blacklist",
                "POST /api/risk/evaluate",
                "GET /api/risk/events"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/rules")
    public ApiResult<RiskRule> saveRule(@RequestBody RiskRule rule) {
        return ApiResult.success(service.saveRule(rule));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/rules")
    public ApiResult<List<RiskRule>> rules() {
        return ApiResult.success(service.rules());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/blacklist")
    public ApiResult<BlacklistEntry> addBlacklist(@RequestBody BlacklistEntry entry) {
        return ApiResult.success(service.addBlacklist(entry));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/blacklist")
    public ApiResult<List<BlacklistEntry>> blacklist() {
        return ApiResult.success(service.blacklist());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/evaluate")
    public ApiResult<RiskDecision> evaluate(@RequestBody RiskEventRequest request) {
        return ApiResult.success(service.evaluate(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/events")
    public ApiResult<List<RiskEvent>> events() {
        return ApiResult.success(service.events());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/RiskControlService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/RiskControlService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class RiskControlService {
    private final RiskControlRepository repository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public RiskControlService(RiskControlRepository repository) {
        this.repository = repository;
    }

    public RiskRule saveRule(RiskRule rule) {
        validateRule(rule);
        if (rule.getThresholdAmount() != null) {
            rule.setThresholdAmount(money(rule.getThresholdAmount()));
        }
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.saveRule(rule);
    }

    public BlacklistEntry addBlacklist(BlacklistEntry entry) {
        validateBlacklist(entry);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.saveBlacklist(entry);
    }

    public RiskDecision evaluate(RiskEventRequest request) {
        validateEvent(request);
        List<String> hitRules = new ArrayList<>();
        List<String> reasons = new ArrayList<>();
        RiskDecisionType decision = RiskDecisionType.ALLOW;

        for (BlacklistEntry entry : repository.blacklist()) {
            if (entry.getSubjectValue().equals(subjectValue(request, entry.getSubjectType()))) {
                hitRules.add("BLACKLIST:" + entry.getEntryId());
                reasons.add(entry.getSubjectType() + " 命中黑名单: " + entry.getReason());
                decision = moreSevere(decision, RiskDecisionType.REJECT);
            }
        }

        for (RiskRule rule : repository.rules()) {
            if (!rule.isEnabled() || !rule.getScene().equals(request.getScene())) {
                continue;
            }
            if (rule.getRuleType() == RiskRuleType.AMOUNT_LIMIT && amountHit(rule, request)) {
                hitRules.add(rule.getRuleId());
                reasons.add("金额 " + money(request.getAmount()) + " 超过阈值 " + rule.getThresholdAmount());
                decision = moreSevere(decision, rule.getDecision());
            }
            if (rule.getRuleType() == RiskRuleType.VELOCITY_LIMIT && velocityHit(rule, request)) {
                int currentCount = velocityCount(rule, request);
                hitRules.add(rule.getRuleId());
                reasons.add(rule.getWindowMinutes() + " 分钟内 " + rule.getSubjectType()
                        + " 事件数 " + currentCount + " 超过限制 " + rule.getLimitCount());
                decision = moreSevere(decision, rule.getDecision());
            }
        }

        if (hitRules.isEmpty()) {
            reasons.add("未命中风险规则");
        }
        RiskDecision riskDecision = new RiskDecision(request.getEventId(), decision, riskScore(decision), hitRules, reasons);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveEvent(new RiskEvent(request.getEventId(), request.getScene(), request.getUserId(), request.getDeviceId(),
                request.getIp(), money(request.getAmount()), request.getEventTime(), decision));
        return riskDecision;
    }

    public List<RiskRule> rules() {
        return repository.rules().stream().sorted(Comparator.comparing(RiskRule::getRuleId)).toList();
    }

    public List<BlacklistEntry> blacklist() {
        return repository.blacklist().stream().sorted(Comparator.comparing(BlacklistEntry::getEntryId)).toList();
    }

    public List<RiskEvent> events() {
        return repository.events().stream().sorted(Comparator.comparing(RiskEvent::getEventTime)).toList();
    }

    private boolean amountHit(RiskRule rule, RiskEventRequest request) {
        return money(request.getAmount()).compareTo(rule.getThresholdAmount()) > 0;
    }

    private boolean velocityHit(RiskRule rule, RiskEventRequest request) {
        return velocityCount(rule, request) > rule.getLimitCount();
    }

    private int velocityCount(RiskRule rule, RiskEventRequest request) {
        LocalDateTime windowStart = request.getEventTime().minusMinutes(rule.getWindowMinutes());
        String subjectValue = subjectValue(request, rule.getSubjectType());
        long historicalCount = repository.events().stream()
                .filter(event -> event.getScene().equals(request.getScene()))
                .filter(event -> subjectValue.equals(subjectValue(event, rule.getSubjectType())))
                .filter(event -> !event.getEventTime().isBefore(windowStart))
                .filter(event -> !event.getEventTime().isAfter(request.getEventTime()))
                .count();
        // The current event is not persisted until after decisioning, so add it to the window count.
        return Math.toIntExact(historicalCount + 1);
    }

    private RiskDecisionType moreSevere(RiskDecisionType current, RiskDecisionType candidate) {
        // REJECT is terminal severity, REVIEW needs manual handling, ALLOW means no risk hit.
        return severity(candidate) > severity(current) ? candidate : current;
    }

    private int severity(RiskDecisionType decision) {
        return switch (decision) {
            case REJECT -> 2;
            case REVIEW -> 1;
            case ALLOW -> 0;
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/risk/RiskControlRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/risk/RiskControlRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class RiskControlRepository {
    private final Map<String, RiskRule> rules = new LinkedHashMap<>();
    private final Map<String, BlacklistEntry> blacklist = new LinkedHashMap<>();
    private final Map<String, RiskEvent> events = new LinkedHashMap<>();

    public RiskRule saveRule(RiskRule rule) {
        rules.put(rule.getRuleId(), rule);
        return rule;
    }

    public BlacklistEntry saveBlacklist(BlacklistEntry entry) {
        blacklist.put(entry.getEntryId(), entry);
        return entry;
    }

    public RiskEvent saveEvent(RiskEvent event) {
        events.put(event.getEventId(), event);
        return event;
    }

    public Optional<RiskEvent> findEvent(String eventId) {
        return Optional.ofNullable(events.get(eventId));
    }

    public List<RiskRule> rules() {
        return new ArrayList<>(rules.values());
    }

    public List<BlacklistEntry> blacklist() {
        return new ArrayList<>(blacklist.values());
    }

    public List<RiskEvent> events() {
        return new ArrayList<>(events.values());
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

1. RiskControlController：接收 HTTP 请求并转换成 Java 方法调用
2. RiskControlService：执行案例的核心业务规则
3. RiskControlRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/risk`：模块说明
- `POST /api/risk/rules`：创建或替换风控规则
- `GET /api/risk/rules`：查询风控规则
- `POST /api/risk/blacklist`：新增黑名单条目
- `GET /api/risk/blacklist`：查询黑名单
- `POST /api/risk/evaluate`：评估风控事件
- `GET /api/risk/events`：查询已评估事件

## 调用验证

```bash
curl -X POST "http://localhost:8142/api/risk/rules" \
  -H "Content-Type: application/json" \
  -d '{"ruleId":"R-AMOUNT","name":"大额支付复核","ruleType":"AMOUNT_LIMIT","scene":"PAYMENT","subjectType":"USER","thresholdAmount":1000.00,"windowMinutes":0,"limitCount":0,"decision":"REVIEW","enabled":true}'
```

```bash
curl -X POST "http://localhost:8142/api/risk/blacklist" \
  -H "Content-Type: application/json" \
  -d '{"entryId":"BL-1","subjectType":"USER","subjectValue":"user-a","reason":"盗刷用户","operator":"risk-admin","createdAt":"2026-05-08T10:00:00"}'
```

```bash
curl -X POST "http://localhost:8142/api/risk/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"eventId":"E-1","scene":"PAYMENT","userId":"user-a","deviceId":"device-a","ip":"192.168.1.8","amount":1200.00,"eventTime":"2026-05-08T10:01:00"}'
```

## 生产映射

本模块使用内存仓储。生产环境通常替换为：

- 风控规则表：规则类型、场景、主体、阈值、窗口、决策、启用状态
- 黑名单表：主体类型、主体值、原因、操作人、生效/过期时间
- 风控事件表或日志流：保存每次评估请求和决策结果
- Redis 计数器或流式聚合：支持分布式频次窗口
- 人工审核队列：承接 `REVIEW` 决策
- 风控审计日志：解释命中规则，支持追踪和申诉

## 生产差距

该示例用于隔离学习 风控规则 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 62-SpringBoot-risk-control test
```

## 要点总结

1. 风控规则配置
2. 黑名单检查
3. 金额阈值检查
4. 频次窗口检查
5. 决策严重级别合并

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
