---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - 安全
  - 认证授权
created: 2026-05-08
---
# 前端鉴权与 Token 存储安全

## 定义

前端鉴权与 Token 存储安全关注登录态在浏览器中的保存、读取、刷新和失效处理。前端只能改善体验，最终授权必须由服务端校验。

## 要点

- HttpOnly Cookie 能降低 XSS 窃取 Token 风险。
- localStorage 使用方便，但暴露给脚本，XSS 风险更高。
- Access Token 生命周期应短，刷新和撤销要有服务端策略。
- 权限按钮隐藏不能替代后端授权。

## 相关概念

- [[认证授权总览：Session、JWT、OAuth2 与 OIDC]]
- [[XSS 攻击与防护]]
- [[CSRF 攻击与防护]]
