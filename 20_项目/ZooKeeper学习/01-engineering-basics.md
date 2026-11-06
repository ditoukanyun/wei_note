---
type: reference
created: 2026-11-06
updated: 2026-11-06
area: "[[后端开发]]"
tags: [ZooKeeper, SpringBoot, Java, 工程结构]
---
# 01 这个工程是怎么跑起来的

> 受众：会写前端或业务代码，但没接触过 Spring Boot。
> 读完你应该能回答：`mvn spring-boot:run` 之后发生了什么？我在浏览器点一下按钮，请求经过了哪些层？配置里的 `zk.connect-string` 是怎么变成一个 Java 字段的？

## 本章解决什么问题

Java 工程对前端同学最陌生的不是语法，而是「没有显式入口、没有 `new`、对象自己就出现了」。本章把这件事拆开：

- 一个 `main` 方法怎么启动整个 Web 服务；
- 注解在做什么（它不是语法糖，是框架的装配声明）；
- 依赖注入（DI）为什么让代码里几乎看不到 `new`；
- 配置文件怎么绑定到对象；
- 一条 HTTP 请求的完整路径。

---

## 30 秒版本

| 问题 | 答案 |
| --- | --- |
| 入口在哪 | `LearnZkApplication.main`，`src/main/java/com/example/learnzk/LearnZkApplication.java:9` |
| 为什么没有 Tomcat 配置 | Spring Boot 内嵌 Tomcat，端口写在 `application.yml:1-2` |
| 对象谁创建的 | Spring 容器扫描注解，按构造器参数自动注入 |
| 配置怎么生效 | `@ConfigurationProperties(prefix = "zk")` 把 `zk.*` 绑定到 `ZkProperties` 的 setter |
| 前端在哪 | `src/main/resources/static/index.html`，由内嵌 Tomcat 直接当静态资源提供 |
| 接口为什么没有 `web.xml` | `@RestController` + `@GetMapping` 等注解被 Spring MVC 扫描成路由 |

---

## 1. 先跑起来

### 1.1 前置

- JDK 17；
- Maven；
- Docker（起 ZooKeeper 集群）。

版本矩阵见代码仓根目录的 `README.md` 第 1 节。

### 1.2 两条命令

```bash
docker compose up -d     # 三节点 ZK：宿主机 2185 / 2186 / 2187
mvn spring-boot:run      # 编译 + 启动应用，占用 8088
```

`mvn spring-boot:run` 做三件事：解析 `pom.xml` 下载依赖 → 编译 `src/main/java` → 用当前 classpath 启动 `LearnZkApplication`。

打包成可执行 jar 则是：

```bash
mvn package
java -jar target/learn-zk-0.0.1-SNAPSHOT.jar
```

### 1.3 验证

```bash
curl http://localhost:8088/api/zk/health
```

返回体里 `connected=true`、`state=CONNECTED` 就说明应用和 ZK 都通了（接口实现见 `src/main/java/com/example/learnzk/web/ZkController.java:43-51`）。

浏览器打开 <http://localhost:8088/index.html>，三个页签分别对应 CRUD、Watch、分布式锁。

---

## 2. Maven 在干什么

`pom.xml` 只做三件事：

**① 继承一个父 POM**

```xml
<parent>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.5</version>
</parent>
```

见 `pom.xml:9-10`。父 POM 帮你管好依赖版本、编译器插件、打包插件。所以下面引依赖时大多不用写 `<version>`。

**② 声明属性**

```xml
<java.version>17</java.version>
<curator.version>5.7.1</curator.version>
```

见 `pom.xml:21-22`。`${curator.version}` 这种占位符就是从这里取的。

**③ 声明依赖**

```xml
<dependency>
    <groupId>org.apache.curator</groupId>
    <artifactId>curator-framework</artifactId>
    <version>${curator.version}</version>
</dependency>
```

见 `pom.xml:38-45`。坐标格式是 `groupId:artifactId:version`。下载后的 jar 放在本机 Maven 仓库（默认 `~/.m2/repository`），多个项目共享。

依赖树可以这样看：

```bash
mvn dependency:tree | grep -i -E "curator|zookeeper"
```

你会看到 Curator 5.7.1 实际带的是 ZooKeeper 3.9.2 客户端——服务端是 3.9.5，客户端小版本不完全一致是正常的，协议兼容。

---

## 3. Spring Boot 启动时发生了什么

```java
@SpringBootApplication
public class LearnZkApplication {
    public static void main(String[] args) {
        SpringApplication.run(LearnZkApplication.class, args);
    }
}
```

