---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - SpringSecurity
  - 认证授权
created: 2026-05-08
---
# Spring Security 入门

## 定义

Spring Security 是 Spring 生态的安全框架，用于处理认证、授权、会话、安全过滤器链、密码加密和常见 Web 安全防护。

## 要点

- SecurityFilterChain 是请求安全处理的核心入口。
- Authentication 表示用户身份，Authorization 判断访问权限。
- 密码必须使用 BCrypt 等安全哈希算法。
- 前后端分离项目常结合 Session、JWT 或 OAuth2。

## 相关概念

- [[认证授权总览：Session、JWT、OAuth2 与 OIDC]]
- [[JWT 登录认证完整流程]]
- [[RBAC 权限模型设计]]
