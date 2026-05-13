---
type: wiki
area: "[[AI]]"
tags: [AI, LLM, Transformer, 缓存]
created: 2026-05-13
source: "[[科普一下：大模型Token的收费逻辑！]]"
---
# KV Cache

## 定义

KV Cache 是 Transformer 推理时保存历史 token 的 Key 和 Value 表示的缓存。它让模型在生成下一个 token 时复用已有上下文计算结果，避免每一步都从头重算全部历史序列。

## 作用

- 降低自回归生成时的重复计算。
- 支持长上下文下持续生成输出。
- 是 [[Prompt 缓存]] 能复用稳定前缀的基础。
- 会随着上下文和输出变长占用更多显存或高速缓存资源。

## 关键限制

- KV Cache 节省的是重复计算，不改变 Decode 必须逐 token 生成的事实。
- 长上下文会带来更大的缓存读写压力。
- 跨请求复用通常要求前缀完全一致，并受缓存有效期限制。

## 示例

如果多个请求都以同一段系统提示词和产品文档开头，服务端可以缓存这段前缀对应的 KV Cache。下一次请求命中相同前缀时，可以跳过这部分 Prefill 计算。

## 相关概念

- [[Prefill 与 Decode]]
- [[Prompt 缓存]]
- [[LLM Token 成本]]
- [[Transformer]]
- [[上下文工程]]

## 参考资料

- [[科普一下：大模型Token的收费逻辑！]]
