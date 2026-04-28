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

## API 接口

| 类型 | 路径 | 说明 |
|------|------|------|
| WS | `/ws-chat` | STOMP 连接端点 |
| WS | `/app/chat.send` | 发送聊天消息 |
| WS | `/topic/messages` | 订阅聊天消息 |
| WS | `/topic/online-users` | 订阅在线用户变更 |
| HTTP POST | `/api/chat/push` | 服务端主动推送 |
| HTTP GET | `/api/chat/online-users` | 查询在线用户 |

## 要点总结

1. **STOMP over WebSocket**：比纯 WebSocket 多了订阅/发布语义，Spring 原生支持
2. **`@MessageMapping`**：类似 `@RequestMapping`，处理客户端发送的 WS 消息
3. **SimpMessagingTemplate**：服务端主动推送消息，不限于 WS 触发
4. **PresenceChannelInterceptor**：通过 STOMP CONNECT/DISCONNECT 命令感知上下线
5. **SockJS 降级**：浏览器不支持 WebSocket 时自动降级为轮询
6. **广播 vs 点对点**：`/topic` 广播，`/queue` 点对点，本例使用广播
