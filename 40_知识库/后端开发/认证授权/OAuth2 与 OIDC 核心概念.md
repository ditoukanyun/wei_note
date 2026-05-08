---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - OAuth2
  - OIDC
created: 2026-05-08
---
# OAuth2 与 OIDC 核心概念

## 定义

OAuth2 是授权框架，允许第三方应用代表用户访问资源；OIDC 是建立在 OAuth2 之上的身份认证层，用于获取标准化用户身份信息。

## 要点

- OAuth2 解决“能访问什么资源”。
- OIDC 解决“用户是谁”。
- 授权码模式配合 PKCE 是现代 Web 与移动应用常见选择。
- Access Token 面向资源服务器，ID Token 面向客户端身份信息。

## 相关概念

- [[认证授权总览：Session、JWT、OAuth2 与 OIDC]]
- [[单点登录 SSO 实践]]
- [[前端鉴权与 Token 存储安全]]
