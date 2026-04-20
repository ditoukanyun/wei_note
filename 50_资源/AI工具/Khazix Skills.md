---
type: resource
tags:
  - AI工具
  - Agent Skills
  - Prompt
  - 知识沉淀
source: "[[GitHub - KKKKhazix/khazix-skills]]"
url: https://github.com/KKKKhazix/khazix-skills
created: 2026-04-15
---
# Khazix Skills
> 记录时间：2026-04-15
> 个人备注：挺好用，值得长期保留。

## 简介
`khazix-skills` 是卡兹克开源的 AI 工具箱，包含两类可复用资产：

- **Prompts**：可直接复制到任意 AI 对话/Deep Research 使用
- **Skills**：符合 Agent Skills 标准的结构化技能，安装后可被 Agent 自动加载

## 目前包含的核心内容
- `横纵分析法` Prompt：用于深度研究，强调纵向时间线 + 横向竞争格局分析
- `hv-analysis` Skill：自动联网收集信息并生成结构化研究输出
- `khazix-writer` Skill：面向公众号长文写作，内置风格规则和自检体系

## 安装方式（仓库提供）
### 方式 1：通过 Agent 对话安装
在支持 Skill 的 Agent（如 [[Claude Code]]、[[Codex]]、OpenClaw）中直接输入：

```text
安装这个 skill：https://github.com/KKKKhazix/khazix-skills
```

### 方式 2：手动安装
1. 从 Releases 下载对应 `.skill` 文件  
2. 拖到对应目录：

- Claude Code：`~/.claude/skills/`
- OpenClaw：`~/.openclaw/skills/`
- Codex：`~/.agents/skills/`

## 适用场景
- 做行业/公司深度研究，需要快速搭建高质量分析框架
- 批量产出结构化长文，需要稳定文风和质量自检
- 沉淀一套可迁移的个人 Agent 工作流

## 相关链接
- 仓库主页：https://github.com/KKKKhazix/khazix-skills
- Agent Skills 标准：https://agentskills.io
