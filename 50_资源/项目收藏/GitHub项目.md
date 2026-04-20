# GitHub 项目收藏

## GitNexus - 代码知识图谱引擎

- **链接**: https://github.com/abhigyanpatwari/GitNexus
- **标签**: #代码分析 #AI工具 #MCP #知识图谱

### 简介
GitNexus 是一个**零服务器的代码智能引擎**，将任何代码库索引成知识图谱（依赖关系、调用链、执行流），然后通过 MCP 工具暴露给 AI 代理使用。

### 核心功能

| 功能 | 说明 |
|------|------|
| **代码索引** | 使用 Tree-sitter 解析 AST，提取函数、类、方法、接口 |
| **知识图谱** | 构建完整的代码关系图（调用、继承、导入） |
| **智能搜索** | BM25 + 语义搜索 + RRF 混合检索 |
| **影响分析** | 修改代码前分析影响范围（blast radius） |
| **MCP 集成** | 为 Cursor、Claude Code、Codex 等提供深度代码感知 |

### 使用方式

#### CLI 安装
```bash
npm install -g gitnexus
```

#### 基本命令
```bash
# 配置 MCP（一次性）
gitnexus setup

# 索引代码库
gitnexus analyze

# 启动 MCP 服务器
gitnexus mcp

# 生成 Wiki 文档
gitnexus wiki

# 查看索引状态
gitnexus status

# 清理索引
gitnexus clean
```

#### 多仓库组管理
```bash
# 创建仓库组
gitnexus group create <name>

# 添加仓库到组
gitnexus group add <name> <repo>

# 跨仓库搜索执行流
gitnexus group query <name> <query>
```

### MCP 工具（16个）

| 工具 | 功能 |
|------|------|
| `list_repos` | 列出所有索引的仓库 |
| `query` | 混合搜索（BM25 + 语义） |
| `context` | 360度符号视图 |
| `impact` | 影响范围分析 |
| `detect_changes` | Git diff 影响映射 |
| `rename` | 多文件协调重命名 |
| `cypher` | 原始 Cypher 图查询 |
| `group_*` | 多仓库组管理工具 |

### 支持语言

TypeScript、JavaScript、Python、Java、Kotlin、C#、Go、Rust、PHP、Ruby、Swift、C、C++、Dart

### 与 DeepWiki 的区别

- **DeepWiki**: 帮助理解代码（描述性）
- **GitNexus**: 让 AI 分析代码（关系型知识图谱，追踪每个依赖关系）

### Web UI

在线体验：https://gitnexus.vercel.app
- 完全客户端运行，代码不上传服务器
- 拖放 ZIP 即可开始探索
- 支持本地后端模式（`gitnexus serve`）

### 企业版功能

- PR 自动影响分析
- 自动更新代码 Wiki
- 自动重新索引
- 多仓库统一图谱
- OCaml 支持

## OpenCLI - 万能 CLI 工具

- **链接**: https://github.com/jackwener/opencli
- **标签**: #CLI #浏览器自动化 #AI工具 #爬虫

### 简介
OpenCLI 是一个**万能 CLI 工具**，可以将任何网站、Electron 应用或本地工具转换成命令行接口。支持 79+ 网站，包括 Bilibili、知乎、小红书、Twitter、Reddit 等。

### 核心特性

| 特性 | 说明 |
|------|------|
| **网站 → CLI** | 将任何网站变成确定性 CLI，支持 70+ 预构建适配器 |
| **浏览器复用** | 复用 Chrome/Chromium 登录状态，账号安全 |
| **反检测** | 内置反指纹、反风控措施 |
| **AI Agent 支持** | AI 可直接控制浏览器，点击、输入、截图 |
| **Electron 应用** | 控制 Cursor、ChatGPT、Notion 等桌面应用 |
| **外部 CLI 集成** | 自动发现和调用 gh、docker、obsidian 等工具 |

### 安装

```bash
# npm 安装
npm install -g @jackwener/opencli

# 安装浏览器扩展（Chrome）
# 1. 下载 releases 中的 opencli-extension.zip
# 2. chrome://extensions 开启开发者模式
# 3. 加载解压的扩展

# 检查状态
opencli doctor
```