`src/main/java/com/example/learnzk/LearnZkApplication.java:6-11`。

### 3.1 启动六步

1. **`SpringApplication.run`** 创建 Spring 容器（`ApplicationContext`）。
2. **`@SpringBootApplication`** 是三个注解的组合：
   - `@Configuration`：这个类可以定义 Bean；
   - `@EnableAutoConfiguration`：根据 classpath 里的 jar 自动配置（有 `spring-boot-starter-web` 就配 Tomcat 和 Spring MVC，有 Jackson 就配 JSON 序列化）；
   - `@ComponentScan`：扫描当前包 `com.example.learnzk` 及子包。
3. **扫描组件**：带 `@Service`、`@RestController`、`@Configuration` 的类被登记为 Bean 定义。
4. **创建 Bean**：按依赖顺序实例化。构造器需要什么参数，容器就从已创建的 Bean 里找。
5. **内嵌 Tomcat 启动**：读取 `server.port`（`application.yml:1-2`），默认监听 8088。
6. **执行 `ApplicationRunner`**：`ZkCrudDemoRunner` 在这一步跑启动演示（`src/main/java/com/example/learnzk/demo/ZkCrudDemoRunner.java:37-47`）。

### 3.2 依赖注入：为什么看不到 `new`

```java
@RestController
@RequestMapping("/api/zk")
public class ZkController {

    private final ZkService zkService;
    private final ZkWatchService watchService;

    public ZkController(ZkService zkService, ZkWatchService watchService, ZkProperties props) {
        this.zkService = zkService;
        ...
    }
}
```

`src/main/java/com/example/learnzk/web/ZkController.java:29-41`。

容器创建 `ZkController` 时，发现构造器要 `ZkService`，就先创建 `ZkService`；`ZkService` 又要 `CuratorFramework`，于是去执行 `ZkConfig` 里的 `@Bean` 方法。整条依赖链自动拼好。

**为什么用构造器注入而不是字段注入**：依赖是 `final` 的，对象创建完就完整可用；写单元测试时可以直接 `new ZkController(mockService, ...)`，不需要启动容器。

### 3.3 ZooKeeper 连接是在「创建 Bean」阶段建立的

```java
@Bean(destroyMethod = "close")
public CuratorFramework curatorFramework(ZkProperties props) throws InterruptedException {
    ...
    client.start();
    if (!client.blockUntilConnected(waitMs, TimeUnit.MILLISECONDS)) {
        throw new IllegalStateException("连接 ZooKeeper 超时...");
    }
    return client;
}
```

`src/main/java/com/example/learnzk/config/ZkConfig.java:23-45`。

这带来一个直接后果：**ZK 连不上，应用起不来**。这是刻意的——演示工程希望问题在启动时就暴露，而不是等到第一个请求才报错。

`destroyMethod = "close"` 表示容器关闭时调用 `CuratorFramework.close()`，正常释放会话；否则服务端要等到会话超时（本项目 30s）才会清理临时节点。

---

## 4. 注解速查表

| 注解 | 出现位置 | 作用 |
| --- | --- | --- |
| `@SpringBootApplication` | `src/main/java/com/example/learnzk/LearnZkApplication.java:6` | 启动类三合一 |
| `@Configuration` | `config/ZkConfig.java:17` | 声明这是一个 Bean 工厂类 |
| `@Bean` | `config/ZkConfig.java:23` | 方法返回值交给容器管理 |
| `@ConfigurationProperties(prefix = "zk")` | `config/ZkProperties.java:7` | 把 `zk.*` 配置绑定到字段 |
| `@EnableConfigurationProperties` | `config/ZkConfig.java:18` | 让 `ZkProperties` 真正注册成 Bean |
| `@Service` | `service/ZkService.java:25` | 业务层组件 |
| `@RestController` | `web/ZkController.java:29` | 控制器，返回值直接写进响应体 |
| `@RequestMapping("/api/zk")` | `web/ZkController.java:30` | 类级路径前缀 |
| `@GetMapping` / `@PostMapping` / `@PutMapping` / `@DeleteMapping` | `web/ZkController.java:43-120` | 方法级路由 + HTTP 方法 |
| `@RequestBody` | `web/ZkController.java:56` | 请求体 JSON → Java 对象 |
| `@RequestParam` | `web/ZkController.java:68` | URL 查询参数 → 方法参数 |
| `@Valid` | `web/ZkController.java:56` | 触发 DTO 上的 `@NotBlank` 等校验 |
| `@RestControllerAdvice` + `@ExceptionHandler` | `web/ZkExceptionHandler.java:12-17` | 全局异常 → 统一响应 |
| `@ConditionalOnProperty` | `demo/ZkCrudDemoRunner.java:23` | 满足配置条件才注册这个 Bean |

