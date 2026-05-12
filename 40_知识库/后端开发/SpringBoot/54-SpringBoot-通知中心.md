---
title: SpringBoot 通知中心
date: 2026-05-11
tags:
  - springboot
  - java
  - 通知
module: 54-SpringBoot-notification-center
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 通知中心

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/54-SpringBoot-notification-center`

## 核心思路

本模块演示通知中心原型：通知模板、用户偏好、渠道路由、站内信、模拟邮件/短信投递、失败状态和重试。

## 能力点

- 通知模板
- 占位符渲染
- 用户通知偏好
- 站内信 inbox
- 邮件/SMS 模拟投递
- 投递状态
- 失败重试

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 通知中心 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/NotificationCenterController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/NotificationCenterController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/notifications")
public class NotificationCenterController {
    private final NotificationCenterService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public NotificationCenterController(NotificationCenterService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "54-SpringBoot-notification-center");
        data.put("desc", "通知模板、用户偏好、渠道路由、站内信、模拟投递与重试");
        data.put("apis", new String[]{
                "GET /api/notifications",
                "POST /api/notifications/templates",
                "POST /api/notifications/preferences",
                "POST /api/notifications/send",
                "GET /api/notifications/inbox/{userId}",
                "GET /api/notifications/deliveries",
                "POST /api/notifications/deliveries/{deliveryId}/retry"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/templates")
    public ApiResult<NotificationTemplate> createTemplate(@RequestBody CreateTemplateRequest request) {
        return ApiResult.success(service.createTemplate(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/preferences")
    public ApiResult<UserNotificationPreference> savePreference(@RequestBody SavePreferenceRequest request) {
        return ApiResult.success(service.savePreference(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/send")
    public ApiResult<SendNotificationResult> send(@RequestBody SendNotificationRequest request) {
        return ApiResult.success(service.send(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/inbox/{userId}")
    public ApiResult<List<InboxMessage>> inbox(@PathVariable String userId) {
        return ApiResult.success(service.inbox(userId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/deliveries")
    public ApiResult<List<NotificationDelivery>> deliveries() {
        return ApiResult.success(service.deliveries());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/deliveries/{deliveryId}/retry")
    public ApiResult<NotificationDelivery> retry(@PathVariable String deliveryId) {
        return ApiResult.success(service.retry(deliveryId));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/NotificationCenterService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/NotificationCenterService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class NotificationCenterService {
    private final NotificationRepository repository;
    private final SimulatedChannelSender sender;
    private final Clock clock;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public NotificationCenterService(NotificationRepository repository, SimulatedChannelSender sender) {
        this(repository, sender, Clock.systemUTC());
    }

    public NotificationCenterService(NotificationRepository repository, SimulatedChannelSender sender, Clock clock) {
        this.repository = repository;
        this.sender = sender;
        this.clock = clock;
    }

    public NotificationTemplate createTemplate(CreateTemplateRequest request) {
        if (request == null || isBlank(request.getCode())) throw new IllegalArgumentException("code 不能为空");
        if (isBlank(request.getTitle())) throw new IllegalArgumentException("title 不能为空");
        if (isBlank(request.getContent())) throw new IllegalArgumentException("content 不能为空");
        NotificationTemplate template = new NotificationTemplate(request.getCode(), request.getTitle(), request.getContent(), clock.instant());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveTemplate(template);
        return template;
    }

    public UserNotificationPreference savePreference(SavePreferenceRequest request) {
        if (request == null || isBlank(request.getUserId())) throw new IllegalArgumentException("userId 不能为空");
        List<ChannelType> channels = request.getEnabledChannels() == null ? List.of() : request.getEnabledChannels();
        UserNotificationPreference preference = new UserNotificationPreference(request.getUserId(), request.getEmail(), request.getPhone(), channels);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.savePreference(preference);
        return preference;
    }

    public SendNotificationResult send(SendNotificationRequest request) {
        if (request == null || isBlank(request.getUserId())) throw new IllegalArgumentException("userId 不能为空");
        NotificationTemplate template = repository.findTemplate(request.getTemplateCode())
                .orElseThrow(() -> new NoSuchElementException("通知模板不存在: " + request.getTemplateCode()));
        UserNotificationPreference preference = repository.findPreference(request.getUserId())
                .orElseThrow(() -> new NoSuchElementException("用户通知偏好不存在: " + request.getUserId()));
        String content = render(template.getContent(), request.getVariables() == null ? Map.of() : request.getVariables());
        List<NotificationDelivery> deliveries = preference.getEnabledChannels().stream()
                .map(channel -> deliver(preference, channel, template.getTitle(), content, 1))
                .toList();
        return new SendNotificationResult(content, deliveries);
    }

    public NotificationDelivery retry(String deliveryId) {
        NotificationDelivery delivery = repository.findDelivery(deliveryId)
                .orElseThrow(() -> new NoSuchElementException("投递记录不存在: " + deliveryId));
        if (delivery.getStatus() != DeliveryStatus.FAILED) {
            throw new IllegalArgumentException("只有失败投递可以重试");
        }
        ChannelSendResult result = sender.send(delivery.getChannel(), delivery.getTarget(), delivery.getTitle(), delivery.getContent());
        delivery.setAttemptCount(delivery.getAttemptCount() + 1);
        delivery.setUpdatedAt(clock.instant());
        if (result.isSuccess()) {
            delivery.setStatus(DeliveryStatus.SUCCESS);
            delivery.setLastError(null);
        } else {
            delivery.setLastError(result.getMessage());
        }
        return delivery;
    }

    public List<InboxMessage> inbox(String userId) { return repository.inbox(userId); }
    public List<NotificationDelivery> deliveries() { return repository.deliveries().stream().sorted(Comparator.comparing(NotificationDelivery::getCreatedAt)).toList(); }
    public List<NotificationTemplate> templates() { return repository.templates(); }

    private NotificationDelivery deliver(UserNotificationPreference preference, ChannelType channel, String title, String content, int attempt) {
        String target = target(preference, channel);
        if (channel == ChannelType.IN_APP) {
            // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
            repository.saveInbox(new InboxMessage(UUID.randomUUID().toString(), preference.getUserId(), title, content, false, clock.instant()));
        }
        ChannelSendResult result = channel == ChannelType.IN_APP
                ? new ChannelSendResult(true, "ok")
                : sender.send(channel, target, title, content);
        NotificationDelivery delivery = new NotificationDelivery(UUID.randomUUID().toString(), preference.getUserId(), channel, target, title, content,
                result.isSuccess() ? DeliveryStatus.SUCCESS : DeliveryStatus.FAILED, attempt,
                result.isSuccess() ? null : result.getMessage(), clock.instant(), clock.instant());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveDelivery(delivery);
        return delivery;
    }

    private String target(UserNotificationPreference preference, ChannelType channel) {
        return switch (channel) {
            case IN_APP -> preference.getUserId();
            case EMAIL -> preference.getEmail();
            case SMS -> preference.getPhone();
        };
    }

    private String render(String template, Map<String, Object> variables) {
        String rendered = template;
        for (Map.Entry<String, Object> entry : variables.entrySet()) {
            rendered = rendered.replace("{" + entry.getKey() + "}", String.valueOf(entry.getValue()));
        }
        return rendered;
    }

    private boolean isBlank(String value) { return value == null || value.isBlank(); }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/notification/NotificationRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/notification/NotificationRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class NotificationRepository {
    private final Map<String, NotificationTemplate> templates = new LinkedHashMap<>();
    private final Map<String, UserNotificationPreference> preferences = new LinkedHashMap<>();
    private final Map<String, InboxMessage> inbox = new LinkedHashMap<>();
    private final Map<String, NotificationDelivery> deliveries = new LinkedHashMap<>();

    public void saveTemplate(NotificationTemplate template) { templates.put(template.getCode(), template); }
    public Optional<NotificationTemplate> findTemplate(String code) { return Optional.ofNullable(templates.get(code)); }
    public List<NotificationTemplate> templates() { return new ArrayList<>(templates.values()); }
    public void savePreference(UserNotificationPreference preference) { preferences.put(preference.getUserId(), preference); }
    public Optional<UserNotificationPreference> findPreference(String userId) { return Optional.ofNullable(preferences.get(userId)); }
    public void saveInbox(InboxMessage message) { inbox.put(message.getMessageId(), message); }
    public List<InboxMessage> inbox(String userId) { return inbox.values().stream().filter(m -> m.getUserId().equals(userId)).toList(); }
    public void saveDelivery(NotificationDelivery delivery) { deliveries.put(delivery.getDeliveryId(), delivery); }
    public Optional<NotificationDelivery> findDelivery(String deliveryId) { return Optional.ofNullable(deliveries.get(deliveryId)); }
    public List<NotificationDelivery> deliveries() { return new ArrayList<>(deliveries.values()); }
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

1. NotificationCenterController：接收 HTTP 请求并转换成 Java 方法调用
2. NotificationCenterService：执行案例的核心业务规则
3. NotificationRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/notifications`：模块说明
- `POST /api/notifications/templates`：创建模板
- `POST /api/notifications/preferences`：保存用户偏好
- `POST /api/notifications/send`：发送通知
- `GET /api/notifications/inbox/{userId}`：查询站内信
- `GET /api/notifications/deliveries`：查询投递记录
- `POST /api/notifications/deliveries/{deliveryId}/retry`：重试失败投递

