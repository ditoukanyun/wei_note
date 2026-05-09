---
title: Claude Code + Skills 保姆级入门教程
date: 2025-02-11
tags: [Claude-Code, Skills, MCP, AI工具, 教程, 入门指南]
category: 知识库/AI工具
status: active
author: sky陈天
source: https://mp.weixin.qq.com/s/TxQZca1mY46usqK08t7hNQ
aliases: [Claude Code 入门, Skills 教程]
priority: high
---
# Claude Code + Skills 保姆级入门教程

> [!info] 文章信息
> **作者**：sky陈天（企业AI营销咨询顾问）  
> **来源**：[陈天AI实战笔记](https://mp.weixin.qq.com/s/TxQZca1mY46usqK08t7hNQ)  
> **字数**：约12,000字  
> **目标读者**：完全不懂编程的小白/文科生

---

## 概述

本文是面向**非程序员**的 Claude Code 入门指南，用大白话讲解 Claude Code、Skills 和 MCP 的概念，并提供保姆级的安装配置教程。

> [!tip] 核心观点
> Claude Code 不只是写代码工具，而是一个**能干活的 AI 智能体**——可以处理文档、整理文件、做 PPT、自动化工作流等。

---

## 第一部分：核心概念

### 1.1 Claude Code 是什么？

**定义**：Claude Code 是一个非常厉害的 AI 智能体，能读取电脑里的所有资料，使用多种工具完成各种任务。

**能做什么**：
- 对表格进行复杂的拆分
- 根据本地文件整理文件夹
- 调用各种工具（剪视频、搜索、配图等）
- 自主执行任务并输出文件

**vs ChatGPT/DeepSeek**：

| 特性 | ChatGPT/DeepSeek | Claude Code |
|------|------------------|-------------|
| 交互方式 | 聊天对话 | 自主执行 |
| 文件处理 | 需手动上传 | 直接读取本地文件 |
| 任务执行 | 给出答案（1分钟内） | 真正执行任务 |
| 上下文记忆 | 每次对话需补充 | 自动关联本地资料 |

> [!quote] 一句话理解
> Claude Code 是一个**能干活的实习生**——能规划任务、使用电脑文件、制作各种文档。

---

### 1.2 Skills 是什么？

**定义**：Skills 是给 AI 的**操作 SOP**（标准操作流程），或者说给 AI 搭的**智能流水线**。

**解决的问题**：

| 传统方式 | Skills 方式 |
|----------|-------------|
| 多个 AI 智能体各自为政 | 统一流程，AI 自主协调 |
| 需要手动复制粘贴上下文 | AI 自动调用资料和工具 |
| 像流水线工人（初中生水平） | 像专家（会自己调试问题） |
| 拖拖拽拽费时间 | 标准化流程，灵活执行 |

**Skills 的目录结构**：

```
Skill文件夹/
├── skill.md          # 核心文件：AI 的操作手册（必需）
├── README.md         # 给人看的说明书
├── reference/        # 知识库：参考资料、模板、风格样本
├── examples/         # 案例库：示例输出
├── scripts/          # 工具箱：可执行的脚本
└── .clinerules       # 配置文件：高级规则设置
```

> [!note] 小提示
> 很多 Skill 只需要一个 `skill.md` 文件就能跑起来，其他都是可选的。

---

### 1.3 MCP 是什么？

**定义**：MCP（Model Context Protocol）是**AI 的 USB 接口**。

**作用**：解决 AI **使用工具**的问题。

**关系**：
- **Skills** = 解决流程问题（怎么做）
- **MCP** = 解决工具问题（用什么做）
- 两者**互为补充，不冲突**

---

## 第二部分：安装配置

### 2.1 前置要求

- ✅ 科学上网能力
- ✅ 30-60 分钟空闲时间
- ✅ 找心情好的时候操作

> [!warning] 遇到问题怎么办？
> 复制错误信息，用以下提示词问任何 AI（ChatGPT、Claude、DeepSeek 都可以）：
> ```
> 我是一个完全不懂编程的小白，我在【安装 Claude Code / 配置 API Key】
> 的过程中遇到了这个错误：【粘贴错误信息】。我用的是 【Mac/Windows】 电脑。
> 请用最简单的语言告诉我怎么解决，每一步要做什么。
> ```

---

### 2.2 了解终端

**什么是终端？**
- 电脑的"对话框"，用文字命令直接操作电脑
- 看起来是黑乎乎/白色的窗口，输入命令后按回车执行

**为什么 Claude Code 要用终端？**
- AI 更喜欢这种方式
- 可以直接读取电脑文件
- 比图形界面高效得多

**如何打开终端**：

| 系统 | 操作方式 |
|------|----------|
| Mac | `Command + 空格` → 输入"终端"或"Terminal" |
| Windows | `Win + R` → 输入 `cmd` → 回车 |

---

### 2.3 安装 Node.js

Node.js 是 Claude Code 的"运行环境"，就像手机 App 需要安装在手机系统上。

#### Mac 用户

**第一步：检查 Homebrew**
```bash
brew --version
```
- 如果显示版本号（如 `Homebrew 4.x.x`），已有 Homebrew，跳到第二步
- 如果显示 "command not found"，需先安装 Homebrew

**安装 Homebrew（如果没有）**：
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
> 可能需输入电脑密码（输入时不显示字符，正常），等几分钟完成

**第二步：用 Homebrew 安装 Node.js**
```bash
brew install node
```
> 等待 1-2 分钟

#### Windows 用户

**推荐方法：官网下载安装（最稳定）**

1. 访问 Node.js 官网：https://nodejs.org/
2. 点击左边绿色的 **"LTS"** 按钮（推荐版本，更稳定）
3. 下载 Windows 安装包（.msi 文件）
4. 双击运行安装程序
5. 一路点击"下一步"，确保勾选 **"Add to PATH"**
6. 完成后点击"完成"

#### 验证安装成功

**关闭之前打开的终端，重新打开新终端**（重要！），然后输入：
```bash
node --version
```

看到类似 `v20.10.0` 的版本号 = ✅ 安装成功  
显示"不是内部或外部命令" = ❌ 安装失败，换方式重试

---

### 2.4 Windows 用户额外步骤：安装 Git

> [!warning] 为什么 Windows 需要多这一步？
> 安装 Claude Code 的命令 (`npm`) 在下载复杂软件包时需要 Git。没有 Git 会报错。

**安装步骤**：

1. 访问 Git 官网下载页面：https://git-scm.com/download/win
2. 网站会自动下载合适的安装程序（.exe 文件）
3. 双击运行安装程序
4. **一路点击"Next"使用默认设置**

**验证安装成功**：

1. **重新打开终端**（关闭所有已打开终端窗口，再打开新的——重要！）
2. 输入：
```bash
git --version
```
3. 看到类似 `git version 2.45.1.windows.1` = ✅ 成功

---

### 2.5 安装 Claude Code

**官方安装地址**：https://docs.anthropic.com/en/docs/claude-code

在终端里输入：
```bash
npm install -g @anthropic-ai/claude-code --registry=https://registry.npmmirror.com
```

> [!info] 说明
> 终端会刷出一堆文字，这是正常的下载安装过程。耐心等待 1-3 分钟。

**验证安装成功**：
```bash
claude --version
```

显示版本号 = 🎉 安装成功！

---

### 2.6 设置 API Key

#### 什么是 API Key？

- 可以理解为**钥匙**或**会员卡**
- Claude Code 本身是"外壳"，真正干活的是云端 AI 模型
- 每次使用都会消耗"算力"，API Key 用于计费和验证身份

#### 为什么推荐智谱 AI？

| 优势 | 说明 |
|------|------|
| 国内访问稳定 | 不需要特殊网络 |
| 价格实惠 | 比官方 Claude API 便宜很多 |
| 支持国内支付 | 支付宝、微信都能充值 |
| 有免费额度 | 新用户注册送体验额度 |

#### 第一步：获取智谱 AI 的 API Key

**1. 注册账号**
- 打开智谱 AI 开放平台：https://open.bigmodel.cn/
- 右上角"注册/登录"，用手机号注册

**2. 实名认证（必须）**
- 登录后完成实名认证（国内 AI 服务要求）

**3. 购买套餐（强烈推荐年度套餐）**

> [!tip] 推荐方案：GLM Coding Pro 连续包年套餐
> - **原价**：¥480/年
> - **折扣价**：¥192/年
> - **包含内容**：Claude Pro 套餐的 3 倍用量
> - **购买链接**：https://www.bigmodel.cn/glm-coding?ic=IQKEJG5NOT

**4. 创建 API Key**
- 控制台找到"API 管理"或"API Key"
- 点击"创建新的 API Key"
- 起个名字（如"Claude Code 专用"）
- **立即复制 API Key 并保存好**

#### 第二步：配置 Claude Code

**方法一：使用智谱自动化助手（强烈推荐，最简单）**

智谱 AI 官方提供 **Coding Tool Helper** 自动化工具，一键完成配置。

**操作步骤**：

1. 在终端输入：
```bash
npx @z_ai/coding-helper
```

2. 按照界面提示操作：
   - 输入 Y 或直接按回车
   - 选择编码套餐
   - 输入刚才复制的 API Key
   - **强烈建议安装推荐的 MCP**

3. 全程图形化界面，约 1-2 分钟完成

**详细说明文档**：https://docs.bigmodel.cn/cn/guide/develop/claude

---

**方法二：手动修改配置文件（备选方案）**

如果自动化助手无法使用，手动修改两个文件：`settings.json` 和 `.claude.json`

**第一步：修改 `settings.json`**

**文件位置**：
- Mac/Linux：`~/.claude/settings.json`
- Windows：`C:\Users\你的用户名\.claude\settings.json`

**打开方式**：
- Mac：终端输入 `open ~/.claude/settings.json`
- Windows：文件资源管理器地址栏输入 `%USERPROFILE%\.claude`

**文件内容**（把 `your_zhipu_api_key` 替换成你的 API Key）：
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

**参数说明**：
- `ANTHROPIC_AUTH_TOKEN`：智谱 AI API Key（必填）
- `ANTHROPIC_BASE_URL`：智谱 AI 接口地址（必填）
- `API_TIMEOUT_MS`：超时时间，防止长任务被中断
- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`：禁用非必要流量

**第二步：修改 `.claude.json`**

**文件位置**：
- Mac/Linux：`~/.claude.json`
- Windows：`C:\Users\你的用户名\.claude.json`

**文件内容**：
```json
{
  "hasCompletedOnboarding": true
}
```

这个参数跳过首次启动的引导流程。

> [!warning] 重要提示
> - 确保 JSON 格式正确（注意逗号、引号、括号）
> - 可用在线 JSON 校验工具检查
> - 修改完成后，**必须重新打开终端才能生效**

---

**方法三：使用环境变量配置（高级用户）**

**Mac/Linux**：
```bash
export ANTHROPIC_API_KEY="your-zhipu-api-key-here"
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
```

永久生效：添加上面两行到 `~/.zshrc` 或 `~/.bash_profile`

**Windows**：
1. 右键"此电脑" → "属性"
2. "高级系统设置" → "环境变量"
3. 在"用户变量"中添加：
   - `ANTHROPIC_API_KEY` = 你的 API Key
   - `ANTHROPIC_BASE_URL` = `https://open.bigmodel.cn/api/paas/v4`

---

#### 第三步：测试是否配置成功

1. **重新打开终端**（重要，确保配置生效）
2. 输入：
```bash
claude
```
3. 第一次运行可能提示 "Do you want to use this API key"，选择 **Yes**
4. 提示是否信任 Claude Code 访问当前文件夹，选择 **Trust**（信任）
5. 试着问问题：
```
请帮我看一下当前目录下有哪些文件
```

能正常回答 = 🎉 **你已经成功入门了！**

---

## 第三部分：Skills 的使用和配置

### 3.1 创建 Skills

**方法一：用 Skill Creator 创建**

Skill Creator 是一个引导式创建 Skill 的工具。

**安装方法**：
在 Claude Code 中发送：
```
请帮我安装这个 Skills：https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
```

AI 会一步步指导下载安装，过程中可能会问 yes or no，按 yes 回车即可。

---

**方法二：安装现成的 Skills**

**去哪里找**：

| 来源 | 链接 | 说明 |
|------|------|------|
| 官方仓库 | https://github.com/anthropics/skills | Skills 的"源头"，适合学习 |
| 精选合集 | https://github.com/ComposioHQ/awesome-claude-skills | 最全的精选列表，分类清晰 |
| 中文社区 | https://claudecn.com/ | 中文教程和可直接使用的 Skills |
| 技能市场 | https://skillsmp.com/ | 可搜索发现新 Skills |

**安装方法**：
1. 在技能市场找到合适的 Skill
2. 复制右侧的命令
3. 在新终端中粘贴并回车
4. 安装完毕后，重新打开 Claude Code 即可使用

---

### 3.2 调用 Skills

**调用语法**：
```
请使用 【某个 Skill 的名字】 来执行 【什么任务】
```

**示例**：
```
请使用 skill-creator 来创建一个 skill
```

---

### 3.3 使用建议

> [!warning] 重要提醒
> **不要安装各种各样的 Skills**。应该根据实际需求，先装几个真正能发挥作用的。
> 
> **别人的不一定好，也不一定适合你**。**最重要的还是你自己的任务**。

---

## 第四部分：可视化界面推荐

### 4.1 为什么需要可视化界面？

命令行看不到改了什么文件，可视化界面可以直观看到文件修改。

### 4.2 推荐工具

| 工具 | 链接 | 特点 |
|------|------|------|
| **Trea** | https://www.trae.ai/ | 字节出品，AI 原生编辑器 |
| **Cursor** | https://cursor.sh/ | AI 加持的 VS Code 分支 |
| **VS Code** | https://code.visualstudio.com/ | 微软出品，免费强大 |

### 4.3 如何使用？

1. 下载安装代码编辑器
2. 点击最上方的"终端"（Terminal）
3. 在终端中输入 `claude` 启动
4. 即可可视化看到 AI 具体修改了哪些内容

---

## 第五部分：进阶内容预告

本文只覆盖入门内容，后续文章将分享：

- [ ] 如何自动切换 API
- [ ] 如何使用 Claude 原生 API
- [ ] Skills 的管理技巧
- [ ] Obsidian + Claude Code 工作流

---

## 总结

| 知识点 | 核心内容 |
|--------|----------|
| **Claude Code** | 能干活的 AI 智能体，不只是写代码 |
| **Skills** | 给 AI 的操作 SOP，标准化流程执行任务 |
| **MCP** | AI 的 USB 接口，解决工具调用问题 |
| **安装步骤** | Node.js → Git(Windows) → Claude Code → API Key |
| **Skills 使用** | 安装现成/用 Skill Creator 创建 → 按名称调用 |
| **推荐搭配** | Trea/Cursor/VS Code 等代码编辑器 |

---

## 相关笔记

- [[AI工具对比]]
- [[Claude Code 进阶技巧]]
- [[Obsidian + Claude Code 工作流]]
- [[MCP 服务器推荐]]

---

## 参考资料

- [官方安装文档](https://docs.anthropic.com/en/docs/claude-code)
- [智谱 AI 开放平台](https://open.bigmodel.cn/)
- [GLM Coding Plan 购买页面](https://www.bigmodel.cn/glm-coding?ic=IQKEJG5NOT)
- [智谱 AI Claude 配置文档](https://docs.bigmodel.cn/cn/guide/develop/claude)
- [Anthropic Skills 官方仓库](https://github.com/anthropics/skills)
- [Awesome Claude Skills 合集](https://github.com/ComposioHQ/awesome-claude-skills)
- [Claude 中文社区](https://claudecn.com/)
- [Skills Marketplace](https://skillsmp.com/)

## 实践流程

```mermaid
flowchart LR
  A[安装 Claude Code] --> B[配置模型和 API]
  B --> C[安装或创建 Skill]
  C --> D[在真实任务中调用]
  D --> E[复盘并迭代 Skill]
```

## 实践检查清单

- 安装后是否能在终端和编辑器中稳定启动。
- API Key 是否安全存储，不写入仓库。
- Skill 是否有明确触发场景和输出格式。
- 第一次使用是否从低风险任务开始。
- 是否把常用流程沉淀成项目命令或 Skill。

## 案例

新手可以先创建“项目代码阅读” Skill，让 Claude 按固定步骤输出目录结构、入口文件、运行命令和风险点；确认效果稳定后再扩展到修改代码。

## 常见误区

- 一开始就让 Claude 修改大量文件，没有建立上下文。
- Skill 没有范例，输出每次都不稳定。
- 把 API Key 写进教程笔记或配置仓库。
