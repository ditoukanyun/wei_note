---
type: resource
tags:
  - AI工具
  - 沙箱
  - 容器
  - 安全
  - 阿里巴巴
  - CNCF
source: "[[GitHub - OpenSandbox]]"
url: https://github.com/alibaba/OpenSandbox
---

# OpenSandbox

## 一句话总结

**OpenSandbox** 是阿里巴巴开源的通用 AI 沙箱平台，为 Coding Agents、GUI Agents、AI 代码执行、Agent 评估和强化学习训练等场景提供多语言 SDK、统一沙箱 API 和 Docker/Kubernetes 运行时支持。

---

## 有什么用

### 核心场景

| 场景 | 说明 |
|------|------|
| **Coding Agents** | 安全运行 Claude Code、Gemini CLI、Codex CLI 等 AI 编程助手 |
| **GUI Agents** | 浏览器自动化（Chrome、Playwright）、桌面环境（VNC） |
| **Agent Evaluation** | 评估 AI Agent 的安全性和能力 |
| **AI Code Execution** | 安全执行 AI 生成的代码 |
| **RL Training** | 强化学习训练环境 |

### 核心功能

- **多语言 SDK**：Python、Java/Kotlin、JavaScript/TypeScript、C#/.NET、Go（路线图）
- **沙箱协议**：定义沙箱生命周期管理 API 和执行 API，可扩展自定义运行时
- **沙箱运行时**：内置 Docker 和 Kubernetes 运行时，支持本地运行和大规模分布式调度
- **沙箱环境**：内置命令执行、文件系统、代码解释器实现
- **网络策略**：统一 Ingress Gateway + 每沙箱 egress 控制
- **强隔离**：支持 gVisor、Kata Containers、Firecracker microVM 等安全容器运行时

---

## 怎么用上

### 快速开始（Docker）

#### 1. 安装沙箱服务器

```bash
uv pip install opensandbox-server
opensandbox-server init-config ~/.sandbox.toml --example docker
```

#### 2. 启动沙箱服务器

```bash
opensandbox-server
```

#### 3. 安装 Code Interpreter SDK 并执行代码

```bash
uv pip install opensandbox-code-interpreter
```

