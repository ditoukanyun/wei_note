---
title: SpringBoot 项目初始化与基本配置
date: 2026-04-20
tags:
  - springboot
  - java
  - 初始化
module: 01-SpringBoot-init
---
# SpringBoot 项目初始化与基本配置

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/01-SpringBoot-init`

## 项目结构

```
01-SpringBoot-init/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/com/cloud/
    │   │   ├── Application.java            # 启动类
    │   │   └── HelloWordController.java    # 示例控制器
    │   └── resources/
    │       └── application.properties      # 配置文件
    └── test/
        └── java/com/cloud/
            └── ApplicationTests.java       # 测试类
```

## 多模块体系

本项目采用 Maven 多模块（multi-module）结构，父 POM 关键配置：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| parent | `spring-boot-starter-parent:3.2.3` | SpringBoot 版本 |
| Java | 17 | JDK 版本 |
| packaging | `pom` | 父模块打包方式 |
| MyBatis | 3.0.3 | MyBatis Starter 版本 |
| Druid | 1.2.23 | 数据库连接池版本 |

## 核心代码

### 启动类 — Application.java

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

`@SpringBootApplication` 是组合注解，等价于：

| 注解 | 作用 |
|------|------|
| `@SpringBootConfiguration` | 标识配置类 |
| `@EnableAutoConfiguration` | 开启自动配置 |
| `@ComponentScan` | 组件扫描（同包及子包） |

### 控制器 — HelloWordController.java

```java
@RestController
public class HelloWordController {
    @GetMapping("/hello")
    public String sayHello() {
        return "Hello World";
    }
}
```

- `@RestController` = `@Controller` + `@ResponseBody`，方法返回值直接写入 HTTP 响应体
- `@GetMapping("/hello")` 映射 GET 请求到 `/hello`

### 配置文件 — application.properties

```properties
spring.application.name=01-SpringBoot-init
server.port=8002
```

| 属性 | 值 | 说明 |
|------|-----|------|
| `spring.application.name` | 01-SpringBoot-init | 应用名称，用于服务注册与日志 |
| `server.port` | 8002 | 内嵌 Tomcat 端口，默认 8080 |

### 模块依赖 — pom.xml

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

`spring-boot-starter-web` 包含：

- Spring MVC
- 内嵌 Tomcat
- Jackson（JSON 序列化）

## 启动流程

```mermaid
graph LR
    A[main 方法] --> B[SpringApplication.run]
    B --> C[创建 ApplicationContext]
    C --> D[执行自动配置]
    D --> E[启动内嵌 Tomcat]
    E --> F["监听 8002 端口"]
```

## 要点总结

1. **起步依赖**：`spring-boot-starter-web` 一个依赖即可搭建 Web 应用
2. **自动配置**：`@SpringBootApplication` 开启，无需手动配置 DispatcherServlet 等
3. **内嵌容器**：无需外部 Tomcat，`java -jar` 即可运行
4. **约定优于配置**：默认扫描启动类同包及子包下的组件