### 常用命令

```bash
# 查看所有命令
opencli list

# 热门网站示例
opencli bilibili hot --limit 5          # B站热门
opencli hackernews top --limit 5        # HackerNews
opencli xiaohongshu search "AI"         # 小红书搜索
opencli twitter trending                # Twitter 趋势

# 浏览器操作（AI Agent 模式）
opencli operate open https://example.com
opencli operate click "登录按钮"
opencli operate type "搜索框" "关键词"
opencli operate screenshot

# 下载内容
opencli xiaohongshu download <note_id> --output ./xhs
opencli bilibili download <bv_id> --output ./bilibili

# 控制 Electron 应用
opencli cursor composer "写一个 Python 脚本"
opencli notion search "AI"

# 外部 CLI 透传
opencli gh pr list --limit 5
opencli docker ps
opencli obsidian search "笔记"
```

### 输出格式

```bash
opencli bilibili hot -f json    # JSON 格式
opencli bilibili hot -f csv     # CSV 格式
opencli bilibili hot -f md      # Markdown
opencli bilibili hot -v         # 详细模式
```

### 自定义适配器

```bash
# 探索网站 API
opencli explore https://example.com --site mysite

# 生成适配器
opencli synthesize mysite

# 一键生成
opencli generate https://example.com --goal "hot"

# 注册本地 CLI
opencli register mycli
```

### 支持的平台

**国内**: Bilibili、知乎、小红书、贴吧、虎扑、闲鱼、1688、元宝、小鹅通
**国际**: Twitter/X、Reddit、YouTube、Amazon、Spotify、HackerNews
**AI 工具**: Gemini、NotebookLM、ChatGPT、Cursor、Codex
**桌面应用**: Cursor、Notion、Discord、豆包

### AI Agent 集成

```bash
# 安装技能（Claude Code / Cursor）
npx skills add jackwener/opencli

# 可用技能
npx skills add jackwener/opencli --skill opencli-operate    # 浏览器自动化
npx skills add jackwener/opencli --skill opencli-explorer   # 适配器开发
npx skills add jackwener/opencli --skill opencli-oneshot    # 快速命令
```

### 插件系统

```bash
# 安装社区插件
opencli plugin install github:user/opencli-plugin-juejin
opencli plugin list
opencli plugin update --all
```

### 退出码

| 码 | 含义 |
|---|------|
| 0 | 成功 |
| 66 | 空结果 |
| 69 | 服务不可用（扩展未连接） |
| 77 | 需要登录 |
| 78 | 配置错误 |

## Harness Engineering - 驭缰工程学习指南

- **链接**: https://github.com/deusyu/harness-engineering
- **标签**: #AI工程 #智能体 #OpenAI #学习资源

### 简介
OpenAI 在 2026 年 2 月提出的工程范式学习档案。**Harness Engineering（驭缰工程）**：工程师不再写代码，而是设计环境、明确意图、构建反馈回路，让 AI 智能体可靠地完成工作。

> 人类掌舵，智能体执行。

### 核心理念

| 传统工程 | Harness Engineering |
|---------|---------------------|
| 人类写代码 → 机器执行 | 人类设计约束 → 智能体写代码 → 机器执行 |

### 六大核心概念

| 概念 | 说明 |
|------|------|
| **仓库即记录系统** | 不在仓库里的东西对智能体不存在，一切决策必须版本化 |
| **地图而非手册** | AGENTS.md 是 ~100 行的入口文件，渐进式披露，指向深层文档 |
| **机械化执行** | 自定义 linter + 结构测试 = 不变量的守护者，智能体可自我纠正 |
| **智能体可读性** | 优先为智能体的推理能力优化，选"无聊"技术 |
| **吞吐量改变合并理念** | 纠错成本低，等待成本高，PR 生命周期很短 |
| **熵管理 = 垃圾回收** | 将"黄金规则"编码进仓库，定期扫描偏差、发起重构 |

