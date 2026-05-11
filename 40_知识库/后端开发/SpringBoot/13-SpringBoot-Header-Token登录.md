---
title: SpringBoot Header Token 登录
date: 2026-04-20
tags:
  - springboot
  - java
  - token
  - 登录
module: 13-SpringBoot-header-token-login
area: [[后端开发]]
created: 2026-04-20
---
# SpringBoot Header Token 登录

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/13-SpringBoot-header-token-login`

## 核心思路

自定义 Token（UUID）存储在服务端内存中，客户端通过 `X-Auth-Token` 请求头携带，拦截器校验。

## Token 存储 — InMemoryTokenService

```java
@Service
public class InMemoryTokenService {
    private final Map<String, LoginUser> tokenStore = new ConcurrentHashMap<>();

    public String createToken(LoginUser loginUser) {
        String token = UUID.randomUUID().toString().replace("-", "");
        tokenStore.put(token, loginUser);
        return token;
    }

    public LoginUser getLoginUser(String token) { return tokenStore.get(token); }
    public void invalidate(String token) { tokenStore.remove(token); }
}
```

- `ConcurrentHashMap` 线程安全
- Token = UUID，无业务含义，不可逆

## 拦截器 — HeaderTokenInterceptor

```java
@Override
public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
    String token = request.getHeader("X-Auth-Token");
    LoginUser loginUser = tokenService.getLoginUser(token);
    if (loginUser == null) throw new UnauthenticatedException("未登录");
    request.setAttribute("loginUser", loginUser);  // 存入 request 供 Controller 使用
    return true;
}
```

- 与 JWT 不同：Token 本身不含用户信息，需查服务端
- 用户信息通过 `request.setAttribute` 传递（非 ThreadLocal）

## Session vs Header Token vs JWT 对比

| 维度 | Session | Header Token | JWT |
|------|---------|-------------|-----|
| Token 位置 | Cookie | 自定义 Header | Authorization Header |
| 用户信息 | 服务端 Session | 服务端内存 Map | Token 自带 |
| 注销 | `invalidate()` 立即生效 | `remove()` 立即生效 | 需黑名单 |
| 分布式 | 需 Session 共享 | 需 Redis 共享 | 天然支持 |
| Token 格式 | JSESSIONID | UUID | Base64 编码 JSON |

## API 接口

| 方法 | 路径 | 需登录 | 说明 |
|------|------|--------|------|
| POST | `/api/header/login` | 否 | 登录，返回 token |
| GET | `/api/header/me` | 是 | 当前用户 |
| POST | `/api/header/logout` | 是 | 登出 |
| GET | `/api/header/public` | 否 | 公开接口 |

## 要点总结

1. **Header Token**：简单 Token 方案，服务端存 Map，客户端传 Header
2. **立即可注销**：删除 Map 中的 key 即可，比 JWT 更易控制
3. **不适合生产**：内存存储，重启丢失、不支持分布式（应换 Redis）
4. **与 Session 的区别**：不用 Cookie，前后端分离友好
5. **与 JWT 的区别**：Token 无业务信息，需查服务端，但注销更简单

## 实践检查清单

- Token 是否有过期时间、刷新策略和主动失效能力。
- Token 存储是否从内存替换为 Redis 等共享存储，以支持多实例。
- 拦截器是否放行登录、健康检查和公开接口。
- 失败响应是否统一返回 401，而不是在业务层散落判断。
- 日志是否避免输出完整 Token，只记录脱敏后的标识。

## 案例

后台管理系统使用 Header Token 登录时，登录接口返回随机 Token，前端存入内存或安全存储，请求时放到 `X-Auth-Token`。用户登出时服务端删除 Token，后续请求立即失效。

## 常见误区

- 只生成 Token 不设置过期时间，导致泄露后长期有效。
- 多实例部署仍使用本地 Map，用户请求打到另一台机器就变成未登录。
- 在日志、异常或浏览器地址中暴露 Token。