## 调用验证

```bash
curl -X POST "http://localhost:8134/api/notifications/templates" \
  -H "Content-Type: application/json" \
  -d '{"code":"ORDER_PAID","title":"订单支付成功","content":"Hi {name}, order {orderId} paid"}'
```

```bash
curl -X POST "http://localhost:8134/api/notifications/preferences" \
  -H "Content-Type: application/json" \
  -d '{"userId":"U100","email":"alice@example.com","phone":"13800000000","enabledChannels":["IN_APP","EMAIL"]}'
```

```bash
curl -X POST "http://localhost:8134/api/notifications/send" \
  -H "Content-Type: application/json" \
  -d '{"userId":"U100","templateCode":"ORDER_PAID","variables":{"name":"Alice","orderId":"O1001"}}'
```

## 生产映射

本模块使用内存仓储和模拟发送器。生产环境通常替换为：

- 模板：数据库模板表、版本管理、Freemarker/Thymeleaf
- 偏好：用户通知设置表
- 发送：MQ + worker
- 邮件：SMTP/SendGrid/SES
- 短信：云短信供应商
- 站内信：inbox 表 + unread counter
- 重试：指数退避、最大次数、死信队列

## 生产差距

该示例用于隔离学习 通知中心 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 54-SpringBoot-notification-center test
```

## 要点总结

1. 通知模板
2. 占位符渲染
3. 用户通知偏好
4. 站内信 inbox
5. 邮件/SMS 模拟投递

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
