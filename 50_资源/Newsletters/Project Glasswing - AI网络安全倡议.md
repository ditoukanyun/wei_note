---
title: Project Glasswing - 保护关键软件的AI时代网络安全倡议
source: https://www.anthropic.com/glasswing
date: 2026-04-08
tags:
  - AI安全
  - 网络安全
  - Anthropic
  - Claude
  - 新闻
status: unread
---

# Project Glasswing - 保护关键软件的AI时代网络安全倡议

> [!info] 基本信息
> - **来源**: [Anthropic 官方公告](https://www.anthropic.com/glasswing)
> - **发布日期**: 2026-04-08
> - **项目性质**: 跨行业网络安全合作倡议

## 核心内容

Anthropic 今天宣布启动 **Project Glasswing**，这是一个汇聚多家科技巨头的网络安全倡议，旨在应对AI时代的新安全挑战。

### 参与企业

| 公司 | 角色 |
|------|------|
| Amazon Web Services | 云基础设施安全 |
| Anthropic | AI模型提供/协调 |
| Apple | 终端设备安全 |
| Broadcom | 企业软件安全 |
| Cisco | 网络安全 |
| CrowdStrike | 端点安全 |
| Google | 云安全/AI |
| JPMorganChase | 金融安全 |
| Linux Foundation | 开源安全 |
| Microsoft | 企业安全 |
| NVIDIA | 硬件安全 |
| Palo Alto Networks | 网络安全 |

### 核心技术：Claude Mythos Preview

这是一个**尚未发布的通用前沿模型**，展示了惊人的网络安全能力：

> [!warning] 关键发现
> Claude Mythos Preview 已发现**数千个高危漏洞**，包括存在于**所有主流操作系统和浏览器**中的漏洞。

#### 能力指标对比

| 基准测试 | Mythos Preview | Opus 4.6 |
|---------|----------------|----------|
| CyberGym (漏洞复现) | **83.1%** | 66.6% |
| SWE-bench Pro | **77.8%** | 53.4% |
| SWE-bench Verified | **93.9%** | 80.8% |
| Terminal-Bench 2.0 | **82.0%** | 65.4% |

### 实际发现案例

1. **OpenBSD 27年漏洞** - 可远程崩溃任何运行该系统的机器
2. **FFmpeg 16年漏洞** - 自动化测试工具500万次未发现的代码问题
3. **Linux内核权限提升** - 自主发现并串联多个漏洞实现提权

### 项目承诺

| 投入 | 金额/资源 |
|------|----------|
| Mythos Preview 使用额度 | 最高 **$100M** |
| 开源安全组织捐款 | **$400万** (Alpha-Omega $250万 + Apache $150万) |
| 覆盖组织 | 40+ 家关键软件基础设施维护者 |

### 定价

Project Glasswing 参与者可使用 Mythos Preview：
- 输入 tokens: **$25/百万**
- 输出 tokens: **$125/百万**

可通过 Claude API、Amazon Bedrock、Google Cloud Vertex AI 和 Microsoft Foundry 访问。

## 行业观点摘录

> "AI能力已经跨越了一个根本性改变保护关键基础设施紧迫性的阈值，没有回头路了。"
> — **Anthony Grieco**, Cisco 安全与信任高级副总裁

> "攻击者发现漏洞和利用漏洞的时间窗口已经崩溃——过去需要数月，现在AI可以在几分钟内完成。"
> — **Elia Zaitsev**, CrowdStrike 首席技术官

> "开源维护者历来只能自己摸索安全问题。通过让关键开源代码库维护者获得新一代AI模型，Project Glasswing 提供了一条可信路径来改变这一等式。"
> — **Jim Zemlin**, Linux Foundation CEO

## 后续计划

- **90天内**: Anthropic 将公开发布报告，分享修复的漏洞和改进措施
- **中期目标**: 与安全组织合作制定AI时代安全实践建议
- **长期愿景**: 建立独立第三方机构持续推动大规模网络安全项目

## 延伸阅读

- [Frontier Red Team 技术博客](https://red.anthropic.com/2026/mythos-preview)
- [Claude Mythos Preview 系统卡片](https://anthropic.com/claude-mythos-preview-system-card)
- [Anthropic 网络安全研究](https://www.anthropic.com/research/building-ai-cyber-defenders)

---

> [!note] 笔记
> 项目名称 Glasswing 取自玻璃翼蝶（*Greta oto*），寓意：透明翅膀让它"隐藏于 plain sight"——如同文中讨论的漏洞；同时透明也象征该项目倡导的透明方法论。
