---
created: 2026-02-25
type: concept
category: AI/Models
tags: [AI, LLM, local-model, open-source]
aliases: [本地大模型, 本地AI]
area: [[AI]]
---
# Ollama

**定义**: Ollama 是一个开源工具，用于在本地机器上轻松运行大语言模型（LLM）。它简化了模型的下载、配置和运行过程，让用户无需复杂的设置就能在本地使用 AI。

## 主要特性

| 特性 | 说明 |
|------|------|
| **本地运行** | 模型完全在本地运行，数据不上传云端 |
| **一键安装** | 简单的安装脚本，几分钟完成部署 |
| **丰富模型** | 支持 Llama、Mistral、Gemma、Qwen 等主流开源模型 |
| **REST API** | 提供 OpenAI 兼容的 API 接口 |
| **跨平台** | 支持 macOS、Linux、Windows |

## 安装

### macOS / Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
下载安装包：[ollama.ai/download](https://ollama.ai/download/windows)

## 基本使用

### 拉取模型
```bash
# 下载 Llama 3.2
ollama pull llama3.2

# 下载 Mistral
ollama pull mistral

# 下载 CodeLlama（编程专用）
ollama pull codellama
```

### 运行模型
```bash
# 交互式对话
ollama run llama3.2

# 单条命令
ollama run llama3.2 "解释什么是机器学习"
```

### 列出已安装模型
```bash
ollama list
```

## 与 OpenClaw 集成

```bash
# 配置 OpenClaw 使用 Ollama
openclaw config set ai.provider "ollama"
openclaw config set ai.model "llama3.2"
openclaw config set ai.baseUrl "http://localhost:11434"
```

## 优缺点

### 优点
- ✅ **隐私安全**: 数据完全本地处理
- ✅ **无需联网**: 离线可用
- ✅ **无 API 费用**: 免费使用
- ✅ **可定制**: 可以微调自己的模型

### 缺点
- ❌ **性能受限**: 本地硬件决定模型大小和速度
- ❌ **能力差距**: 开源模型通常不如 GPT-4/Claude 强大
- ❌ **资源占用**: 需要足够的内存和显存

## 硬件要求

| 模型大小 | 最低内存 | 推荐配置 |
|----------|----------|----------|
| 7B (70亿参数) | 8GB | 16GB RAM |
| 13B (130亿参数) | 16GB | 32GB RAM |
| 70B (700亿参数) | 64GB | 128GB RAM + GPU |

> 💡 使用 GPU 可以大幅提升推理速度（支持 CUDA、Metal、ROCm）

## 常用模型推荐

| 模型 | 参数 | 特点 |
|------|------|------|
| **Llama 3.2** | 3B/11B | Meta 最新，多语言支持好 |
| **Mistral** | 7B | 性能优秀，速度快 |
| **Qwen 2.5** | 7B/14B | 阿里出品，中文表现好 |
| **Gemma 2** | 9B/27B | Google 出品，轻量高效 |
| **CodeLlama** | 7B/13B/34B | 编程专用 |
| **DeepSeek Coder** | 6.7B/33B | 中文编程强 |

## 相关概念

- [[AI Agent]] - 可以使用本地模型作为"大脑"
- [[LLM]] - Ollama 运行的是开源大语言模型
- [[OpenClaw]] - 支持与 Ollama 集成使用本地模型

---

*参考: [[OpenClaw]] 可通过 Ollama 连接本地模型*

## 实践流程

```mermaid
flowchart LR
  A[选择模型] --> B[拉取到本地]
  B --> C[运行和测试 Prompt]
  C --> D[接入应用或 Agent]
  D --> E[监控速度和资源]
```

## 实践检查清单

- 模型大小是否匹配本机内存和显存。
- 是否用目标任务样例测试中文、代码或推理能力。
- 是否记录模型版本和量化方式。
- 本地服务是否限制访问来源，避免被局域网滥用。
- 是否评估本地推理速度是否满足交互体验。

## 案例

本地知识库整理任务可以先用小模型做分类和摘要，再把复杂推理任务交给更强模型。这样能兼顾隐私、成本和质量。

## 常见误区

- 认为本地模型一定更安全，忽略本地服务暴露和数据落盘。
- 拉取过大的模型，导致响应极慢或内存不足。
- 不做任务评测，直接把模型接入生产流程。
