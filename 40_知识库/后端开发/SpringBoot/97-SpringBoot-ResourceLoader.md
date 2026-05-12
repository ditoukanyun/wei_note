---
title: SpringBoot ResourceLoader
date: 2026-05-11
tags:
  - springboot
  - java
  - 资源加载
module: 97-SpringBoot-resource-loader
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ResourceLoader

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/97-SpringBoot-resource-loader`

## 核心思路

本模块演示 Spring 的资源抽象：用 `ResourceLoader` 读取单个 `classpath:` 资源，用 `PathMatchingResourcePatternResolver` 扫描 `classpath*:` pattern，并把资源转换成稳定的描述信息。

## 能力点

- `ResourceLoader`
- `Resource`
- `ClassPathResource` 风格位置
- `PathMatchingResourcePatternResolver`
- `classpath:` 单资源加载
- `classpath*:` classpath 聚合扫描
- 资源存在性和可读性判断
- ApplicationContextRunner 验证资源服务
- MockMvc 验证完整应用上下文中的资源接口

## 结构与链路

1. `ResourceCatalogService` 注入 `ResourceLoader`。
2. `loadSingle(...)` 使用 `resourceLoader.getResource("classpath:...")`。
3. `scanTextResources()` 使用 `PathMatchingResourcePatternResolver`。
4. pattern `classpath*:demo-resources/**/*.txt` 扫描模块内文本资源。
5. 每个 `Resource` 转换为 `ResourceDescriptor`。
6. controller 暴露 metadata、single 和 scan 接口。

## 关键实现

单资源：

```java
Resource resource = resourceLoader.getResource("classpath:demo-resources/orders/order-template.txt");
```

pattern 扫描：

```java
Resource[] resources = patternResolver.getResources("classpath*:demo-resources/**/*.txt");
```

`classpath:` 通常定位一个资源；`classpath*:` 用于聚合 classpath 上所有匹配资源，常见于框架扫描配置、metadata 或多个 jar 中的同名资源。

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ResourceLoader 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ResourceLoaderController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ResourceLoaderController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/resource-loader")
public class ResourceLoaderController {
    private final ResourceCatalogService resourceCatalogService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ResourceLoaderController(ResourceCatalogService resourceCatalogService) {
        this.resourceCatalogService = resourceCatalogService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "97-SpringBoot-resource-loader",
                "topic", "Spring ResourceLoader and classpath resource pattern scanning",
                "apis", List.of(
                        "GET /api/resource-loader",
                        "GET /api/resource-loader/single?location=classpath:demo-resources/orders/order-template.txt",
                        "GET /api/resource-loader/scan"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/single")
    public ApiResult<ResourceDescriptor> single(@RequestParam(defaultValue = "classpath:demo-resources/orders/order-template.txt")
                                                String location) {
        return ApiResult.success(resourceCatalogService.loadSingle(location));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/scan")
    public ApiResult<List<ResourceDescriptor>> scan() {
        return ApiResult.success(resourceCatalogService.scanTextResources());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/resource/ResourceCatalogService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/resource/ResourceCatalogService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
public class ResourceCatalogService {
    private static final String TEXT_RESOURCE_PATTERN = "classpath*:demo-resources/**/*.txt";

    private final ResourceLoader resourceLoader;
    private final PathMatchingResourcePatternResolver patternResolver;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ResourceCatalogService(ResourceLoader resourceLoader) {
        this.resourceLoader = resourceLoader;
        this.patternResolver = new PathMatchingResourcePatternResolver(resourceLoader);
    }

    public ResourceDescriptor loadSingle(String location) {
        // classpath: resolves one resource from the application's classpath.
        // ResourceLoader 根据 location 字符串找到资源，调用方不必关心底层来自文件还是 classpath。
        return describe(location, resourceLoader.getResource(location));
    }

    public List<ResourceDescriptor> scanTextResources() {
        try {
            // classpath*: allows Spring to aggregate matching resources across classpath roots and jars.
            // classpath* 扫描可能返回多个资源，常用于框架发现约定位置的配置。
            return Arrays.stream(patternResolver.getResources(TEXT_RESOURCE_PATTERN))
                    .map(resource -> describe(resource.getDescription(), resource))
                    .sorted(Comparator.comparing(ResourceDescriptor::filename))
                    .toList();
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to scan resources with pattern " + TEXT_RESOURCE_PATTERN, ex);
        }
    }

    private ResourceDescriptor describe(String location, Resource resource) {
        boolean exists = resource.exists();
        boolean readable = exists && resource.isReadable();
        return new ResourceDescriptor(
                location,
                resource.getFilename() == null ? "unknown" : resource.getFilename(),
                exists,
                readable,
                readable ? preview(resource) : "missing"
        );
    }

    private String preview(Resource resource) {
        try {
            String content = new String(resource.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
            return content.replace(System.lineSeparator(), " | ").trim();
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to read resource " + resource.getDescription(), ex);
        }
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/resource/ResourceLoaderConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/resource/ResourceLoaderConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration(proxyBeanMethods = false)
public class ResourceLoaderConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public ResourceCatalogService resourceCatalogService(ResourceLoader resourceLoader) {
        return new ResourceCatalogService(resourceLoader);
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
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
    @ExceptionHandler(Exception.class)
    public ApiResult<Void> handleException(Exception ex) {
        return ApiResult.fail(500, ex.getMessage());
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. ResourceLoaderConfig：启动时注册配置、Bean 或扩展点
2. ResourceLoaderController：接收 HTTP 请求并转换成 Java 方法调用
3. ResourceCatalogService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/resource-loader`：模块说明
- `GET /api/resource-loader/single?location=classpath:demo-resources/orders/order-template.txt`：加载单个资源
- `GET /api/resource-loader/scan`：扫描 demo 文本资源

## 调用验证

```bash
curl "http://localhost:8177/api/resource-loader"
```

```bash
curl "http://localhost:8177/api/resource-loader/single?location=classpath:demo-resources/orders/order-template.txt"
```

```bash
curl "http://localhost:8177/api/resource-loader/scan"
```

`/scan` 核心响应：

```json
[
  {
    "filename": "inventory-template.txt",
    "exists": true,
    "readable": true
  },
  {
    "filename": "order-template.txt",
    "exists": true,
    "readable": true
  }
]
```

## 生产映射

Spring `Resource` 抽象适合屏蔽文件系统、classpath、jar 包等资源来源差异。典型场景：

- 加载 SQL、模板、规则文件等 classpath 内容；
- 扫描多个 jar 里的配置或 metadata；
- 编写 starter 时查找约定路径资源；
- 阅读 Spring 源码中资源加载、组件扫描、XML/metadata 解析相关逻辑。

如果资源来自用户上传或外部存储，不应直接套用 classpath 扫描；那类场景需要独立的存储、权限和生命周期设计。

## 生产差距

该示例用于隔离学习 ResourceLoader 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 97-SpringBoot-resource-loader test
```

测试覆盖：

- 加载 `order-template.txt`
- 缺失 classpath 资源返回 `exists=false`
- 扫描返回 `inventory-template.txt` 和 `order-template.txt`
- MockMvc 验证 metadata 和 scan 接口

## 要点总结

1. `ResourceLoader`
2. `Resource`
3. `ClassPathResource` 风格位置
4. `PathMatchingResourcePatternResolver`
5. `classpath:` 单资源加载

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