### 4.1 请求参数和请求体怎么区分

- `GET /api/zk/nodes?path=/foo` → `@RequestParam String path`；
- `POST /api/zk/nodes` + JSON body → `@RequestBody CreateNodeRequest req`。

### 4.2 DTO 是 record，不是 class

```java
public record CreateNodeRequest(
        @NotBlank(message = "path 不能为空") String path,
        String data,
        String mode,
        Boolean createParents
) {}
```

`src/main/java/com/example/learnzk/web/dto/CreateNodeRequest.java:11-15`。

`record` 是 Java 16 正式支持的类型：一行声明字段，编译器自动生成构造器、`equals`、`hashCode` 和访问器。访问器名字是 `path()` 而不是 `getPath()`，但 **Jackson 序列化成 JSON 时字段名仍是 `path`**，前端不用关心这个差异。

---

## 5. 配置是怎么绑定到 Java 对象的

`application.yml`：

```yaml
zk:
  connect-string: 127.0.0.1:2185,127.0.0.1:2186,127.0.0.1:2187
  namespace: ""
  session-timeout: 30s
  connection-timeout: 15s
  base-sleep-time: 1s
  max-retries: 3
  demo:
    enabled: true
    path: /learn-zk/demo
```

`src/main/resources/application.yml:8-21`。

对应的类：

```java
@ConfigurationProperties(prefix = "zk")
public class ZkProperties {
    private String connectString = "127.0.0.1:2181";
    private Duration sessionTimeout = Duration.ofSeconds(30);
    ...
    private Demo demo = new Demo();
}
```

`src/main/java/com/example/learnzk/config/ZkProperties.java:7-24`。

**绑定规则（relaxed binding）**：

| YAML 写法 | Java 字段 |
| --- | --- |
| `connect-string` | `connectString` |
| `CONNECT_STRING` | `connectString` |
| `session-timeout: 30s` | `Duration sessionTimeout`（Spring 自动把 `30s` 解析成 `Duration`） |
| `demo.enabled` | `demo.enabled`（嵌套对象） |

注意两点：

1. 只有 `@ConfigurationProperties` 不够，还要 `@EnableConfigurationProperties(ZkProperties.class)`（`config/ZkConfig.java:18`）才会注册成 Bean；
2. 字段必须有 getter/setter，否则绑定不上。`record` 不适合做 `@ConfigurationProperties`（它是不可变的）。

---

## 6. 一条请求的完整链路

以「创建节点」为例：前端点「创建」，发 `POST /api/zk/nodes`。

```
浏览器 index.html
   │  call('POST', API + '/nodes', body)      index.html:296-306
   ▼
Tomcat（8088）
   │  按 HTTP 方法和路径匹配
   ▼
ZkController.create                            ZkController.java:55-63
   │  @Valid 校验 DTO → Jackson 反序列化
   │  parseMode("PERSISTENT")                  ZkController.java:126-137
   ▼
ZkService.create                               ZkService.java:45-62
   │  ZkPath.normalize(path)                   ZkPath.java:12-27
   │  选择是否 creatingParentsIfNeeded()
   ▼
CuratorFramework.create().forPath(...)          ZkService.java:51-58
   │  连接池 + 重试 + 会话
   ▼
ZooKeeper 集群（Leader 处理写请求，过半确认后提交）
   │
   ▼
返回真实路径 → ApiResponse.ok(...)              ZkController.java:62
   │  Jackson 序列化为 {"code":0,"message":"创建成功","data":"/learn-zk/..."}
   ▼
浏览器
```

失败分支走的是另一条路：

```
ZkService 抛出 KeeperException
   ▼
@RestControllerAdvice 捕获                ZkExceptionHandler.java:17-31
   ▼
KeeperException.Code → HTTP 状态码         ZkExceptionHandler.java:20-27
   ▼
ApiResponse.fail(status, "NODEEXISTS: ... \n→ 下一步该怎么做")
```

这也是为什么前端能看到 409 + 一句中文提示，而不是 500 + 堆栈。

### 6.1 统一响应结构

```java
public record ApiResponse<T>(int code, String message, T data) {
    public static <T> ApiResponse<T> ok(T data) { ... }
    public static <T> ApiResponse<T> fail(int code, String message) { ... }
}
```

`src/main/java/com/example/learnzk/web/ApiResponse.java:3-15`。

