---
title: SpringBoot BeanFactoryPostProcessor
date: 2026-05-11
tags:
  - springboot
  - java
  - spring扩展点
module: 74-SpringBoot-bean-factory-post-processor
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot BeanFactoryPostProcessor

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/74-SpringBoot-bean-factory-post-processor`

## 核心思路

本模块演示 Spring 容器 refresh 过程中的 `BeanFactoryPostProcessor`：在 Bean 实例化之前修改 `BeanDefinition`，让最终创建出来的 Bean 使用新的属性值。

## 能力点

- `BeanFactoryPostProcessor`
- `ConfigurableListableBeanFactory`
- `BeanDefinition`
- Bean 实例化前属性改写
- `static @Bean` 注册早期扩展点
- MockMvc 验证最终 Bean 行为

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot BeanFactoryPostProcessor 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/BeanFactoryPostProcessorController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/BeanFactoryPostProcessorController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/bean-factory-post-processor")
public class BeanFactoryPostProcessorController {
    private final GreetingTemplate greetingTemplate;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public BeanFactoryPostProcessorController(GreetingTemplate greetingTemplate) {
        this.greetingTemplate = greetingTemplate;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "74-SpringBoot-bean-factory-post-processor",
                "apis", List.of(
                        "GET /api/bean-factory-post-processor",
                        "GET /api/bean-factory-post-processor/greeting"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/greeting")
    public ApiResult<Map<String, Object>> greeting(@RequestParam(defaultValue = "Spring") String name) {
        return ApiResult.success(Map.of(
                "greeting", greetingTemplate.greet(name),
                "messagePrefix", greetingTemplate.getMessagePrefix(),
                "processorTag", greetingTemplate.getProcessorTag()
        ));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 后置处理器：容器创建过程中如何扩展

源码位置：`src/main/java/com/cloud/beanfactory/GreetingTemplateBeanFactoryPostProcessor.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/beanfactory/GreetingTemplateBeanFactoryPostProcessor.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class GreetingTemplateBeanFactoryPostProcessor implements BeanFactoryPostProcessor {
    public static final String TARGET_BEAN_NAME = "greetingTemplate";

    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
        if (!beanFactory.containsBeanDefinition(TARGET_BEAN_NAME)) {
            return;
        }
        BeanDefinition beanDefinition = beanFactory.getBeanDefinition(TARGET_BEAN_NAME);
        beanDefinition.getPropertyValues().add("messagePrefix", "post-processed");
        beanDefinition.getPropertyValues().add("processorTag", "bean-factory-post-processor");
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/beanfactory/GreetingTemplateConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/beanfactory/GreetingTemplateConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
public class GreetingTemplateConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean(GreetingTemplateBeanFactoryPostProcessor.TARGET_BEAN_NAME)
    public GreetingTemplate greetingTemplate() {
        GreetingTemplate template = new GreetingTemplate();
        template.setMessagePrefix("raw-prefix");
        return template;
    }

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public static BeanFactoryPostProcessor greetingTemplateBeanFactoryPostProcessor() {
        // Static @Bean lets Spring create the BeanFactoryPostProcessor before regular @Configuration instantiation.
        return new GreetingTemplateBeanFactoryPostProcessor();
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

- 从 README 的接口或测试名称开始，先定位入口类。
- 找 Controller、Runner、Listener 或 AutoConfiguration 作为第一阅读点。
- 沿着构造器注入的依赖继续进入 Service、Repository 或扩展点类。

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/bean-factory-post-processor`：模块说明
- `GET /api/bean-factory-post-processor/greeting?name=Spring`：返回被改写后的 greeting 行为

## 调用验证

```bash
curl "http://localhost:8154/api/bean-factory-post-processor"
```

```bash
curl "http://localhost:8154/api/bean-factory-post-processor/greeting?name=Spring"
```

响应中的 `messagePrefix` 应为 `post-processed`，`processorTag` 应为 `bean-factory-post-processor`。

## 生产映射

生产系统可以用这个模式：

- 修改第三方 starter 注册的 BeanDefinition
- 为一类 Bean 统一追加默认属性
- 在 Bean 创建前替换不安全的默认配置
- 做定义层面的兼容适配

如果需要新增 BeanDefinition，应使用 `BeanDefinitionRegistryPostProcessor`；如果需要修改已经创建的对象，应使用 `BeanPostProcessor`。

## 生产差距

该示例用于隔离学习 BeanFactoryPostProcessor 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 74-SpringBoot-bean-factory-post-processor test
```

测试覆盖：

- 直接使用 `DefaultListableBeanFactory` 验证 BeanDefinition 改写
- 缺少目标 BeanDefinition 时不报错
- MockMvc 验证完整 Spring Boot 启动链路里的最终 Bean 行为

## 要点总结

1. `BeanFactoryPostProcessor`
2. `ConfigurableListableBeanFactory`
3. `BeanDefinition`
4. Bean 实例化前属性改写
5. `static @Bean` 注册早期扩展点

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
