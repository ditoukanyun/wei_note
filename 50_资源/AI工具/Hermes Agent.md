# Hermes Agent

> 来源：https://github.com/nousresearch/hermes-agent  
> 记录时间：2026-04-08

## 简介

由 **Nous Research** 开发的**自进化 AI Agent**，主打"能和你一起成长的智能体"。

## 核心特点

| 特性 | 说明 |
|------|------|
| **自学习循环** | 从经验中创建技能、使用时自动改进、主动持久化知识 |
| **跨平台** | Telegram、Discord、Slack、WhatsApp、Signal、CLI 统一入口 |
| **模型自由** | 支持 Nous Portal、OpenRouter(200+模型)、Kimi/Moonshot、OpenAI 等，随时切换 |
| **记忆系统** | 会话搜索 + LLM 摘要 + 用户画像建模 |
| **定时任务** | 内置 cron，支持自然语言配置定时报告/备份 |
| **子代理** | 可生成隔离子代理并行处理任务 |

## 与 OpenClaw 的关系

- Hermes 可以**一键迁移** OpenClaw 的配置：`hermes claw migrate`
- 迁移内容包括：SOUL.md、记忆、技能、API 密钥、消息平台配置等

## 技术架构

- **6 种运行后端**：本地、Docker、SSH、Daytona、Singularity、Modal
- **Serverless 支持**：Daytona/Modal 可在空闲时休眠，按需唤醒
- **Skills 系统**：兼容 [agentskills.io](https://agentskills.io) 开放标准
- **MCP 集成**：可连接任意 MCP 服务器扩展能力

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

## 常用命令

```bash
hermes              # 启动交互式 CLI
hermes model        # 选择 LLM 提供商和模型
hermes tools        # 配置启用的工具
hermes gateway      # 启动消息网关
hermes setup        # 运行完整设置向导
hermes claw migrate # 从 OpenClaw 迁移
hermes update       # 更新到最新版本
```

## 一句话总结

> Hermes 是 OpenClaw 的"竞品+进化版"——同样的多平台 AI 助手理念，但增加了**自学习、技能进化、更灵活的模型选择**，并且可以平滑迁移 OpenClaw 数据。

## 相关链接

- 官网文档：https://hermes-agent.nousresearch.com/docs/
- GitHub：https://github.com/nousresearch/hermes-agent
- Skills Hub：https://agentskills.io