约定：`code = 0` 表示成功，失败时 `code` 与 HTTP 状态码一致（409、404、400...）。

---

## 7. 日志

### 7.1 门面与实现

代码里用的是 SLF4J 门面：

```java
private static final Logger log = LoggerFactory.getLogger(ZkService.class);
```

实际输出由 Logback 完成（Spring Boot 默认集成）。好处是以后换日志框架不用改业务代码。

### 7.2 本项目的两份日志

`src/main/resources/logback-spring.xml`：

| Appender | 目标 | 内容 |
| --- | --- | --- |
| `CONSOLE` | 控制台 | root 级，所有应用日志 |
| `ZK_LOCK_FILE` | `logs/zk-lock-demo.log` | 只收 logger 名为 `ZK_LOCK` 的日志 |

关键配置：

```xml
<logger name="ZK_LOCK" level="INFO" additivity="true">
    <appender-ref ref="ZK_LOCK_FILE"/>
</logger>
```

`src/main/resources/logback-spring.xml:23-25`。

- `additivity="true"`：这份日志除了写文件，还会继续往 root 传递，所以控制台也能看到；
- 滚动策略：单文件 10MB、按天切、保留 7 天、总量上限 200MB（`logback-spring.xml:10-15`）。

### 7.3 为什么用 logger 名而不是类名

```java
private static final Logger LOG = LoggerFactory.getLogger("ZK_LOCK");
```

`src/main/java/com/example/learnzk/service/DistributedLockService.java:41`。

用类名的话，日志会混在 `com.example.learnzk.service.*` 里，无法单独落到一个业务文件。用一个自定义名字，等于给这类日志开了个「频道」，配置里按频道分发。

### 7.4 调整日志级别

`application.yml:23-27`：

```yaml
logging:
  level:
    org.apache.zookeeper: WARN    # ZK 客户端内部日志太吵
    org.apache.curator: INFO
    com.example.learnzk: DEBUG
```

想看 Curator 的重连细节，把 `org.apache.curator` 改成 `DEBUG`。

---

## 8. 前端是怎么接进来的

### 8.1 静态资源

`src/main/resources/static/` 下的文件由 Tomcat 直接提供，不需要额外配置。所以 `static/index.html` 的访问路径就是 `/index.html`（根路径 `/` 会返回它）。

它和 `/api/zk/**` 不冲突：Spring MVC 先匹配控制器，匹配不到才落到静态资源处理。

### 8.2 三个页签

```html
<button class="tab active" data-tab="crud" onclick="switchTab('crud')">节点 CRUD</button>
<button class="tab" data-tab="watch" onclick="switchTab('watch')">Watch 监听</button>
<button class="tab" data-tab="lock" onclick="switchTab('lock')">分布式锁</button>
```

`src/main/resources/static/index.html:150-152`。

切换逻辑在 `index.html:283` 的 `switchTab`：给选中的按钮加 `active`，给对应 panel 加 `active`，再用 `history.replaceState` 把 `#crud` / `#watch` / `#lock` 写进地址栏。所以：

- 刷新后还停在原页签；
- 可以把 `index.html#lock` 直接发给别人。

### 8.3 请求封装

```js
const API = '/api/zk';

async function call(method, url, body) {
  ...
  const res = await fetch(url, opt);
  ...
}
```

`src/main/resources/static/index.html:277,296-306`。

统一在这里处理 JSON 头、错误提示和 `ApiResponse` 解包；业务函数只关心 `data`。

---

## 9. 自检

不看代码回答：

1. `ZkProperties` 为什么必须被 `@EnableConfigurationProperties` 注册一次？
2. `ZkConfig.curatorFramework` 方法上的 `destroyMethod = "close"` 如果不写，会发生什么？
3. 为什么 `ZkController` 里没有 `new ZkService()`？
4. 一个 `POST /api/zk/nodes` 请求，从进入 Tomcat 到写到 ZK，中间经过哪几个类？
5. `logs/zk-lock-demo.log` 为什么不会混入其他模块的日志？

答案分别对应：第 5 节、第 3.3 节、第 3.2 节、第 6 节、第 7.3 节。

---

## 10. 延伸阅读

- Spring Boot 官方文档：<https://docs.spring.io/spring-boot/>（「Core Features」讲 Bean 与配置，「Web」讲 MVC）
- Maven 依赖机制：<https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html>
- Java `record`：<https://docs.oracle.com/en/java/javase/17/language/records.html>

下一篇：[`02-zookeeper-principles.md`](02-zookeeper-principles.md)
