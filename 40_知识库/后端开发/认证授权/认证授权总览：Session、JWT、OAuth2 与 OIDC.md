---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - 认证授权
  - 安全
created: 2026-04-30
---
# 认证授权总览：Session、JWT、OAuth2 与 OIDC

## 学习目标

- 区分认证、授权、会话管理和权限控制。
- 理解 Session、JWT、OAuth2、OIDC 的适用场景和取舍。
- 能为 Web 应用、开放平台和前后端分离系统设计登录与授权流程。

## 核心概念

- **认证**：确认用户是谁。
- **授权**：确认用户能做什么。
- **Session**：服务端保存登录态，客户端保存会话标识。
- **JWT**：自包含 Token，适合无状态校验，但撤销和续期需要额外设计。
- **OAuth2**：授权框架，用于第三方应用代表用户访问资源。
- **OIDC**：基于 OAuth2 的身份认证层，提供标准化用户身份信息。

## 推荐阅读顺序

1. [[SpringBoot/12-SpringBoot-Session登录]]
2. [[SpringBoot/09-SpringBoot-JWT认证]]
3. [[SpringBoot/16-SpringBoot-JWT-RBAC权限控制]]
4. 本文：统一认证授权模型。
5. 后续拆分文章：Spring Security、OAuth2、OIDC、SSO。

## 工程实践清单

- 内部管理系统优先从 Session 或 JWT + RBAC 开始。
- 第三方登录、开放授权和企业单点登录优先理解 OAuth2/OIDC。
- Token 设计需要同时考虑签发、校验、刷新、撤销和审计。
- 权限模型先明确资源、动作、角色和主体，再选择 RBAC 或 ABAC。

## 后续可拆分文章

- [[Spring Security 入门]]
- [[JWT 登录认证完整流程]]
- [[OAuth2 与 OIDC 核心概念]]
- [[RBAC 权限模型设计]]
- [[单点登录 SSO 实践]]

## 相关链接

- [[后端开发 MOC]]
- [[前端安全总览：XSS、CSRF 与 CSP]]
- [[SpringBoot/SpringBoot 学习计划]]
