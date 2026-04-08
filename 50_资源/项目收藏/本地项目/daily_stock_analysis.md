# daily_stock_analysis - 股票智能分析系统

- **路径**: `/code/daily_stock_analysis`
- **GitHub**: https://github.com/ZhuLinsen/daily_stock_analysis
- **标签**: #股票 #AI分析 #量化 #Python

## 简介
基于 AI 大模型的 A股/港股/美股自选股智能分析系统，每日自动分析并推送「决策仪表盘」到企业微信/飞书/Telegram/Discord/邮箱。

## 主要功能

| 模块 | 功能 |
|------|------|
| AI 决策仪表盘 | 一句话核心结论 + 精确买卖点位 + 操作检查清单 |
| 多维度分析 | 技术面 + 筹码分布 + 舆情情报 + 实时行情 |
| 全球市场 | A股、港股、美股及美股指数 |
| 策略系统 | A股「三段式复盘策略」、美股「Regime Strategy」 |
| 智能导入 | 图片、CSV/Excel、剪贴板粘贴导入自选股 |
| Agent 问股 | 多轮策略问答，支持 11 种内置策略 |
| 多渠道推送 | 企业微信、飞书、Telegram、Discord、钉钉、邮件 |
| 自动化 | GitHub Actions 定时执行 |

## 技术栈

- **AI 模型**: LiteLLM 统一调用（Gemini、GPT、Claude、DeepSeek 等）
- **行情数据**: AkShare、Tushare、Pytdx、Baostock、YFinance
- **新闻搜索**: Tavily、SerpAPI、Bocha、Brave
- **Web 框架**: FastAPI + React
- **部署**: Docker、GitHub Actions

## 常用命令

```bash
# 本地运行
cd /code/daily_stock_analysis
pip install -r requirements.txt
cp .env.example .env
python main.py

# 启动 Web 界面
python main.py --webui

# 仅启动 Web
python main.py --webui-only

# 手动执行分析
python main.py --force-run
```

## 配置文件

- **环境变量**: `.env`（从 `.env.example` 复制）
- **LLM 配置**: `litellm_config.yaml`（可选高级配置）
- **Docker**: `docker/` 目录

## 重要文件

| 文件 | 说明 |
|------|------|
| `main.py` | 主入口 |
| `analyzer_service.py` | 分析服务 |
| `webui.py` | Web 界面入口 |
| `server.py` | FastAPI 服务 |
| `AGENTS.md` | AI Agent 配置 |
| `SKILL.md` | 项目技能文档 |

## 注意事项

1. **API Key 配置**: 至少配置一个 AI 模型（Gemini/OpenAI/DeepSeek等）和一个通知渠道
2. **股票列表**: 在 `.env` 中设置 `STOCK_LIST`，如 `600519,hk00700,AAPL`
3. **交易日检查**: 默认非交易日不执行，可设置 `TRADING_DAY_CHECK_ENABLED=false` 关闭
4. **Web 认证**: 设置 `ADMIN_AUTH_ENABLED=true` 启用登录保护

---

*记录时间: 2026-04-07*
