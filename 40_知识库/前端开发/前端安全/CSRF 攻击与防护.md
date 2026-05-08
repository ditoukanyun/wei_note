---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - 安全
  - CSRF
created: 2026-05-08
---
# CSRF 攻击与防护

## 定义

CSRF 是攻击者诱导已登录用户向目标站点发起非预期请求的攻击方式，利用的是浏览器自动携带 Cookie 的机制。

## 防护

- 重要写操作使用 CSRF Token。
- Cookie 设置 `SameSite`。
- 校验 Origin 或 Referer。
- 关键操作增加二次确认。

## 相关概念

- [[前端安全总览：XSS、CSRF 与 CSP]]
- [[认证授权总览：Session、JWT、OAuth2 与 OIDC]]
