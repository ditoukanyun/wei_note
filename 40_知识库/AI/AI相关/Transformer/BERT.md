---
type: wiki
area: "[[AI]]"
tags: [Transformer, BERT]
created: 2026-05-08
---
# BERT
BERT 是基于 Transformer Encoder 的预训练语言模型，擅长理解类任务和双向上下文建模。

## 架构特点

- Encoder-only Transformer。
- 双向上下文建模，适合理解任务。
- 预训练任务包括 Masked Language Model。
- 常用于分类、实体识别、句子匹配和检索表示。

## 使用流程

```mermaid
flowchart TD
    A["输入文本"] --> B["Tokenizer"]
    B --> C["BERT Encoder"]
    C --> D["得到上下文表示"]
    D --> E["分类/匹配/抽取任务"]
```

## 实践检查清单

- 任务是否更偏理解而不是生成。
- 输入长度是否符合模型限制。
- 是否需要 fine-tuning 或只用 embedding。
- 中文任务是否选择合适的中文预训练模型。
- 输出是否通过标注集验证，而不是只看单例。

## 案例

客服工单分类可以用 BERT 对文本编码，再接分类层判断问题类型。若任务是生成回复，则更适合 GPT 类生成模型或 RAG 方案。

## 常见误区

- 用 BERT 做开放式生成。
- 不区分句向量检索和 token 级理解任务。

## 相关概念
- [[Transformer]]
- [[Attention Mechanism]]