### 仓库结构

```
harness-engineering/
├── AGENTS.md           # 仓库导航入口（给智能体看的）
├── concepts/           # Phase 1：概念笔记
├── thinking/           # Phase 2：独立思考与质疑
├── practice/           # Phase 3：小项目实验
├── feedback/           # Phase 4：踩坑与迭代心得
├── works/              # Phase 5：可展示的作品
├── prompts/            # 验证有效的提示词
└── references/         # 外部资源索引
```

### 实践数据（OpenAI 团队）

| 指标 | 数据 |
|------|------|
| 团队规模 | 3 人 → 7 人 |
| 时间跨度 | 5 个月 |
| 代码量 | ~100 万行 |
| PR 数量 | ~1,500 个 |
| 人均日 PR | 3.5 个 |
| 单次运行时长 | 6+ 小时 |
| 效率 | 手工编写的 ~1/10 时间 |

### 相关项目

| 项目 | Stars | 说明 |
|------|-------|------|
| snarktank/ralph | 13.6k | 原版 Ralph：bash 脚本反复启动 AI |
| ralph-orchestrator | 2.3k | Rust 进化版：Hat 角色系统 + 多后端 |
| bmad-ralph | 2 | BMAD 方法论 + Ralph：三层自愈 |

### Ralph 信条与 Harness 对应

| Ralph 信条 | Harness 概念 |
|-----------|-------------|
| Fresh Context Is Reliability | 智能体可读性 |
| Backpressure Over Prescription | 机械化执行 |
| The Plan Is Disposable | 熵管理 |
| Disk Is State, Git Is Memory | 仓库即记录系统 |
| Steer With Signals, Not Scripts | 人类掌舵 |
| Let Ralph Ralph | 智能体执行 |

### 学习路径

1. **Phase 1**: 阅读 `concepts/`，理解六大核心概念
2. **Phase 2**: 在 `thinking/` 中写下质疑和延伸思考
3. **Phase 3**: 在 `practice/` 中用 AI 智能体从零构建小项目
4. **Phase 4**: 在 `feedback/` 中记录踩坑和修正
5. **Phase 5**: 在 `works/` 中提炼成文章或工具

### 相关资源

- [OpenAI 原文](https://openai.com/index/harness-engineering/) - Harness Engineering 完整阐述
- [Harness design for long-running apps](https://www.anthropic.com/research/harness-design) - Anthropic Labs 实战
- [为什么 AI 写代码更快但交付没变](https://www.seangoedecke.com/ai-coding/) - 约束理论拆解效率悖论

---

*记录时间: 2026-04-07*

## Khazix Skills - Agent Skills 与 Prompt 工具箱

- **链接**: https://github.com/KKKKhazix/khazix-skills
- **标签**: #AI工具 #AgentSkills #Prompt #研究工作流 #写作工作流

### 简介
卡兹克开源的个人 AI 方法论仓库，分为两部分：
- **Prompts**：可直接复制到 AI 对话中使用
- **Skills**：符合 Agent Skills 标准的结构化技能，可安装到 Claude Code、Codex、OpenClaw 等工具

### 核心内容

| 模块 | 说明 |
|------|------|
| **横纵分析法（Prompt）** | 纵向时间线 + 横向竞争格局分析，适合深度研究 |
| **hv-analysis（Skill）** | 自动联网收集信息并生成结构化研究输出 |
| **khazix-writer（Skill）** | 面向公众号长文写作，包含风格规则与自检机制 |

### 安装方式

#### Agent 对话安装

```text
安装这个 skill：https://github.com/KKKKhazix/khazix-skills
```

#### 手动安装

- 在 Releases 下载 `.skill` 文件
- 放入对应目录：
  - Claude Code: `~/.claude/skills/`
  - OpenClaw: `~/.openclaw/skills/`
  - Codex: `~/.agents/skills/`

### 个人备注

挺好用，尤其适合把“研究 + 写作”沉淀成可复用流程。

### 相关笔记

- [[Khazix Skills]]

---

*记录时间: 2026-04-15*
