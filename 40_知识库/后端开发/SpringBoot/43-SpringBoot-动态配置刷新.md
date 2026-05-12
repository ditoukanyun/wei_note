---
title: SpringBoot 动态配置刷新
date: 2026-05-11
tags:
  - springboot
  - java
  - 配置
module: 43-SpringBoot-dynamic-config-refresh
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 动态配置刷新

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/43-SpringBoot-dynamic-config-refresh`

## 核心思路

本模块演示一个内存版动态配置中心：通过 API 修改配置，服务发布变更事件，运行时设置监听事件后刷新快照，不需要重启应用。

## 能力点

- 配置项版本管理
- 配置值校验
- Spring 应用事件发布与监听
- 运行时配置快照刷新
- 动态开关、限流阈值、签名时间窗配置示例

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 动态配置刷新 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/DynamicConfigController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/DynamicConfigController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/config")
public class DynamicConfigController {

    private final DynamicConfigService configService;
    private final RuntimeSettingsService runtimeSettingsService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DynamicConfigController(DynamicConfigService configService, RuntimeSettingsService runtimeSettingsService) {
        this.configService = configService;
        this.runtimeSettingsService = runtimeSettingsService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "43-SpringBoot-dynamic-config-refresh");
        data.put("desc", "内存动态配置中心、变更事件和运行时刷新");
        data.put("keys", configService.keys());
        data.put("apis", new String[]{
                "GET /api/config/items",
                "GET /api/config/items/{key}",
                "PUT /api/config/items/{key}",
                "GET /api/config/runtime"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/items")
    public ApiResult<List<ConfigItem>> items() {
        return ApiResult.success(configService.findAll());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/items/{key}")
    public ApiResult<ConfigItem> item(@PathVariable String key) {
        return ApiResult.success(configService.findByKey(key));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PutMapping("/items/{key}")
    public ApiResult<ConfigItem> update(@PathVariable String key, @RequestBody UpdateConfigRequest request) {
        return ApiResult.success(configService.update(key, request.getValue()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/runtime")
    public ApiResult<RuntimeSettings> runtime() {
        return ApiResult.success(runtimeSettingsService.snapshot());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/DynamicConfigService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/DynamicConfigService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class DynamicConfigService {

    private final DynamicConfigRepository repository;
    private final ApplicationEventPublisher publisher;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DynamicConfigService(DynamicConfigRepository repository, ApplicationEventPublisher publisher) {
        this.repository = repository;
        this.publisher = publisher;
    }

    public List<ConfigItem> findAll() {
        return repository.findAll();
    }

    public ConfigItem findByKey(String key) {
        return repository.findByKey(key)
                .orElseThrow(() -> new IllegalArgumentException("配置不存在: " + key));
    }

    public ConfigItem update(String key, String value) {
        ConfigItem current = findByKey(key);
        validate(key, value);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        ConfigItem updated = repository.save(current.nextVersion(value, LocalDateTime.now()));
        publisher.publishEvent(new ConfigChangedEvent(updated));
        return updated;
    }

    public List<String> keys() {
        return repository.keys();
    }

    private void validate(String key, String value) {
        if (!StringUtils.hasText(value)) {
            throw new IllegalArgumentException(key + " 不能为空");
        }
        if ("feature.new-checkout.enabled".equals(key)) {
            if (!"true".equalsIgnoreCase(value) && !"false".equalsIgnoreCase(value)) {
                throw new IllegalArgumentException(key + " 必须是 true 或 false");
            }
            return;
        }
        if ("rate-limit.login.limit".equals(key)) {
            int limit = parseInt(key, value);
            if (limit < 1 || limit > 1000) {
                throw new IllegalArgumentException(key + " 必须是 1 到 1000 的整数");
            }
            return;
        }
        if ("signature.allowed-skew-seconds".equals(key)) {
            int seconds = parseInt(key, value);
            if (seconds < 30 || seconds > 3600) {
                throw new IllegalArgumentException(key + " 必须是 30 到 3600 的整数");
            }
        }
    }

    private int parseInt(String key, String value) {
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException ex) {
            throw new IllegalArgumentException(key + " 必须是整数");
        }
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/configcenter/DynamicConfigRepository.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/configcenter/DynamicConfigRepository.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class DynamicConfigRepository {

    private final Map<String, ConfigItem> items = new ConcurrentHashMap<>();

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DynamicConfigRepository() {
        LocalDateTime now = LocalDateTime.of(2026, 4, 30, 10, 0);
        save(new ConfigItem("feature.new-checkout.enabled", "false", 1, "新结账流程开关", now));
        save(new ConfigItem("rate-limit.login.limit", "5", 1, "登录接口限流阈值", now));
        save(new ConfigItem("signature.allowed-skew-seconds", "300", 1, "请求签名允许时间偏移秒数", now));
    }

    public List<ConfigItem> findAll() {
        return items.values().stream()
                .sorted(Comparator.comparing(ConfigItem::getKey))
                .toList();
    }

    public Optional<ConfigItem> findByKey(String key) {
        return Optional.ofNullable(items.get(key));
    }

    public ConfigItem save(ConfigItem item) {
        items.put(item.getKey(), item);
        return item;
    }

    public List<String> keys() {
        return new ArrayList<>(findAll().stream().map(ConfigItem::getKey).toList());
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 示例里的 Repository 多半是内存实现；真实项目要替换成数据库、缓存或外部服务。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/RuntimeSettingsService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/RuntimeSettingsService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class RuntimeSettingsService {

    private final DynamicConfigRepository repository;
    private volatile RuntimeSettings settings;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public RuntimeSettingsService(DynamicConfigRepository repository) {
        this.repository = repository;
        refresh();
    }

    public RuntimeSettings snapshot() {
        return settings;
    }

    @EventListener
    public void handleConfigChanged(ConfigChangedEvent event) {
        refresh();
    }

    private void refresh() {
        settings = new RuntimeSettings(
                Boolean.parseBoolean(value("feature.new-checkout.enabled")),
                Integer.parseInt(value("rate-limit.login.limit")),
                Integer.parseInt(value("signature.allowed-skew-seconds"))
        );
    }

    private String value(String key) {
        return repository.findByKey(key)
                .orElseThrow(() -> new IllegalStateException("配置不存在: " + key))
                .getValue();
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. DynamicConfigController：启动时注册配置、Bean 或扩展点
2. DynamicConfigController：接收 HTTP 请求并转换成 Java 方法调用
3. DynamicConfigService：执行案例的核心业务规则
4. DynamicConfigRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/config`：模块说明和配置 key
- `GET /api/config/items`：查询全部配置项
- `GET /api/config/items/{key}`：查询单个配置项
- `PUT /api/config/items/{key}`：更新配置项
- `GET /api/config/runtime`：查询运行时快照

## 调用验证

```bash
curl "http://localhost:8123/api/config/runtime"
```

更新签名时间窗：

```bash
curl -X PUT "http://localhost:8123/api/config/items/signature.allowed-skew-seconds" \
  -H "Content-Type: application/json" \
  -d '{"value":"120"}'
```

再次查询 `/api/config/runtime`，可以看到 `signatureAllowedSkewSeconds` 已刷新为 `120`。

## 生产差距

该示例用于隔离学习 动态配置刷新 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 43-SpringBoot-dynamic-config-refresh test
```

## 要点总结

1. 配置项版本管理
2. 配置值校验
3. Spring 应用事件发布与监听
4. 运行时配置快照刷新
5. 动态开关、限流阈值、签名时间窗配置示例

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
