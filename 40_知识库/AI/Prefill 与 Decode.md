---
type: wiki
area: "[[AI]]"
tags: [AI, LLM, 推理, Token]
created: 2026-05-13
source: "[[科普一下：大模型Token的收费逻辑！]]"
---
# Prefill 与 Decode

## 定义

Prefill 与 Decode 是大模型推理的两个阶段。Prefill 处理用户输入并生成初始 [[KV Cache]]；Decode 根据已有上下文逐个生成输出 token。

## Prefill

- 发生在模型读取 Prompt 时。
- 输入 token 可以一次性进入矩阵运算，高度并行。
- 主要瓶颈是算力，GPU 计算单元利用率高。
- 输出结果之一是后续生成要复用的 [[KV Cache]]。

## Decode

- 发生在模型开始生成答案之后。
- 由于自回归机制，输出 token 必须一个接一个生成。
- 每个新 token 都依赖前面 token 的结果，无法像输入一样完全并行。
- 主要瓶颈变成显存带宽和缓存读写，吞吐量通常远低于 Prefill。

## 成本含义

输入 token 通常便宜，是因为 Prefill 可以批量并行处理；输出 token 通常更贵，是因为 Decode 串行生成、吞吐低、资源占用时间更长。

## 相关概念

- [[LLM Token 成本]]
- [[KV Cache]]
- [[Prompt 缓存]]
- [[Transformer]]
- [[上下文工程]]

## 参考资料

- [[科普一下：大模型Token的收费逻辑！]]
