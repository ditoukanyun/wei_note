---
title: SpringBoot BeanPostProcessor
date: 2026-05-11
tags:
  - springboot
  - java
  - spring扩展点
module: 76-SpringBoot-bean-post-processor
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot BeanPostProcessor

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/76-SpringBoot-bean-post-processor`

## 核心思路

本模块演示 `BeanPostProcessor`：Bean 已经创建之后，在初始化前后对对象本身做加工。

## 能力点

- `BeanPostProcessor`
- `postProcessBeforeInitialization`
- `postProcessAfterInitialization`
- `InitializingBean`
- 对象级生命周期标记
- MockMvc 验证最终 Bean 状态

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot BeanPostProcessor 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/BeanPostProcessorController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/BeanPostProcessorController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/bean-post-processor")
public class BeanPostProcessorController {
    private final LifecycleProbe lifecycleProbe;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public BeanPostProcessorController(LifecycleProbe lifecycleProbe) {
        this.lifecycleProbe = lifecycleProbe;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "76-SpringBoot-bean-post-processor",
                "apis", List.of(
                        "GET /api/bean-post-processor",
                        "GET /api/bean-post-processor/probe"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/probe")
    public ApiResult<LifecycleProbe> probe() {
        return ApiResult.success(lifecycleProbe);
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/beanpost/LifecycleProbeConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/beanpost/LifecycleProbeConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
public class LifecycleProbeConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public LifecycleProbe lifecycleProbe() {
        return new LifecycleProbe();
    }

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public static BeanPostProcessor lifecycleProbeBeanPostProcessor() {
        // BeanPostProcessor works on created objects; modules 74 and 75 work on BeanDefinitions before this point.
        return new LifecycleProbeBeanPostProcessor();
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：LifecycleProbe

源码位置：`src/main/java/com/cloud/beanpost/LifecycleProbe.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/beanpost/LifecycleProbe.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class LifecycleProbe implements InitializingBean {
    private final boolean constructed;
    private boolean beforeInitialization;
    private boolean initialized;
    private boolean afterInitialization;
    private String processorTag = "none";

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public LifecycleProbe() {
        this.constructed = true;
    }

    @Override
    public void afterPropertiesSet() {
        this.initialized = true;
    }

    public boolean isConstructed() {
        return constructed;
    }

    public boolean isBeforeInitialization() {
        return beforeInitialization;
    }

    public void setBeforeInitialization(boolean beforeInitialization) {
        this.beforeInitialization = beforeInitialization;
    }

    public boolean isInitialized() {
        return initialized;
    }

    public boolean isAfterInitialization() {
        return afterInitialization;
    }

    public void setAfterInitialization(boolean afterInitialization) {
        this.afterInitialization = afterInitialization;
    }

    public String getProcessorTag() {
        return processorTag;
    }

    public void setProcessorTag(String processorTag) {
        this.processorTag = processorTag;
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 后置处理器：容器创建过程中如何扩展

源码位置：`src/main/java/com/cloud/beanpost/LifecycleProbeBeanPostProcessor.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/beanpost/LifecycleProbeBeanPostProcessor.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class LifecycleProbeBeanPostProcessor implements BeanPostProcessor {
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        if (bean instanceof LifecycleProbe probe) {
            probe.setBeforeInitialization(true);
            probe.setProcessorTag("bean-post-processor");
        }
        return bean;
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        if (bean instanceof LifecycleProbe probe) {
            probe.setAfterInitialization(true);
            probe.setProcessorTag("bean-post-processor");
        }
        return bean;
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

- `GET /api/bean-post-processor`：模块说明
- `GET /api/bean-post-processor/probe`：返回生命周期探针状态

## 调用验证

```bash
curl "http://localhost:8156/api/bean-post-processor"
```

```bash
curl "http://localhost:8156/api/bean-post-processor/probe"
```

## 生产映射

生产系统可以用这个模式：

- 给特定类型 Bean 增加初始化标记
- 包装或装饰已经创建的对象
- 注入对象级默认状态
- 做框架级生命周期增强

如果需要改 BeanDefinition，用 `BeanFactoryPostProcessor`；如果需要注册 BeanDefinition，用 `BeanDefinitionRegistryPostProcessor`。

## 生产差距

该示例用于隔离学习 BeanPostProcessor 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 76-SpringBoot-bean-post-processor test
```

测试覆盖：

- 直接使用 `DefaultListableBeanFactory` 验证 before/init/after 顺序
- 非目标 Bean 原样返回
- MockMvc 验证最终对象状态进入 controller

## 要点总结

1. `BeanPostProcessor`
2. `postProcessBeforeInitialization`
3. `postProcessAfterInitialization`
4. `InitializingBean`
5. 对象级生命周期标记

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
