---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - JWT
  - 认证授权
created: 2026-05-08
---
# JWT 登录认证完整流程

## 定义

JWT 登录认证流程是用户登录成功后由服务端签发 Token，客户端后续请求携带 Token，服务端验证签名、有效期和权限声明的认证方式。

## 流程

1. 用户提交账号密码。
2. 服务端校验身份并签发 Access Token。
3. 客户端请求携带 Token。
4. 服务端验证签名、过期时间和权限。
5. Token 过期后通过刷新机制或重新登录续期。

## 要点

- JWT 撤销和黑名单需要额外设计。
- 不应在 Token 中放敏感明文信息。
- 前端存储策略要结合 [[前端鉴权与 Token 存储安全]]。

## 相关概念

- [[认证授权总览：Session、JWT、OAuth2 与 OIDC]]
- [[SpringBoot/09-SpringBoot-JWT认证]]
- [[RBAC 权限模型设计]]
