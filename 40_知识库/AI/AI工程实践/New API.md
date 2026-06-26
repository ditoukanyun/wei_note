---
area: "[[AI工程实践]]"
tags: [AI网关, LLM网关, API中转, 模型聚合]
created: 2026-06-04
source:
  - https://github.com/QuantumNous/new-api
  - https://raw.githubusercontent.com/QuantumNous/new-api/main/README.md
  - https://docs.newapi.pro/en/docs/guide/feature-guide/admin/channel
---
# New API

## 定义

New API 是一个开源的 LLM 网关和 AI 资产管理系统，用于把多个模型服务商、多个 API Key、用户 Token、计费、额度、权限和日志统一管理起来。

它更像一个“通用模型网关”，适合做 OpenAI、Claude、Gemini、DeepSeek、OpenRouter 等多模型、多渠道的统一入口。

## 主要作用

- 统一模型调用入口：给用户暴露统一 API 地址和 Token。
- 多渠道管理：把不同上游服务商配置成 Channel。
- 多模型聚合：统一管理不同供应商的模型能力。
- 用户和额度管理：支持用户 Token、额度、计费、用量统计。
- 渠道调度：支持渠道优先级、权重随机、失败重试、多 Key 轮询或权重随机。
- 协议兼容：常用于兼容 OpenAI 风格 API，并转接不同模型供应商。

## 和账号池的关系

New API 可以做一定程度的“Key 池”或“渠道池”，但它的核心抽象是 **渠道 Channel**，不是订阅账号池。

适合的账号池形态：

- 多个 OpenAI API Key 作为多个渠道。
- 多个服务商 API Key 做统一模型网关。
- 按渠道设置优先级、权重、限额、模型映射。

不太适合的账号池形态：

- 多个订阅账号 OAuth 额度分发。
- Claude Code、Codex、Gemini CLI 这类需要粘性会话的 Agent 账号池。
- 需要账号级并发、用户级并发、失败冷却、会话绑定的订阅账号调度。

如果目标是“通用 API 中转 + 多模型聚合”，New API 更合适。  
如果目标是“多个订阅账号组成账号池，给内部用户分发统一 Key”，应优先看 [[Sub2API]]。

## 典型架构

```text
用户 / 应用 / Agent 客户端
  -> New API
  -> 渠道调度
  -> OpenAI / Claude / Gemini / DeepSeek / OpenRouter 等上游
```

## 适用场景

- 团队内部统一 LLM API 出口。
- 对多个模型供应商做统一鉴权、计费和用量统计。
- 需要支持不同用户、不同额度、不同模型权限。
- 希望把多个 API Key 统一封装成一个网关。

## 不适用或需要谨慎的场景

- 订阅账号共享或 OAuth 账号池分发。
- 需要强粘性会话的编程 Agent 工具。
- 需要对每个上游账号做细粒度并发、冷却、失败降权。

## 与 Sub2API 的区别

- New API：偏 **模型网关 / 渠道管理 / 多模型聚合**。
- [[Sub2API]]：偏 **订阅账号池 / 额度分发 / 粘性会话调度**。

二者可以组合，但初期不建议增加复杂度：

```text
用户
  -> New API：用户、套餐、模型聚合、统一入口
  -> Sub2API：订阅账号池调度
  -> 上游账号 / API
```

## 参考资料

- [QuantumNous/new-api](https://github.com/QuantumNous/new-api)
- [New API README](https://raw.githubusercontent.com/QuantumNous/new-api/main/README.md)
- [New API 渠道管理文档](https://docs.newapi.pro/en/docs/guide/feature-guide/admin/channel)
