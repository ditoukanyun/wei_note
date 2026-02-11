---
title: Python UV包管理工具
description: UV - 下一代高性能Python包管理工具，虚拟环境、依赖管理、项目工作流
date: 2025-02-11
tags:
  - python
  - uv
  - package-manager
  - virtualenv
  - dependencies
  - tools
category: 应用阶段
status: active
aliases:
  - UV
  - 包管理工具
  - Python UV
area: "[[开发工具]]"
parent: "[[00-导航-Python编程导航]]"
up: "[[00-MOC-知识地图]]"
source: https://juejin.cn/post/7444548883646709796
---

> 官方文档: [docs.astral.sh/uv](https://docs.astral.sh/uv/)
> GitHub: [github.com/astral-sh/uv](https://github.com/astral-sh/uv)
> 作者: [Astral](https://astral.sh/) (Ruff 的创造者)

**UV** 是一个由 Astral 公司用 Rust 语言开发的**超高速 Python 包管理工具**，旨在全面替代传统的 `pip`、`venv`、`pip-tools`、`virtualenv` 等工具。UV 的速度比 pip 快 **10-100 倍**，同时提供现代化的项目管理体验。

> [!info] UV 的定位
> UV 不仅仅是一个更快的 pip，而是一个完整的 Python 项目管理解决方案，涵盖了虚拟环境、依赖管理、Python 版本管理、脚本执行等全流程。

## 1. 核心特性

### 1.1 极致性能

- **安装速度**: 比 pip 快 10-100 倍
- **依赖解析**: 使用 Rust 实现的高性能解析器
- **并行下载**: 充分利用网络带宽
- **缓存优化**: 智能缓存机制避免重复下载

### 1.2 全功能覆盖

| 功能 | UV 支持 | 替代工具 |
|------|---------|----------|
| 包安装 | `uv pip install` | pip |
| 虚拟环境 | `uv venv` | venv/virtualenv |
| 依赖锁定 | `uv.lock` | pip-tools |
| 项目管理 | `uv init/add/sync` | poetry/pdm |
| Python 版本 | `uv python` | pyenv |
| 脚本运行 | `uv run` | - |
| 工具执行 | `uvx` | pipx |

### 1.3 兼容性设计

- **100% 兼容 pip**: 支持 `requirements.txt` 和 `pyproject.toml`
- **标准格式**: 使用业界标准的 `pyproject.toml`
- **无缝迁移**: 现有项目无需修改即可使用

## 2. 安装与配置

### 2.1 安装 UV

```bash
# 推荐：使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或从 PyPI 安装
pip install uv

# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2.2 自更新

```bash
# 更新 UV 到最新版本
uv self update
```

### 2.3 配置环境变量（可选）

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export UV_LINK_MODE=copy  # 可选: copy, hardlink, symlink
export UV_CACHE_DIR=~/.cache/uv
```

## 3. 基础命令详解

### 3.1 虚拟环境管理

```bash
# 创建虚拟环境（默认使用系统 Python）
uv venv

# 指定 Python 版本
uv venv --python 3.11
uv venv --python 3.12.1

# 指定目录名
uv venv myenv --python 3.11

# 查看帮助
uv venv --help
```

激活环境（激活方式与传统相同）：

```bash
# macOS/Linux
source .venv/bin/activate

# Windows CMD
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 3.2 包管理（兼容 pip 接口）

```bash
# 安装包
uv pip install flask
uv pip install flask==3.0.0

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 安装开发依赖
uv pip install -r requirements-dev.txt

# 卸载包
uv pip uninstall flask

# 列出已安装包
uv pip list

# 显示包信息
uv pip show flask

# 冻结依赖
uv pip freeze > requirements.txt

# 检查依赖冲突
uv pip check
```

### 3.3 依赖锁定（类似 pip-tools）

```bash
# 编译依赖（生成锁定文件）
uv pip compile pyproject.toml -o requirements.txt
uv pip compile requirements.in -o requirements.txt

# 升级所有包
uv pip compile pyproject.toml --upgrade

# 升级特定包
uv pip compile pyproject.toml --upgrade-package flask
```

## 4. 现代项目工作流（推荐）

### 4.1 初始化新项目

```bash
# 1. 创建项目目录
mkdir my-project && cd my-project

# 2. 初始化项目（生成 pyproject.toml）
uv init

# 3. 创建虚拟环境并指定 Python 版本
uv venv --python 3.11

# 4. 激活环境
source .venv/bin/activate  # macOS/Linux
```

### 4.2 添加依赖

```bash
# 添加生产依赖（自动更新 pyproject.toml）
uv add flask
uv add fastapi uvicorn

# 添加开发依赖
uv add --dev pytest black ruff mypy

# 添加可选依赖组
uv add --group docs mkdocs mkdocs-material

# 指定版本
uv add "flask>=2.0.0,<3.0.0"
uv add requests==2.31.0
```

### 4.3 同步依赖

```bash
# 同步依赖（根据 pyproject.toml 和 uv.lock）
uv sync

# 仅同步生产依赖
uv sync --no-dev

# 同步并更新所有包
uv sync --upgrade

# 更新特定包
uv sync --upgrade-package flask

# 严格模式（确保锁定文件最新）
uv sync --locked
```

> [!tip] 为什么使用 uv.lock？
> `uv.lock` 文件记录了完整的依赖树（包括传递依赖）的确切版本，确保团队成员和 CI/CD 环境使用完全相同的依赖版本，实现可重现的构建。

### 4.4 运行项目

```bash
# 运行 Python 脚本（自动使用项目环境）
uv run python main.py

# 运行模块
uv run python -m pytest

# 运行命令（无需手动激活环境）
uv run flask run
uv run pytest

# 运行单文件脚本（带依赖声明）
uv run --with requests script.py
```

### 4.5 pyproject.toml 配置示例

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "项目描述"
readme = "README.md"
requires-python = ">=3.11"
authors = [
    { name = "Your Name", email = "you@example.com" }
]
keywords = ["web", "api"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.11",
]

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
]

[project.scripts]
my-cli = "my_project.cli:main"

[tool.uv]
# UV 特定配置
python-preference = "only-managed"  # 仅使用 UV 管理的 Python 版本

[tool.uv.pip]
generate-hashes = true  # 生成哈希值增强安全性

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]
```

## 5. Python 版本管理

### 5.1 安装 Python 版本

```bash
# 列出可安装的 Python 版本
uv python list

# 安装特定版本
uv python install 3.11
uv python install 3.12.1
uv python install 3.10 3.11 3.12  # 安装多个版本

# 查看已安装版本
uv python list --installed
```

### 5.2 项目指定 Python 版本

```bash
# 创建项目时指定
uv init --python 3.11

# 修改已有项目
uv python pin 3.11  # 创建 .python-version 文件
```

### 5.3 使用 .python-version 文件

```bash
# 创建版本文件
echo "3.11.7" > .python-version

# 此后 uv venv 会自动使用该版本
uv venv  # 使用 3.11.7
```

## 6. 脚本支持（革命性功能）

### 6.1 单文件脚本管理

UV 可以在 Python 脚本中直接声明依赖，无需创建完整的项目：

```python
# hello.py
# /// script
# dependencies = [
#     "requests>=2.31.0",
#     "rich>=13.0.0",
# ]
# ///

import requests
from rich import print

response = requests.get("https://api.github.com")
print(f"Status: {response.status_code}")
print(response.json())
```

运行脚本：

```bash
# UV 会自动安装声明的依赖并运行
uv run hello.py
```

### 6.2 包含元数据的脚本

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "flask",
# ]
# [tool.uv]
# exclude-newer = "2024-01-01T00:00:00Z"
# ///
```

## 7. 工具管理（uvx / uv tool）

### 7.1 临时运行工具

```bash
# 无需安装，直接运行工具
uvx ruff check .
uvx black main.py
uvx mypy src/
uvx cookiecutter gh:audreyfeldroy/cookiecutter-pypackage

# 指定版本
uvx ruff@0.1.0 check .

# 传递参数
uvx --python 3.11 pytest --version
```

### 7.2 安装工具

```bash
# 安装工具（全局可用）
uv tool install black
uv tool install ruff
uv tool install pytest

# 安装多个工具
uv tool install black ruff mypy

# 查看已安装工具
uv tool list

# 升级工具
uv tool upgrade ruff

# 卸载工具
uv tool uninstall ruff
```

### 7.3 工具目录

```bash
# 查看工具安装目录
uv tool dir

# 查看工具二进制文件目录
uv tool dir --bin
```

## 8. UV vs 传统工具命令对比

### 8.1 包安装

| 操作 | UV 命令 | pip 命令 |
|------|---------|----------|
| 安装包 | `uv pip install flask` | `pip install flask` |
| 安装指定版本 | `uv pip install flask==2.3.0` | `pip install flask==2.3.0` |
| 从文件安装 | `uv pip install -r requirements.txt` | `pip install -r requirements.txt` |
| 可编辑安装 | `uv pip install -e .` | `pip install -e .` |
| 卸载包 | `uv pip uninstall flask` | `pip uninstall flask` |
| 列出包 | `uv pip list` | `pip list` |
| 导出依赖 | `uv pip freeze` | `pip freeze` |

### 8.2 项目管理（UV 特有）

| 操作 | UV 命令 | Poetry 等效命令 |
|------|---------|-----------------|
| 初始化项目 | `uv init` | `poetry init` |
| 添加依赖 | `uv add flask` | `poetry add flask` |
| 添加开发依赖 | `uv add --dev pytest` | `poetry add --group dev pytest` |
| 同步依赖 | `uv sync` | `poetry install` |
| 更新依赖 | `uv sync --upgrade` | `poetry update` |
| 运行命令 | `uv run python main.py` | `poetry run python main.py` |
| 构建项目 | `uv build` | `poetry build` |
| 发布项目 | `uv publish` | `poetry publish` |

### 8.3 虚拟环境

| 操作 | UV 命令 | 传统命令 |
|------|---------|----------|
| 创建环境 | `uv venv` | `python -m venv .venv` |
| 指定 Python | `uv venv --python 3.11` | - |
| 激活环境 | `source .venv/bin/activate` | `source .venv/bin/activate` |

## 9. 团队协作最佳实践

### 9.1 项目结构

```
my-project/
├── .python-version          # 指定 Python 版本
├── pyproject.toml           # 项目配置和依赖
├── uv.lock                  # 锁定文件（必须提交）
├── README.md
├── .gitignore
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── main.py
└── tests/
    └── test_main.py
```

### 9.2 .gitignore 配置

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境（可选，可以提交 .venv 到版本控制）
.venv/
venv/
ENV/
env/

# UV（不需要忽略 uv.lock，应该提交）

# IDE
.idea/
.vscode/
*.swp
*.swo
```

### 9.3 新成员加入流程

```bash
# 1. 克隆项目
git clone https://github.com/org/my-project.git
cd my-project

# 2. 创建虚拟环境（会自动使用 .python-version 指定的版本）
uv venv

# 3. 激活环境
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

# 4. 同步依赖（根据 uv.lock 安装精确版本）
uv sync

# 5. 运行项目
uv run python main.py
```

### 9.4 CI/CD 集成

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install UV
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
      
      - name: Set up Python
        run: uv python install
      
      - name: Create virtual environment
        run: uv venv
      
      - name: Install dependencies
        run: uv sync --locked
      
      - name: Run tests
        run: uv run pytest
      
      - name: Run linting
        run: uv run ruff check .
```

## 10. 迁移指南

### 10.1 从 pip + requirements.txt 迁移

```bash
# 1. 初始化 UV 项目
uv init

# 2. 导入现有依赖
uv add -r requirements.txt

# 如果 requirements.txt 有分类
uv add -r requirements.txt
uv add --dev -r requirements-dev.txt

# 3. 同步并生成 uv.lock
uv sync
```

### 10.2 从 Poetry 迁移

```bash
# 1. 导出 Poetry 依赖
poetry export -f requirements.txt --without-hashes > requirements.txt
poetry export -f requirements.txt --without-hashes --with dev > requirements-dev.txt

# 2. 初始化 UV 项目
uv init

# 3. 导入依赖
uv add -r requirements.txt
uv add --dev -r requirements-dev.txt

# 4. 复制其他配置（scripts, entry points 等）
# 手动编辑 pyproject.toml
```

### 10.3 从 pip-tools 迁移

```bash
# UV 直接兼容 requirements.in 格式
# 只需替换命令：
# pip-compile -> uv pip compile
# pip-sync -> uv sync
```

## 11. 高级技巧

### 11.1 离线模式

```bash
# 仅使用缓存，不访问网络
uv pip install --offline flask
uv sync --offline
```

### 11.2 约束文件

```bash
# 使用约束文件限制依赖版本
uv pip install -c constraints.txt flask
```

### 11.3 配置镜像源

```bash
# 使用国内镜像加速
uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple flask

# 或通过环境变量
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

### 11.4 查看依赖树

```bash
# 显示依赖树
uv pip tree

# 显示反向依赖（谁依赖了这个包）
uv pip tree --reverse
```

### 11.5 清理缓存

```bash
# 查看缓存大小
uv cache dir

# 清理缓存
uv cache clean

# 清理特定包的缓存
uv cache clean flask
```

## 12. 常见问题

### Q: UV 和 Poetry 有什么区别？

**A:** UV 更快（Rust 编写），同时兼容 pip 接口，学习成本更低。Poetry 功能更丰富但速度较慢。UV 更适合追求性能和简洁的开发者。

### Q: 是否应该提交 uv.lock 到版本控制？

**A:** **是的**，uv.lock 确保了依赖版本的一致性，类似于 Cargo.lock 或 package-lock.json，必须提交到版本控制。

### Q: UV 支持私有 PyPI 仓库吗？

**A:** 支持，可以使用 `--index-url` 或配置 `UV_INDEX_URL` 环境变量。

### Q: 可以部分迁移吗？

**A:** 可以，UV 完全兼容 pip 接口，你可以先用 `uv pip install` 替代 pip，逐步采用其他功能。

### Q: UV 支持 Conda 吗？

**A:** UV 专注于 PyPI 生态，不直接支持 Conda。如果需要 Conda 的包管理，仍需使用 conda/mamba。

## 结论

UV 通过 Rust 的高性能实现和现代化的工具设计，彻底改变了 Python 包管理的体验。它不仅带来了数量级的性能提升，还统一了 Python 项目管理的整个工作流。

**推荐使用场景：**

- ✨ **新项目**: 直接使用 UV 作为项目基础工具
- 🚀 **现有项目**: 逐步迁移，先替换 pip 命令
- 👥 **团队协作**: 统一的工具链减少环境配置问题
- ⚡ **CI/CD**: 极快的安装速度显著缩短构建时间

随着 UV 生态的不断完善，它正在成为 Python 包管理的事实标准，值得每一位 Python 开发者学习和使用。

---

> [!tip] 学习资源
> - [UV 官方文档](https://docs.astral.sh/uv/)
> - [UV GitHub 仓库](https://github.com/astral-sh/uv)
> - [Astral 博客](https://astral.sh/blog)
> - [迁移指南](https://docs.astral.sh/uv/guides/migration/)

#工具 #Python #UV #开发效率 #包管理