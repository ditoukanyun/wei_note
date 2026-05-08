---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - 安全
  - CSP
created: 2026-05-08
---
# CSP 内容安全策略

## 定义

CSP 是通过 HTTP 响应头限制页面可加载脚本、样式、图片、字体和连接来源的浏览器安全机制。

## 要点

- `script-src` 控制脚本来源。
- `connect-src` 控制接口、WebSocket 等连接来源。
- `img-src`、`style-src`、`font-src` 控制资源来源。
- 可先使用 Report-Only 模式观察影响。

## 相关概念

- [[XSS 攻击与防护]]
- [[前端安全总览：XSS、CSRF 与 CSP]]
