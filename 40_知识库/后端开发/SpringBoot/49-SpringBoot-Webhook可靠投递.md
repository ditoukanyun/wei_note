---
title: SpringBoot Webhook可靠投递
date: 2026-05-11
tags:
  - springboot
  - java
  - webhook
module: 49-SpringBoot-webhook-delivery
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot Webhook可靠投递

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/49-SpringBoot-webhook-delivery`

## 核心思路

本模块演示出站 Webhook 投递：订阅事件类型，发布事件后按订阅生成投递记录，使用 HMAC SHA-256 签名，失败后进入重试等待，超过最大次数后进入死信，并支持死信重放。

## 能力点

- Webhook 订阅
- HMAC 签名
- 投递历史
- 重试退避
- 死信记录
- 死信重放

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot Webhook可靠投递 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/WebhookDeliveryController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/WebhookDeliveryController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/webhooks")
public class WebhookDeliveryController {

    private final WebhookDeliveryService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public WebhookDeliveryController(WebhookDeliveryService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "49-SpringBoot-webhook-delivery");
        data.put("desc", "Webhook 订阅、HMAC 签名投递、重试退避、死信和重放");
        data.put("apis", new String[]{
                "GET /api/webhooks",
                "POST /api/webhooks/subscriptions",
                "GET /api/webhooks/subscriptions",
                "POST /api/webhooks/events",
                "POST /api/webhooks/retries/due",
                "POST /api/webhooks/deliveries/{deliveryId}/replay",
                "GET /api/webhooks/deliveries"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/subscriptions")
    public ApiResult<WebhookSubscription> createSubscription(@RequestBody CreateWebhookSubscriptionRequest request) {
        return ApiResult.success(service.createSubscription(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/subscriptions")
    public ApiResult<List<WebhookSubscription>> subscriptions() {
        return ApiResult.success(service.subscriptions());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/events")
    public ApiResult<List<WebhookDeliveryRecord>> publish(@RequestBody PublishWebhookEventRequest request) {
        return ApiResult.success(service.publishEvent(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/retries/due")
    public ApiResult<List<WebhookDeliveryRecord>> processDueRetries() {
        return ApiResult.success(service.processDueRetries());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/deliveries/{deliveryId}/replay")
    public ApiResult<WebhookDeliveryRecord> replay(@PathVariable String deliveryId) {
        return ApiResult.success(service.replay(deliveryId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/deliveries")
    public ApiResult<List<WebhookDeliveryRecord>> deliveries() {
        return ApiResult.success(service.deliveryHistory());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/WebhookDeliveryService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/WebhookDeliveryService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class WebhookDeliveryService {

    private final WebhookDeliveryRepository repository;
    private final WebhookClient webhookClient;
    private final Clock clock;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public WebhookDeliveryService(WebhookDeliveryRepository repository, WebhookClient webhookClient) {
        this(repository, webhookClient, Clock.systemUTC());
    }

    public WebhookDeliveryService(WebhookDeliveryRepository repository, WebhookClient webhookClient, Clock clock) {
        this.repository = repository;
        this.webhookClient = webhookClient;
        this.clock = clock;
    }

    public WebhookSubscription createSubscription(CreateWebhookSubscriptionRequest request) {
        validateSubscription(request);
        WebhookSubscription subscription = new WebhookSubscription(
                UUID.randomUUID().toString(),
                request.getEventType(),
                request.getTargetUrl(),
                request.getSecret(),
                request.getMaxAttempts() <= 0 ? 3 : request.getMaxAttempts(),
                true,
                clock.instant()
        );
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveSubscription(subscription);
        return subscription;
    }

    public List<WebhookSubscription> subscriptions() {
        return repository.subscriptions().stream()
                .sorted(Comparator.comparing(WebhookSubscription::getCreatedAt))
                .toList();
    }

    public List<WebhookDeliveryRecord> publishEvent(PublishWebhookEventRequest request) {
        validateEvent(request);
        return repository.subscriptions().stream()
                .filter(WebhookSubscription::isActive)
                .filter(subscription -> subscription.getEventType().equals(request.getEventType()))
                .map(subscription -> createAndAttempt(subscription, request.getEventType(), request.getPayload()))
                .toList();
    }

    public List<WebhookDeliveryRecord> processDueRetries() {
        Instant now = clock.instant();
        return repository.deliveries().stream()
                .filter(record -> record.getStatus() == WebhookDeliveryStatus.RETRY_WAIT)
                .filter(record -> !record.getNextRetryAt().isAfter(now))
                .map(this::attemptExisting)
                .toList();
    }

    public WebhookDeliveryRecord replay(String deliveryId) {
        WebhookDeliveryRecord record = findDelivery(deliveryId);
        if (record.getStatus() != WebhookDeliveryStatus.DEAD_LETTER) {
            throw new IllegalArgumentException("只有死信投递可以重放");
        }
        WebhookSubscription subscription = repository.findSubscription(record.getSubscriptionId())
                .orElseThrow(() -> new NoSuchElementException("订阅不存在: " + record.getSubscriptionId()));
        return createAndAttempt(subscription, record.getEventType(), record.getPayload());
    }

    public List<WebhookDeliveryRecord> deliveryHistory() {
        return repository.deliveries().stream()
                .sorted(Comparator.comparing(WebhookDeliveryRecord::getCreatedAt))
                .toList();
    }

    public String sign(String eventType, String payload, String secret) {
        try {
            String data = eventType + "." + payload;
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            return HexFormat.of().formatHex(mac.doFinal(data.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception exception) {
            throw new IllegalStateException("生成 webhook 签名失败", exception);
        }
    }

    private WebhookDeliveryRecord createAndAttempt(WebhookSubscription subscription, String eventType, String payload) {
        WebhookDeliveryRecord record = new WebhookDeliveryRecord(
                UUID.randomUUID().toString(),
                subscription.getSubscriptionId(),
                eventType,
                subscription.getTargetUrl(),
                payload,
                sign(eventType, payload, subscription.getSecret()),
                clock.instant()
        );
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveDelivery(record);
        return attempt(record, subscription);
    }

    private WebhookDeliveryRecord attemptExisting(WebhookDeliveryRecord record) {
        WebhookSubscription subscription = repository.findSubscription(record.getSubscriptionId())
                .orElseThrow(() -> new NoSuchElementException("订阅不存在: " + record.getSubscriptionId()));
        return attempt(record, subscription);
    }

    private WebhookDeliveryRecord attempt(WebhookDeliveryRecord record, WebhookSubscription subscription) {
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：SimulatedWebhookClient

源码位置：`src/main/java/com/cloud/webhook/SimulatedWebhookClient.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/webhook/SimulatedWebhookClient.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Component
public class SimulatedWebhookClient implements WebhookClient {

