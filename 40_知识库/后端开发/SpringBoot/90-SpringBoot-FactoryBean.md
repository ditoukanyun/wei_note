---
title: SpringBoot FactoryBean
date: 2026-05-11
tags:
  - springboot
  - java
module: 90-SpringBoot-factory-bean
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot FactoryBean

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/90-SpringBoot-factory-bean`

## 核心思路

本模块演示 Spring 的 `FactoryBean`：容器里注册的是工厂 Bean，但普通 bean name 返回的是工厂生产的产品对象；使用 `&beanName` 才能取到工厂本身。

## 能力点

- `FactoryBean<T>`
- `getObject()`
- `getObjectType()`
- `isSingleton()`
- `BeanFactory.FACTORY_BEAN_PREFIX`
- `&featureClient` factory dereference
- ApplicationContextRunner 验证产品 Bean 和工厂 Bean
- MockMvc 验证完整应用上下文中的 FactoryBean 行为

## 关键实现

配置类注册 factory bean：

```java
@Bean("featureClient")
FeatureClientFactoryBean featureClientFactoryBean() {
    return new FeatureClientFactoryBean();
}
```

工厂返回产品对象：

```java
public FeatureClient getObject() {
    return singleton;
}
```

取工厂本身时需要 `&` 前缀：

```java
applicationContext.getBean("&featureClient", FeatureClientFactoryBean.class);
```

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot FactoryBean 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/FactoryBeanController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/FactoryBeanController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/factory-bean")
public class FactoryBeanController {
    private final FeatureClient featureClient;
    private final ApplicationContext applicationContext;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public FactoryBeanController(FeatureClient featureClient, ApplicationContext applicationContext) {
        this.featureClient = featureClient;
        this.applicationContext = applicationContext;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "90-SpringBoot-factory-bean",
                "topic", "Spring FactoryBean product lookup and factory dereference",
                "apis", List.of(
                        "GET /api/factory-bean",
                        "GET /api/factory-bean/summary"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/summary")
    public ApiResult<Map<String, Object>> summary() {
        FeatureClientFactoryBean factoryBean = applicationContext.getBean(
                BeanFactory.FACTORY_BEAN_PREFIX + "featureClient",
                FeatureClientFactoryBean.class
        );
        Class<?> objectType = factoryBean.getObjectType();
        return ApiResult.success(Map.of(
                "product", Map.of(
                        "clientId", featureClient.clientId(),
                        "source", featureClient.source()
                ),
                "factory", Map.of(
                        "beanName", BeanFactory.FACTORY_BEAN_PREFIX + "featureClient",
                        "objectType", objectType == null ? "unknown" : objectType.getSimpleName(),
                        "singleton", factoryBean.isSingleton(),
                        "factoryMode", factoryBean.factoryMode()
                )
        ));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/factory/FactoryBeanConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/factory/FactoryBeanConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration(proxyBeanMethods = false)
public class FactoryBeanConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean("featureClient")
    FeatureClientFactoryBean featureClientFactoryBean() {
        // Spring exposes this bean name as FeatureClient; "&featureClient" dereferences the factory itself.
        return new FeatureClientFactoryBean();
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：FeatureClient

源码位置：`src/main/java/com/cloud/factory/FeatureClient.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/factory/FeatureClient.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public record FeatureClient(String clientId, String source) {
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 工厂 Bean：Bean 的创建可以被接管

源码位置：`src/main/java/com/cloud/factory/FeatureClientFactoryBean.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/factory/FeatureClientFactoryBean.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class FeatureClientFactoryBean implements FactoryBean<FeatureClient> {
    private final FeatureClient singleton = new FeatureClient("factory-client", "FeatureClientFactoryBean");

    @Override
    public FeatureClient getObject() {
        return singleton;
    }

    @Override
    public Class<?> getObjectType() {
        return FeatureClient.class;
    }

    @Override
    public boolean isSingleton() {
        return true;
    }

    public String factoryMode() {
        return "FactoryBean";
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

- `GET /api/factory-bean`：模块说明
- `GET /api/factory-bean/summary`：返回产品对象和工厂对象摘要

## 调用验证

```bash
curl "http://localhost:8170/api/factory-bean"
```

```bash
curl "http://localhost:8170/api/factory-bean/summary"
```

`/summary` 核心响应：

```json
{
  "product": {
    "clientId": "factory-client",
    "source": "FeatureClientFactoryBean"
  },
  "factory": {
    "beanName": "&featureClient",
    "objectType": "FeatureClient",
    "singleton": true,
    "factoryMode": "FactoryBean"
  }
}
```

## 生产映射

`FactoryBean` 常见于框架层：Mapper 工厂、代理工厂、集成客户端工厂、连接器工厂。业务代码通常只依赖产品对象，不直接依赖 factory；框架代码或诊断代码才需要通过 `&beanName` 取工厂本身。

适合使用这个模式的场景：

- 暴露由框架生成的客户端或代理对象
- 让业务代码注入产品接口，隐藏构造细节
- 需要让容器知道产品对象类型
- 阅读 MyBatis、Spring AOP、远程客户端代理相关源码

普通静态对象创建不需要使用 `FactoryBean`；直接 `@Bean` 更简单。

## 生产差距

该示例用于隔离学习 FactoryBean 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 90-SpringBoot-factory-bean test
```

测试覆盖：

- `FeatureClientFactoryBean` 返回单例 `FeatureClient`
- `getObjectType()` 返回 `FeatureClient.class`
- `isSingleton()` 返回 `true`
- `featureClient` bean name 返回产品对象
- `&featureClient` 返回工厂对象
- MockMvc 验证 metadata 和 summary 接口

## 要点总结

1. `FactoryBean<T>`
2. `getObject()`
3. `getObjectType()`
4. `isSingleton()`
5. `BeanFactory.FACTORY_BEAN_PREFIX`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
