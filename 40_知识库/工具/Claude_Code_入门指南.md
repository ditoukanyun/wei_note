---
type: wiki
created: 2026-02-11
area: "[[工具]]"
tags: [claude, ai-tool, skills, mcp, tutorial]
author: sky陈天
source: "公众号-陈天AI实战笔记"
status: complete
---

# Claude Code 入门指南

> 面向非程序员小白的保姆级教程，从概念到实操全过程。

## 概述

Claude Code 是一个强大的 AI 智能体，能读取电脑里的所有资料，使用各种工具完成多样化任务。它不仅仅是写代码的工具，更是能覆盖文档类工作、文件整理、任务规划等多种场景的生产力工具。

## 核心概念

### Claude Code 是什么？

Claude Code 是一个**能干活的 AI 智能体**，具备以下能力：

- 对表格进行复杂的拆分
- 根据本地文件整理文件夹
- 调用各种工具完成任务（剪视频、搜索、配图等）
- 自主执行任务并输出文件

**与 ChatGPT 的区别**：

| ChatGPT/DeepSeek | Claude Code |
|-----------------|-------------|
| 主要进行对话 | 能自主处理文件 |
| 需要手动上传文件 | 直接读取本地文件 |
| 一分钟内给出答案 | 能真正执行任务 |
| 每次对话像"傻子" | 能规划整个任务流程 |

**一句话理解**：Claude Code 像一个能干活的实习生，能规划任务、使用电脑文件、制作 PPT/Word/Excel 等资料。

### Skills 是什么？

Skills 本质上是**给 AI 的操作 SOP（标准操作流程）**，类似于工作中的工作流。

**传统工作流的问题**：
- 门槛高，拖拖拽拽费时间
- 不够智能，遇到小问题就报错
- 像流水线工人，需要人工串联

**Skills 的优势**：
- **灵活度**：固定大流程，过程中灵活使用资料
- **智能度**：遇到问题时像专家一样自主调试

**一句话总结**：Skills 是给 AI 搭的流水线，规定标准化流程、每一步怎么做、用什么工具、参考什么文档。

#### Skills 目录结构

```
skill-folder/
├── skill.md          # 核心文件，AI 的操作手册（必须）
├── README.md         # 给人看的说明书
├── reference/        # 知识库（参考资料、模板、样本）
├── examples/         # 案例库（好的输出示例）
├── scripts/          # 工具箱（脚本文件）
└── .clinerules       # 高级配置文件
```

💡 **提示**：很多 Skill 只需要 `skill.md` 就能运行，其他都是可选的。

### MCP 是什么？

MCP（Model Context Protocol）本质上是**AI 的 USB 接口**，解决 AI 使用工具的问题。

**与 Skills 的关系**：
- **MCP** 解决工具问题
- **Skills** 解决流程问题
- 两者**互为补充，不冲突**

## 安装配置

### 前置要求

- 科学上网（Claude Code 需要）
- 安装 Node.js（运行环境）
- 安装 Git（Windows 用户必需）

### 第一步：安装 Node.js

**Mac 用户（使用 Homebrew）**：

```bash
# 检查是否已安装
brew --version

# 未安装则先安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Node.js
brew install node

# 验证
node --version
```

**Windows 用户**：

1. 访问 https://nodejs.org/
2. 下载 LTS 版本（绿色按钮）
3. 运行安装包，一路点击"下一步"
4. 确保勾选 "Add to PATH"
5. 验证：`node --version`

**Windows 额外：安装 Git**

1. 访问 https://git-scm.com/download/win
2. 下载并运行安装程序
3. 一路 Next 使用默认设置
4. 验证：`git --version`

### 第二步：安装 Claude Code

```bash
npm install -g @anthropic-ai/claude-code --registry=https://registry.npmmirror.com

# 验证安装
claude --version
```

### 第三步：配置 API Key

**推荐：智谱 AI（国内用户）**

优势：
- 国内访问稳定，无需特殊网络
- 价格实惠，支持支付宝/微信
- 新用户有免费额度

**配置步骤**：

1. 注册智谱 AI 账号：https://open.bigmodel.cn/
2. 完成实名认证
3. 购买套餐（推荐 GLM Coding Pro 年度套餐 ¥192/年）
4. 创建 API Key 并复制

**配置方法**（推荐方法一）：

**方法一：使用智谱自动化助手（最简单）**

```bash
npx @z_ai/coding-helper
```

按界面提示操作，自动完成配置。

**方法二：手动修改配置文件**

创建/修改 `~/.claude/settings.json`：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your_zhipu_api_key",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": 1
  }
}
```

创建/修改 `~/.claude.json`：

```json
{
  "hasCompletedOnboarding": true
}
```

**验证配置**：

```bash
# 重新打开终端
claude

# 测试
请帮我看一下当前目录下有哪些文件
```

## Skills 的使用

### 安装 Skills

**方法一：使用 Skill Creator 创建**

```
请帮我安装这个 Skills：https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
```

**方法二：安装现成 Skills**

访问 https://skillsmp.com/，复制安装命令，在终端运行。

### 调用 Skills

```
请使用 【Skill名称】 来执行 【任务描述】
```

### 推荐 Skills 资源

| 资源 | 链接 | 说明 |
|-----|------|------|
| 官方仓库 | https://github.com/anthropics/skills | 源头，适合学习修改 |
| 精选合集 | https://github.com/ComposioHQ/awesome-claude-skills | 最全精选列表 |
| 中文社区 | https://claudecn.com/ | 中文教程和 Skills |
| 技能市场 | https://skillsmp.com/ | 搜索发现新 Skills |

💡 **建议**：先安装真正能发挥作用的 Skills，根据任务需求选择，不要盲目安装。

## 可视化界面推荐

推荐在代码编辑器中使用 Claude Code，可视化查看文件修改：

**推荐编辑器**：
- [Trea](https://www.trae.ai/)
- Cursor
- VS Code

**使用方法**：
1. 打开编辑器的"终端"（Terminal）
2. 在终端中输入 `claude` 启动
3. 即可可视化查看修改内容

## 常见问题解决

### 遇到错误怎么办？

**万能提示词**：

```
我是一个完全不懂编程的小白，我在【安装 Claude Code / 配置 API Key】的过程中遇到了这个错误：【把错误信息粘贴在这里】。我用的是 [Mac/Windows] 电脑。请用最简单的语言告诉我怎么解决，每一步要做什么。
```

### 终端相关

**什么是终端？**
- 电脑的"对话框"，用文字命令操作电脑
- AI 更喜欢这种方式，能直接读取文件、执行操作

**如何打开终端？**

- **Mac**：`Command + 空格` → 输入"终端"或"Terminal"
- **Windows**：`Win + R` → 输入 `cmd` → 回车

## 参考资源

- 智谱 AI 详细文档：https://docs.bigmodel.cn/cn/guide/develop/claude
- Claude Code 官方文档：https://docs.anthropic.com/en/docs/claude-code

## 相关阅读

- [[AI工具]] - AI 工具汇总
- [[MCP]] - Model Context Protocol 详解
- [[Obsidian]] - 知识管理工具

---

*原文作者：sky 陈天 | 公众号：陈天AI实战笔记*