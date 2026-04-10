---
type: wiki
tags:
  - Claude
  - AI Agent
  - 云平台
  - AWS
  - Azure
  - GCP
  - 企业部署
source: "[[Claude Platform Documentation]]"
url: https://platform.claude.com/docs/en/managed-agents/overview
---

# Claude Platform Managed Agents

## 一句话总结

**Claude Platform Managed Agents** 是 Anthropic 提供的企业级 AI Agent 托管服务，支持在 AWS、Azure、GCP 等主流云平台上部署和管理 Claude 智能体，实现安全、可扩展的 AI 自动化工作流。

---

## 有什么用

### 核心能力

| 能力 | 说明 |
|------|------|
| **云端托管** | 在 AWS Bedrock、Azure AI Foundry、GCP Vertex AI 上运行 Claude Agents |
| **安全管理** | 企业级身份验证、访问控制、审计日志 |
| **自动扩缩容** | 根据工作负载自动调整计算资源 |
| **多 Agent 编排** | 协调多个专业 Agent 完成复杂任务 |
| **持久化存储** | 对话历史、知识库、执行状态的持久化 |
| **MCP 集成** | 通过 Model Context Protocol 连接企业数据源 |

### 适用场景

1. **企业 AI 自动化** - 安全的代码生成、文档处理、数据分析
2. **多步骤工作流** - 需要多个 Agent 协作的复杂任务
3. **合规要求** - 需要审计日志、数据驻留、加密的企业环境
4. **大规模部署** - 需要高可用和自动扩缩容的生产环境

---

## 云环境设置（Cloud Environment Setup）

### 1. AWS Bedrock 设置

#### 前置条件
- AWS 账户已开通 Bedrock 访问权限
- 在 Bedrock Console 申请 Claude 模型访问权限
- IAM 权限：`AmazonBedrockFullAccess`

#### 环境配置

```bash
# 启用 Bedrock 模式
export CLAUDE_CODE_USE_BEDROCK=1

# AWS 认证（推荐用 IAM Role，避免硬编码密钥）
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key

# 可选：指定模型版本
export ANTHROPIC_MODEL=eu.anthropic.claude-3-7-sonnet-20250219-v1:0
export ANTHROPIC_SMALL_FAST_MODEL=eu.anthropic.claude-3-haiku-20240307-v1:0
```

#### Claude Code 配置

创建 `~/.claude/settings.json`：

```json
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "us-east-1",
    "ANTHROPIC_MODEL": "anthropic.claude-3-7-sonnet-20250219-v1:0"
  }
}
```

#### Python SDK 使用

```python
import boto3
from anthropic import AnthropicBedrock

client = AnthropicBedrock(
    aws_region="us-east-1",
    aws_access_key="your_access_key",
    aws_secret_key="your_secret_key"
)

response = client.messages.create(
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

### 2. Azure AI Foundry 设置

#### 前置条件
- 付费 Azure 订阅（Enterprise 或 MCA-E）
- Microsoft Foundry 项目（支持区域：East US2、West Central US、Sweden Central）
- Azure Marketplace 模型订阅权限

#### 部署步骤

**1. 在 Azure Foundry 部署 Claude 模型**

```bash
# 登录 Azure
az login

# 设置订阅
az account set --subscription "your-subscription-id"

# 创建资源组
az group create --name claude-agents --location eastus2

# 部署模型（通过 Azure Portal 或 CLI）
# Base URL: https://<resource-name>.services.ai.azure.com/anthropic
```

**2. 环境变量配置**

```bash
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=your-resource-name
export ANTHROPIC_FOUNDRY_BASE_URL=https://your-resource.services.ai.azure.com

# 或使用 Entra ID 认证（推荐）
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id
```

**3. Python SDK 使用**

```python
from anthropic import AnthropicFoundry
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Entra ID 认证（推荐）
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
)

client = AnthropicFoundry(
    azure_ad_token_provider=token_provider,
    base_url="https://your-resource.services.ai.azure.com/anthropic"
)

# 或使用 API Key
client = AnthropicFoundry(
    api_key="your-foundry-api-key",
    base_url="https://your-resource.services.ai.azure.com/anthropic"
)
```

---

### 3. Google Vertex AI 设置

#### 前置条件
- GCP 项目已启用 Vertex AI API
- 服务账号有 `roles/aiplatform.user` 权限

#### 通过 Portkey 集成（推荐）

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.portkey.ai",
    "ANTHROPIC_AUTH_TOKEN": "YOUR_PORTKEY_API_KEY",
    "ANTHROPIC_CUSTOM_HEADERS": "x-portkey-api-key: YOUR_PORTKEY_API_KEY\nx-portkey-provider: vertex\nx-portkey-vertex-project-id: YOUR_GCP_PROJECT_ID\nx-portkey-vertex-region: us-central1",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-20250514"
  }
}
```

