---
title: SpringBoot WebSocket 聊天
date: 2026-04-20
tags:
  - springboot
  - java
  - websocket
  - stomp
  - 聊天
module: 17-SpringBoot-websocket-chat
area: [[后端开发]]
created: 2026-04-20
---
# SpringBoot WebSocket 聊天

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/17-SpringBoot-websocket-chat`

## 核心思路

基于 STOMP over WebSocket 协议实现多人实时聊天，包含**用户上线/下线感知**和**服务端主动推送**两种消息模式。

## 项目结构

```
src/main/java/com/cloud/
├── config/WebSocketConfig.java
├── controller/
│   ├── ChatWsController.java           (WS 消息处理)
│   └── ChatPushController.java         (HTTP 推送 + 在线查询)
├── ws/PresenceChannelInterceptor.java  (上下线感知)
├── service/OnlineUserService.java
├── model/ChatMessage.java
├── common/ApiResult.java
└── exception/GlobalExceptionHandler.java
```

## 依赖与配置

| 依赖 | 说明 |
|------|------|
| `spring-boot-starter-web` | Web 框架 |
| `spring-boot-starter-websocket` | WebSocket + STOMP |

```yaml
server:
  port: 8097

spring:
  application:
    name: websocket-chat-demo
```

## 核心代码解析

### WebSocketConfig — STOMP 配置

```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws-chat")
            .setAllowedOriginPatterns("*")
            .withSockJS();                         // SockJS 降级
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        registry.setApplicationDestinationPrefixes("/app");   // 客户端发消息前缀
        registry.enableSimpleBroker("/topic", "/queue");      // 服务端推送前缀
    }

    @Override
    public void configureClientInboundChannel(ChannelRegistration registration) {
        registration.interceptors(presenceChannelInterceptor); // 上下线拦截
    }
}
```

> [!tip] STOMP 前缀规则
> - `/app/**`：客户端发送消息的目的地前缀
> - `/topic/**`：广播（一对多）
> - `/queue/**`：点对点（一对一）

### PresenceChannelInterceptor — 上下线感知

```java
@Override
public Message<?> preSend(Message<?> message, MessageChannel channel) {
    StompHeaderAccessor accessor = MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor.class);

    if (StompCommand.CONNECT.equals(accessor.getCommand())) {
        String userId = accessor.getFirstNativeHeader("userId");
        onlineUserService.userOnline(sessionId, userId);
        broadcastOnlineUsers();    // 广播在线列表
    }

    if (StompCommand.DISCONNECT.equals(accessor.getCommand())) {
        onlineUserService.userOffline(sessionId);
        broadcastOnlineUsers();
    }
    return message;
}
```

### ChatWsController — WS 消息路由

```java
@Controller
public class ChatWsController {
    @MessageMapping("/chat.send")          // 客户端发到 /app/chat.send
    public void send(ChatMessage message) {
        messagingTemplate.convertAndSend("/topic/messages", message);  // 广播到 /topic/messages
    }
}
```

### ChatPushController — HTTP 推送

```java
@PostMapping("/push")
public ApiResult<Map<String, Object>> push(@RequestParam String from, @RequestParam String content) {
    ChatMessage message = new ChatMessage();
    message.setType("SYSTEM");
    messagingTemplate.convertAndSend("/topic/messages", message);  // 服务端主动推
    return ApiResult.success(data);
}
```

### OnlineUserService — 在线用户管理

```java
@Service
public class OnlineUserService {
    private final Map<String, String> sessionUserMap = new ConcurrentHashMap<>();
    // sessionId → userId
    // getOnlineUsers() 去重后返回列表
}
```

### ChatMessage 消息模型

| 字段 | 类型 | 说明 |
|------|------|------|
| `from` | String | 发送者 |
| `content` | String | 消息内容 |
| `type` | String | USER / SYSTEM |
| `sentAt` | Long | 时间戳 |

## WebSocket 通信架构

```mermaid
graph TD
    subgraph 客户端
        C1[Client 1]
        C2[Client 2]
        C3[Client N]
    end

    subgraph 服务端
        EP[/ws-chat STOMP Endpoint]
        MB[MessageBroker /topic /queue]
        WS[ChatWsController /app/chat.send]
        PUSH[ChatPushController /api/chat/push]
        OLS[OnlineUserService]
        PI[PresenceChannelInterceptor]
    end

    C1 & C2 & C3 -->|STOMP CONNECT| EP
    EP --> PI
    PI --> OLS
    C1 -->|SEND /app/chat.send| WS
    WS -->|convertAndSend| MB
    PUSH -->|convertAndSend| MB
    MB -->|SUBSCRIBE /topic/messages| C1 & C2 & C3
    MB -->|SUBSCRIBE /topic/online-users| C1 & C2 & C3
```

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot WebSocket 聊天 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ChatPushController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ChatPushController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/chat")
public class ChatPushController {

    private final SimpMessagingTemplate messagingTemplate;
    private final OnlineUserService onlineUserService;

    public ChatPushController(SimpMessagingTemplate messagingTemplate,
                              OnlineUserService onlineUserService) {
        this.messagingTemplate = messagingTemplate;
        this.onlineUserService = onlineUserService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/push")
    public ApiResult<Map<String, Object>> push(@RequestParam String from,
                                                @RequestParam String content) {
        ChatMessage message = new ChatMessage();
        message.setFrom(from);
        message.setContent(content);
        message.setType("SYSTEM");
        message.setSentAt(System.currentTimeMillis());
        messagingTemplate.convertAndSend("/topic/messages", message);

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("pushed", true);
        data.put("sentAt", message.getSentAt());
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/online-users")
    public ApiResult<Map<String, Object>> onlineUsers() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("count", onlineUserService.getOnlineCount());
        data.put("users", onlineUserService.getOnlineUsers());
        return ApiResult.success(data);
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ChatWsController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ChatWsController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
@Controller
public class ChatWsController {

    private final SimpMessagingTemplate messagingTemplate;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ChatWsController(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    @MessageMapping("/chat.send")
    public void send(ChatMessage message) {
        if (message == null || message.getContent() == null || message.getContent().isBlank()) {
            return;
        }
        if (message.getFrom() == null || message.getFrom().isBlank()) {
            message.setFrom("anonymous");
        }
        if (message.getType() == null || message.getType().isBlank()) {
            message.setType("USER");
        }
        if (message.getSentAt() == null) {
            message.setSentAt(System.currentTimeMillis());
        }

        messagingTemplate.convertAndSend("/topic/messages", message);
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/OnlineUserService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/OnlineUserService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class OnlineUserService {

    private final Map<String, String> sessionUserMap = new ConcurrentHashMap<>();

    public void userOnline(String sessionId, String userId) {
        if (sessionId == null || sessionId.isBlank() || userId == null || userId.isBlank()) {
            return;
        }
        sessionUserMap.put(sessionId, userId);
    }

    public void userOffline(String sessionId) {
        if (sessionId == null || sessionId.isBlank()) {
            return;
        }
        sessionUserMap.remove(sessionId);
    }

    public List<String> getOnlineUsers() {
        Set<String> uniqueUsers = ConcurrentHashMap.newKeySet();
        uniqueUsers.addAll(sessionUserMap.values());

        List<String> users = new ArrayList<>(uniqueUsers);
        users.sort(Comparator.naturalOrder());
        return users;
    }

    public int getOnlineCount() {
        return getOnlineUsers().size();
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 请求拦截：进入 Controller 前做什么

源码位置：`src/main/java/com/cloud/ws/PresenceChannelInterceptor.java`

拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。

```java
// 文件：com/cloud/ws/PresenceChannelInterceptor.java
// 学习重点：拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。
@Component
public class PresenceChannelInterceptor implements ChannelInterceptor {

    private final OnlineUserService onlineUserService;
    private final ObjectProvider<SimpMessagingTemplate> messagingTemplateProvider;

    public PresenceChannelInterceptor(OnlineUserService onlineUserService,
                                      ObjectProvider<SimpMessagingTemplate> messagingTemplateProvider) {
        this.onlineUserService = onlineUserService;
        this.messagingTemplateProvider = messagingTemplateProvider;
    }

    @Override
    public Message<?> preSend(Message<?> message, MessageChannel channel) {
        StompHeaderAccessor accessor = MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor.class);
        if (accessor == null || accessor.getCommand() == null) {
            return message;
        }

        if (StompCommand.CONNECT.equals(accessor.getCommand())) {
            String userId = accessor.getFirstNativeHeader("userId");
            String sessionId = accessor.getSessionId();
            if (userId == null || userId.isBlank()) {
                userId = "guest-" + (sessionId == null ? "unknown" : sessionId);
            }
            onlineUserService.userOnline(sessionId, userId);
            broadcastOnlineUsers();
        }

        if (StompCommand.DISCONNECT.equals(accessor.getCommand())) {
            onlineUserService.userOffline(accessor.getSessionId());
            broadcastOnlineUsers();
        }

        return message;
    }

    private void broadcastOnlineUsers() {
        SimpMessagingTemplate messagingTemplate = messagingTemplateProvider.getIfAvailable();
        if (messagingTemplate == null) {
            return;
        }
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("count", onlineUserService.getOnlineCount());
        payload.put("users", onlineUserService.getOnlineUsers());
        payload.put("timestamp", System.currentTimeMillis());
        messagingTemplate.convertAndSend("/topic/online-users", payload);
    }
}
```

关键点拆解：

- 前置处理负责准备上下文，后置处理负责清理资源；这两个动作要成对出现。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. PresenceChannelInterceptor：请求进入 Controller 前准备上下文或校验
2. ChatPushController：接收 HTTP 请求并转换成 Java 方法调用
3. OnlineUserService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

| 类型 | 路径 | 说明 |
|------|------|------|
| WS | `/ws-chat` | STOMP 连接端点 |
| WS | `/app/chat.send` | 发送聊天消息 |
| WS | `/topic/messages` | 订阅聊天消息 |
| WS | `/topic/online-users` | 订阅在线用户变更 |
| HTTP POST | `/api/chat/push` | 服务端主动推送 |
| HTTP GET | `/api/chat/online-users` | 查询在线用户 |

## 生产差距

这个示例适合帮助初学者理解 WebSocket 聊天 的核心机制，但生产项目不能只停留在“能跑通”。真实落地时至少要补齐：统一鉴权、参数边界校验、异常响应、结构化日志、监控指标、自动化测试、配置隔离和容量评估。

如果模块涉及数据库、缓存、消息、网关、认证或外部服务，还要进一步考虑连接池、超时、重试、幂等、事务边界、数据一致性和故障告警。学习时可以先记住主流程，再用这些生产差距反向检查自己是否真正理解了案例。

## 要点总结

1. **STOMP over WebSocket**：比纯 WebSocket 多了订阅/发布语义，Spring 原生支持
2. **`@MessageMapping`**：类似 `@RequestMapping`，处理客户端发送的 WS 消息
3. **SimpMessagingTemplate**：服务端主动推送消息，不限于 WS 触发
4. **PresenceChannelInterceptor**：通过 STOMP CONNECT/DISCONNECT 命令感知上下线
5. **SockJS 降级**：浏览器不支持 WebSocket 时自动降级为轮询
6. **广播 vs 点对点**：`/topic` 广播，`/queue` 点对点，本例使用广播