```python
import asyncio
from datetime import timedelta
from code_interpreter import CodeInterpreter, SupportedLanguage
from opensandbox import Sandbox
from opensandbox.models import WriteEntry

async def main() -> None:
    # 1. 创建沙箱
    sandbox = await Sandbox.create(
        "opensandbox/code-interpreter:v1.0.2",
        entrypoint=["/opt/opensandbox/code-interpreter.sh"],
        env={"PYTHON_VERSION": "3.11"},
        timeout=timedelta(minutes=10),
    )

    async with sandbox:
        # 2. 执行 shell 命令
        execution = await sandbox.commands.run("echo 'Hello OpenSandbox!'")
        print(execution.logs.stdout[0].text)

        # 3. 写入文件
        await sandbox.files.write_files([
            WriteEntry(path="/tmp/hello.txt", data="Hello World", mode=644)
        ])

        # 4. 读取文件
        content = await sandbox.files.read_file("/tmp/hello.txt")
        print(f"Content: {content}")

        # 5. 创建代码解释器
        interpreter = await CodeInterpreter.create(sandbox)

        # 6. 执行 Python 代码
        result = await interpreter.codes.run("""
            import sys
            print(sys.version)
            result = 2 + 2
            result
        """, language=SupportedLanguage.PYTHON)

        print(result.result[0].text)  # 4
        print(result.logs.stdout[0].text)  # 3.11.14

    # 7. 清理沙箱
    await sandbox.kill()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 集成示例

### 基础示例

- **[code-interpreter](examples/code-interpreter/)** - 端到端代码解释器 SDK 工作流
- **[aio-sandbox](examples/aio-sandbox/)** - 使用 OpenSandbox SDK 的一体化沙箱设置
- **[agent-sandbox](examples/agent-sandbox/)** - Kubernetes 上的 Agent 沙箱工作负载

### Coding Agent 集成

| Agent | 示例 |
|-------|------|
| Claude Code | [claude-code](examples/claude-code/) |
| Gemini CLI | [gemini-cli](examples/gemini-cli/) |
| OpenAI Codex CLI | [codex-cli](examples/codex-cli/) |
| Qwen Code | [qwen-code](examples/qwen-code/) |
| Kimi CLI | [kimi-cli](examples/kimi-cli/) |

### 浏览器和桌面环境

- **[chrome](examples/chrome/)** - Chromium 沙箱，支持 VNC 和 DevTools
- **[playwright](examples/playwright/)** - Playwright + Chromium 无头爬取和测试
- **[desktop](examples/desktop/)** - 完整桌面环境，支持 VNC 访问
- **[vscode](examples/vscode/)** - 沙箱内运行的 code-server（VS Code Web）

### ML 和训练

- **[rl-training](examples/rl-training/)** - DQN CartPole 训练，支持检查点和摘要输出

---

## 项目结构

```
OpenSandbox/
├── sdks/                    # 多语言 SDK
│   ├── sandbox/python/      # Python 沙箱 SDK
│   ├── code-interpreter/python/  # Python 代码解释器 SDK
│   ├── sandbox/kotlin/      # Java/Kotlin SDK
│   ├── sandbox/javascript/  # JavaScript/TypeScript SDK
│   └── sandbox/csharp/      # C#/.NET SDK
├── specs/                   # OpenAPI 规范和生命周期规范
├── server/                  # Python FastAPI 沙箱生命周期服务器
├── kubernetes/              # Kubernetes 部署和示例
├── components/
│   ├── execd/              # 沙箱执行守护进程（命令和文件操作）
│   ├── ingress/            # 沙箱流量入口代理
│   └── egress/             # 沙箱网络出口控制
├── sandboxes/              # 运行时沙箱实现
└── examples/               # 集成示例和用例
```

---

## 安全隔离

支持以下安全容器运行时：

- **gVisor** - Google 的用户空间内核
- **Kata Containers** - 轻量级虚拟机
- **Firecracker microVM** - AWS 的无服务器虚拟化

详见：[Secure Container Runtime Guide](docs/secure-container.md)

---

## 关键链接

- **官网文档**：https://open-sandbox.ai/
- **中文文档**：https://open-sandbox.ai/zh/
- **GitHub**：https://github.com/alibaba/OpenSandbox
- **PyPI**：https://pypi.org/project/opensandbox/
- **npm**：https://www.npmjs.com/package/@alibaba-group/opensandbox
- **CNCF Landscape**：https://landscape.cncf.io/?item=orchestration-management--scheduling-orchestration--opensandbox

---

## 与同类工具对比

| 特性 | OpenSandbox | E2B | Modal |
|------|-------------|-----|-------|
| 开源 | ✅ 完全开源 | ✅ 开源 | ❌ 闭源 |
| Kubernetes 支持 | ✅ 原生支持 | ⚠️ 有限 | ⚠️ 有限 |
| 多语言 SDK | ✅ Python/Java/TS/C# | ✅ 多语言 | ✅ 多语言 |
| 安全容器 | ✅ gVisor/Kata/Firecracker | ✅ Firecracker | ❓ |
| 网络策略 | ✅ Ingress + Egress | ⚠️ 基础 | ⚠️ 基础 |
| 中国可用性 | ✅ 阿里云原生 | ⚠️ 需代理 | ⚠️ 需代理 |

---

## 适用场景总结

1. **AI 应用开发者**：需要安全执行 AI 生成代码的沙箱环境
2. **AI Agent 团队**：需要评估和隔离 Agent 行为的平台
3. **企业用户**：需要符合安全合规要求的容器隔离方案
4. **强化学习研究者**：需要大规模分布式训练环境
5. **中国开发者**：需要国内可用的沙箱解决方案
