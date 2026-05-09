---
type: wiki
area: "[[通用技能]]"
tags: [Web安全]
created: 2026-05-08
---
# CSRF
CSRF 是跨站请求伪造，利用用户已登录状态发起非预期请求。

## 相关概念
- [[CSRF 攻击与防护]]
- [[前端安全总览：XSS、CSRF 与 CSP]]

## 攻击流程

```mermaid
flowchart LR
  A[用户登录目标站点] --> B[浏览恶意页面]
  B --> C[恶意页面发起请求]
  C --> D[浏览器自动携带 Cookie]
  D --> E[目标站点误认为用户操作]
```

## 防护检查清单

- 状态变更请求是否使用 CSRF Token 或双提交 Cookie。
- Cookie 是否设置合适的 `SameSite`。
- 关键操作是否要求二次确认或重新认证。
- 服务端是否校验 Origin 或 Referer 作为辅助信号。
- GET 请求是否避免执行写操作。

## 案例

用户登录后台后访问恶意网页，网页自动提交“修改邮箱”的表单。如果后台只依赖 Cookie 登录态且没有 CSRF Token，浏览器会自动携带 Cookie，导致操作被执行。

## 防护边界

CSRF 的关键在于攻击者不能读取响应，但能诱导浏览器携带用户凭证发起请求。因此防护重点是证明请求来自真实页面和真实意图。CSRF Token、`SameSite` Cookie、Origin/Referer 校验和关键操作二次确认可以组合使用。

不是所有接口风险相同。读取接口通常影响较小，状态变更接口、资金操作、权限变更和账号安全操作必须重点防护。服务端应拒绝用 GET 执行写操作，因为图片、链接和跳转都可能触发 GET。

若系统改用纯 Token 放在 Authorization Header，CSRF 风险会降低，但仍要关注 XSS 和 Token 存储安全。

## 常见误区

- 认为只要使用 POST 就不会被 CSRF。
- 只在前端加确认弹窗，服务端没有校验。
- 混淆 CSRF 和 XSS，忽略二者防护重点不同。