    private final ConcurrentMap<String, Integer> remainingFailures = new ConcurrentHashMap<>();

    public void fail(String targetUrl, int times) {
        remainingFailures.put(targetUrl, times);
    }

    public void succeed(String targetUrl) {
        remainingFailures.remove(targetUrl);
    }

    @Override
    public WebhookClientResult send(WebhookClientRequest request) {
        if (request.getTargetUrl().startsWith("simulate://always-fail")) {
            return WebhookClientResult.failure("simulated failure");
        }
        Integer remaining = remainingFailures.getOrDefault(request.getTargetUrl(), 0);
        if (remaining > 0) {
            remainingFailures.put(request.getTargetUrl(), remaining - 1);
            return WebhookClientResult.failure("simulated failure");
        }
        return WebhookClientResult.success();
    }

    public Map<String, Integer> remainingFailures() {
        return Map.copyOf(remainingFailures);
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：WebhookClient

源码位置：`src/main/java/com/cloud/webhook/WebhookClient.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/webhook/WebhookClient.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public interface WebhookClient {

    WebhookClientResult send(WebhookClientRequest request);
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
- 忽略幂等、重试、超时和补偿，导致失败后状态不一致。

## API 接口

- `GET /api/webhooks`：模块说明
- `POST /api/webhooks/subscriptions`：创建订阅
- `GET /api/webhooks/subscriptions`：查询订阅
- `POST /api/webhooks/events`：发布事件并触发投递
- `POST /api/webhooks/retries/due`：处理到期重试
- `POST /api/webhooks/deliveries/{deliveryId}/replay`：重放死信
- `GET /api/webhooks/deliveries`：查询投递历史

## 调用验证

```bash
curl -X POST "http://localhost:8129/api/webhooks/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{"eventType":"order.created","targetUrl":"https://example.com/webhook","secret":"secret","maxAttempts":3}'
```

```bash
curl -X POST "http://localhost:8129/api/webhooks/events" \
  -H "Content-Type: application/json" \
  -d '{"eventType":"order.created","payload":"{\"orderId\":\"O1001\"}"}'
```

## 生产映射

本模块使用内存仓储和模拟客户端。生产环境通常替换为：

- 订阅表：MySQL/PostgreSQL
- 投递表：持久化 delivery records
- 投递执行：MQ + worker 或定时扫描 due retry
- HTTP 客户端：WebClient/OkHttp/Apache HttpClient
- 签名头：如 `X-Webhook-Signature`
- 重试策略：指数退避 + 最大窗口 + 死信队列

## 生产差距

该示例用于隔离学习 Webhook可靠投递 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 49-SpringBoot-webhook-delivery test
```

## 要点总结

1. Webhook 订阅
2. HMAC 签名
3. 投递历史
4. 重试退避
5. 死信记录

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