#### 直接 Vertex AI 配置

```bash
export CLAUDE_CODE_USE_VERTEX=1
export VERTEX_PROJECT_ID=your-gcp-project
export VERTEX_REGION=us-central1
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

#### 企业级 Fallback 配置

```json
{
  "strategy": { "mode": "fallback" },
  "targets": [
    { "provider": "@vertex-prod" },
    { "provider": "@anthropic-prod" }
  ],
  "cache": { "mode": "simple" },
  "retry": { "attempts": 3 }
}
```

---

## 跨云平台对比

| 特性 | AWS Bedrock | Azure AI Foundry | GCP Vertex AI |
|------|-------------|------------------|---------------|
| **认证方式** | IAM / API Keys | Entra ID / API Keys | Service Account / Portkey |
| **Claude Opus** | ✅ us-west-2 | ✅ East US2, Sweden | ✅ 部分区域 |
| **无服务器** | Lambda + Bedrock | Container Apps | Cloud Functions |
| **企业安全** | IAM, KMS, CloudTrail | Microsoft Entra, RBAC | IAM, Cloud Audit Logs |
| **模型版本控制** | 跨区域推理 | Global Standard | Model Garden |
| **延迟优化** | 边缘节点 | Azure CDN | Global Load Balancing |

---

## 多 Agent 编排设置

### 基础架构

```
┌─────────────────────────────────────────────────────────┐
│                  Claude Platform                        │
│              (Managed Agent Orchestrator)               │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Code Agent │    │  Doc Agent  │    │  Test Agent │
│  (Claude)   │    │  (Claude)   │    │  (Claude)   │
└─────────────┘    └─────────────┘    └─────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                  ┌─────────────────┐
                  │  Cloud Runtime  │
                  │ (AWS/Azure/GCP) │
                  └─────────────────┘
```

### 环境变量统一配置

```bash
# 选择云提供商（三选一）
export CLAUDE_CODE_USE_BEDROCK=1      # AWS
# export CLAUDE_CODE_USE_FOUNDRY=1    # Azure
# export CLAUDE_CODE_USE_VERTEX=1     # GCP

# 通用配置
export CLAUDE_AGENT_MODE=managed
export CLAUDE_MAX_AGENTS=5
export CLAUDE_AGENT_TIMEOUT=300
```

---

## 故障排查

### AWS Bedrock 常见问题

| 问题 | 解决方案 |
|------|----------|
| Model Access Denied | 在 Bedrock Console > Model Access 申请权限 |
| Region 错误 | Claude 3 Opus 仅在 us-west-2 可用 |
| Token 过期 | 配置 IAM Role 而非长期 Access Key |

### Azure Foundry 常见问题

| 问题 | 解决方案 |
|------|----------|
| 401/403 错误 | 检查 Entra ID scope 是否为 `https://ai.azure.com/.default` |
| Quota 不足 | 提交工单申请预览模型配额 |
| 部署失败 | 确认区域支持（East US2 / Sweden Central） |

### GCP Vertex AI 常见问题

| 问题 | 解决方案 |
|------|----------|
| 认证失败 | 检查服务账号权限和 JSON 密钥 |
| 区域不可用 | 使用 Portkey 作为中间层 |

---

## 相关资源

- [AWS Bedrock Claude 文档](https://aws.amazon.com/bedrock/claude/)
- [Azure AI Foundry Claude 指南](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-claude)
- [Portkey Vertex AI 集成](https://docs.portkey.ai/docs/integrations/libraries/claude-code-vertex)
- [Claude Code AWS Bedrock 配置](https://blog.playgroundtech.io/getting-started-with-claude-code-on-aws-bedrock-b22a0ea09ba5)
- [AWS Agent Plugins for Claude Code](https://builder.aws.com/content/39tWkKMGjPSXv4HOVoSm5C47ijN/from-deploy-to-aws-to-live-in-minutes-getting-started-with-agent-plugins-for-aws-and-claude-code)

---

## 使用建议

1. **生产环境**：优先使用 IAM Role（AWS）或 Entra ID（Azure），避免硬编码密钥
2. **多区域部署**：配置 Fallback 策略，确保高可用
3. **成本优化**：使用 Haiku 处理简单任务，Sonnet/Opus 处理复杂任务
4. **安全合规**：启用 CloudTrail（AWS）或 Activity Log（Azure）审计
5. **监控告警**：集成 CloudWatch / Azure Monitor / GCP Monitoring
