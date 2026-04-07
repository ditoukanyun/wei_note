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

---

*记录时间: 2026-04-07*
