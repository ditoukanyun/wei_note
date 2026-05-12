---
title: SpringBoot WebMVC扩展点
date: 2026-05-11
tags:
  - springboot
  - java
  - 积分
module: 69-SpringBoot-webmvc-extension-points
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot WebMVC扩展点

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/69-SpringBoot-webmvc-extension-points`

## 核心思路

本模块演示 Spring MVC 常见扩展点：`HandlerInterceptor`、`HandlerMethodArgumentResolver`、`ResponseBodyAdvice` 和统一请求上下文增强。

## 能力点

- `HandlerInterceptor`
- `HandlerMethodArgumentResolver`
- `ResponseBodyAdvice`
- `WebMvcConfigurer`
- 请求上下文归一化
- controller 参数注入
- trace id 响应增强

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot WebMVC扩展点 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/WebMvcExtensionController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/WebMvcExtensionController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/webmvc")
public class WebMvcExtensionController {
    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/extensions")
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "69-SpringBoot-webmvc-extension-points");
        data.put("desc", "HandlerInterceptor、参数解析器、ResponseBodyAdvice 与请求上下文增强");
        data.put("apis", new String[]{
                "GET /api/webmvc/extensions",
                "GET /api/webmvc/context",
                "GET /api/webmvc/orders/{orderId}"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/context")
    public ApiResult<RequestMetadata> context(RequestMetadata metadata) {
        return ApiResult.success(metadata);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/orders/{orderId}")
    public ApiResult<Map<String, Object>> order(@PathVariable String orderId, RequestMetadata metadata) {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("orderId", orderId);
        data.put("tenantId", metadata.getTenantId());
        data.put("handledBy", "anonymous".equals(metadata.getOperatorId()) ? "u-100-default" : metadata.getOperatorId());
        data.put("channel", metadata.getChannel());
        return ApiResult.success(data);
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 请求拦截：进入 Controller 前做什么

源码位置：`src/main/java/com/cloud/webmvc/RequestContextInterceptor.java`

拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。

```java
// 文件：com/cloud/webmvc/RequestContextInterceptor.java
// 学习重点：拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。
@Component
public class RequestContextInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        // HandlerInterceptor runs before the controller, making it a good place to normalize request context.
        RequestMetadata metadata = new RequestMetadata(
                headerOrDefault(request, "X-Trace-Id", "trace-" + UUID.randomUUID()),
                headerOrDefault(request, "X-Tenant-Id", "public"),
                headerOrDefault(request, "X-Operator-Id", "anonymous"),
                headerOrDefault(request, "X-Channel", "web")
        );
        request.setAttribute(RequestMetadata.ATTRIBUTE_NAME, metadata);
        response.setHeader("X-Trace-Id", metadata.getTraceId());
        return true;
    }

    private String headerOrDefault(HttpServletRequest request, String name, String defaultValue) {
        String value = request.getHeader(name);
        return value == null || value.isBlank() ? defaultValue : value;
    }
}
```

关键点拆解：

- 前置处理负责准备上下文，后置处理负责清理资源；这两个动作要成对出现。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/config/WebMvcExtensionConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/config/WebMvcExtensionConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
public class WebMvcExtensionConfig implements WebMvcConfigurer {
    private final RequestContextInterceptor interceptor;
    private final RequestMetadataArgumentResolver argumentResolver;

    public WebMvcExtensionConfig(RequestContextInterceptor interceptor,
                                 RequestMetadataArgumentResolver argumentResolver) {
        this.interceptor = interceptor;
        this.argumentResolver = argumentResolver;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(interceptor).addPathPatterns("/api/**");
    }

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        resolvers.add(argumentResolver);
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：RequestMetadataArgumentResolver

源码位置：`src/main/java/com/cloud/webmvc/RequestMetadataArgumentResolver.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/webmvc/RequestMetadataArgumentResolver.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Component
public class RequestMetadataArgumentResolver implements HandlerMethodArgumentResolver {
    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return RequestMetadata.class.isAssignableFrom(parameter.getParameterType());
    }

    @Override
    public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer mavContainer,
                                  NativeWebRequest webRequest, WebDataBinderFactory binderFactory) {
        // Argument resolvers run when Spring MVC prepares controller method parameters.
        Object metadata = webRequest.getAttribute(RequestMetadata.ATTRIBUTE_NAME, NativeWebRequest.SCOPE_REQUEST);
        if (metadata instanceof RequestMetadata requestMetadata) {
            return requestMetadata;
        }
        return new RequestMetadata("trace-missing", "public", "anonymous", "web");
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. WebMvcExtensionConfig：启动时注册配置、Bean 或扩展点
2. RequestContextInterceptor：请求进入 Controller 前准备上下文或校验
3. WebMvcExtensionController：接收 HTTP 请求并转换成 Java 方法调用

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/webmvc/extensions`：模块说明
- `GET /api/webmvc/context`：返回当前请求上下文
- `GET /api/webmvc/orders/{orderId}`：返回订单示例响应，并展示响应增强

## 调用验证

```bash
curl "http://localhost:8149/api/webmvc/context" \
  -H "X-Trace-Id: trace-123" \
  -H "X-Tenant-Id: tenant-a" \
  -H "X-Operator-Id: u-100" \
  -H "X-Channel: mobile"
```

```bash
curl "http://localhost:8149/api/webmvc/orders/O-100" \
  -H "X-Trace-Id: trace-order"
```

响应体中的 `traceId` 由 `TraceResponseBodyAdvice` 统一补齐，响应头中的 `X-Trace-Id` 由拦截器补齐。

## 生产映射

生产系统可以用同样模式实现：

- trace id、租户、操作人统一提取
- controller 参数级上下文注入
- 多租户和审计上下文传播
- 响应体或响应头统一增强
- 避免每个 controller 重复解析请求头

## 生产差距

该示例用于隔离学习 WebMVC扩展点 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 69-SpringBoot-webmvc-extension-points test
```

测试覆盖：

- 拦截器读取 header 和默认值
- 参数解析器支持并解析 `RequestMetadata`
- MockMvc 验证 header 到 controller 参数的完整链路
- `ResponseBodyAdvice` 给响应体补充 trace id

## 要点总结

1. `HandlerInterceptor`
2. `HandlerMethodArgumentResolver`
3. `ResponseBodyAdvice`
4. `WebMvcConfigurer`
5. 请求上下文归一化

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
