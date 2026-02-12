---
type: wiki
created: 2026-02-12
area: "[[AI_ML]]"
tags: [langchain, middleware, python, hooks, decorator]
---

# LangChain Middleware 中间件系统

## 概述

Middleware（中间件）是 LangChain 1.0+ 引入的强大扩展机制，允许在 Agent 执行流程的不同阶段插入自定义逻辑，而无需修改核心代码。

**Python 关联**：基于 Python 装饰器模式实现，类似 Flask/Django 中间件、FastAPI 依赖注入。

---

## 为什么需要 Middleware

### 传统方式的痛点

```python
# 旧方式：逻辑分散在各处
def agent_step():
    # 1. 手动记录日志
    log_start()
    
    # 2. 手动修剪消息
    if len(messages) > 20:
        messages = messages[-20:]
    
    # 3. 调用模型
    response = model.invoke(messages)
    
    # 4. 手动安全检查
    if not is_safe(response):
        response = "[Filtered]"
    
    # 5. 手动记录结束
    log_end()
```

### Middleware 解决方案

```python
# 新方式：关注点分离
agent = create_agent(
    model=model,
    tools=tools,
    middleware=[
        LoggingMiddleware(),      # 日志
        TrimmingMiddleware(),     # 消息修剪
        SafetyMiddleware(),       # 安全检查
    ]
)
```

---

## 四种核心钩子

### 1. @before_model - 模型调用前

在调用 LLM 之前处理状态，适合：消息修剪、上下文注入、预处理

```python
from langchain.agents.middleware import before_model

@before_model
def trim_messages(state: AgentState, runtime) -> dict:
    """修剪过长的对话历史"""
    messages = state["messages"]
    
    if len(messages) > 20:
        # 保留系统消息和最近的消息
        system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
        recent_msgs = messages[-19:]
        messages = system_msgs + recent_msgs
    
    return {"messages": messages}

@before_model
def inject_context(state: AgentState, runtime) -> dict:
    """注入用户上下文"""
    user_id = runtime.context.user_id
    user_prefs = runtime.store.get(("prefs",), user_id)
    
    # 在消息前添加上下文
    context_msg = SystemMessage(f"用户偏好: {user_prefs}")
    messages = [context_msg] + state["messages"]
    
    return {"messages": messages}
```

**执行时机**：
```
用户输入 → [before_model] → LLM调用
                ↓
           状态预处理
```

### 2. @after_model - 模型响应后

处理模型输出，适合：内容审查、后处理、格式化

```python
from langchain.agents.middleware import after_model

@after_model(can_jump_to=["tools", "end"])
def content_safety_check(state: AgentState, runtime) -> dict | None:
    """内容安全检查"""
    last_message = state["messages"][-1]
    
    if contains_sensitive_info(last_message.content):
        # 过滤敏感内容
        last_message.content = "[内容已过滤]"
        return {"messages": state["messages"]}
    
    # 返回 None 继续正常流程
    return None

@after_model
def format_output(state: AgentState, runtime) -> dict:
    """格式化输出"""
    last_message = state["messages"][-1]
    
    # 添加 Markdown 格式化
    if not last_message.content.startswith("```"):
        last_message.content = f"```\n{last_message.content}\n```"
    
    return {"messages": state["messages"]}
```

**跳转控制**：
- `can_jump_to=["tools", "end"]`：可以跳转到工具节点或结束
- 返回 `dict`：更新状态并继续
- 返回 `None`：继续正常流程

### 3. @wrap_model_call - 包装模型调用

包装整个模型调用过程，适合：日志、监控、动态模型选择

```python
from langchain.agents.middleware import wrap_model_call
import time

@wrap_model_call
def logging_middleware(request: ModelRequest, handler):
    """记录模型调用日志"""
    model_name = request.model.__class__.__name__
    message_count = len(request.state["messages"])
    
    print(f"[{time.strftime('%H:%M:%S')}] 调用 {model_name}")
    print(f"  - 消息数: {message_count}")
    
    start = time.time()
    try:
        response = handler(request)
        elapsed = time.time() - start
        print(f"  - 成功 ({elapsed:.2f}s)")
        return response
    except Exception as e:
        elapsed = time.time() - start
        print(f"  - 失败 ({elapsed:.2f}s): {e}")
        raise

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler):
    """基于复杂度动态选择模型"""
    message_count = len(request.state["messages"])
    
    # 简单查询使用轻量级模型
    if message_count < 5:
        model = ChatOpenAI(model="gpt-4.1-mini")
    else:
        model = ChatOpenAI(model="gpt-4.1")
    
    # 覆盖模型
    new_request = request.override(model=model)
    return handler(new_request)
```

### 4. @wrap_tool_call - 包装工具调用

包装工具执行过程，适合：重试、错误处理、权限检查

```python
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage

@wrap_tool_call
def retry_middleware(request: ToolCallRequest, handler):
    """工具重试机制"""
    max_retries = 3
    tool_name = request.tool_call["name"]
    
    for attempt in range(max_retries):
        try:
            return handler(request)
        except Exception as e:
            if attempt == max_retries - 1:
                # 最后一次失败，返回错误消息
                return ToolMessage(
                    content=f"工具 {tool_name} 执行失败: {str(e)}",
                    tool_call_id=request.tool_call["id"]
                )
            
            # 指数退避
            wait = 2 ** attempt
            print(f"重试 {tool_name} ({attempt + 1}/{max_retries})，等待 {wait}s")
            time.sleep(wait)

@wrap_tool_call
def permission_check(request: ToolCallRequest, handler):
    """权限检查"""
    tool_name = request.tool_call["name"]
    user_role = request.runtime.context.user_role
    
    # 敏感工具需要管理员权限
    if tool_name.startswith("admin_") and user_role != "admin":
        return ToolMessage(
            content=f"权限不足: {tool_name} 需要管理员权限",
            tool_call_id=request.tool_call["id"]
        )
    
    return handler(request)
```

---

## 执行顺序图解

```
用户输入
    ↓
[before_model] ────────→ 状态预处理（修剪、注入）
    ↓
[wrap_model_call] ─────→ 开始计时/日志
    ↓
    LLM 调用
    ↓
[wrap_model_call] ─────→ 结束计时/日志
    ↓
[after_model] ─────────→ 后处理（审查、格式化）
    ↓
需要工具？
    ↓ 是
[wrap_tool_call] ──────→ 重试/权限检查
    ↓
    工具执行
    ↓
观察结果 ──────────────→ 回到 [before_model]
    ↓ 否
最终输出
```

---

## 高级用法

### 类形式中间件

```python
from langchain.agents.middleware import AgentMiddleware

class AnalyticsMiddleware(AgentMiddleware):
    """分析中间件"""
    
    def __init__(self):
        self.call_count = 0
        self.total_latency = 0
    
    def before_model(self, state, runtime):
        """记录开始时间"""
        state["start_time"] = time.time()
        return None
    
    def after_model(self, state, runtime):
        """计算延迟"""
        if "start_time" in state:
            latency = time.time() - state["start_time"]
            self.call_count += 1
            self.total_latency += latency
            
            print(f"平均延迟: {self.total_latency / self.call_count:.2f}s")
        
        return None
```

### 动态工具过滤

```python
@wrap_model_call
def filter_tools_by_permission(request: ModelRequest, handler):
    """根据权限过滤工具"""
    user_role = request.runtime.context.user_role
    
    permission_map = {
        "admin": lambda t: True,
        "editor": lambda t: not t.name.startswith("delete_"),
        "viewer": lambda t: t.name.startswith("read_")
    }
    
    filter_fn = permission_map.get(user_role, permission_map["viewer"])
    filtered_tools = [t for t in request.tools if filter_fn(t)]
    
    return handler(request.override(tools=filtered_tools))
```

### 组合多个中间件

```python
agent = create_agent(
    model=model,
    tools=tools,
    middleware=[
        # 按顺序执行
        LoggingMiddleware(),           # 1. 记录开始
        PermissionMiddleware(),        # 2. 权限检查
        TrimmingMiddleware(max=20),    # 3. 修剪消息
        RetryMiddleware(max=3),        # 4. 工具重试
        AnalyticsMiddleware(),         # 5. 性能分析
    ]
)
```

---

## 最佳实践

### 1. 保持中间件单一职责

```python
# 好的做法：每个中间件只做一件事
@before_model
def trim_messages(state, runtime):
    """只负责修剪消息"""
    pass

@before_model
def inject_context(state, runtime):
    """只负责注入上下文"""
    pass

# 避免：一个中间件做太多事
@before_model
def do_everything(state, runtime):
    """修剪、注入、格式化..."""
    pass
```

### 2. 错误处理策略

```python
@wrap_tool_call
def robust_tool_wrapper(request, handler):
    try:
        return handler(request)
    except NetworkError:
        # 网络错误：重试
        return retry_handler(request)
    except ValidationError as e:
        # 验证错误：返回友好提示
        return ToolMessage(
            content=f"输入无效: {e.message}",
            tool_call_id=request.tool_call["id"]
        )
    except Exception as e:
        # 未知错误：记录并抛出
        logger.error(f"Tool error: {e}")
        raise
```

### 3. 状态更新注意事项

```python
@before_model
def update_state(state, runtime):
    """正确更新状态"""
    # 返回需要更新的字段
    return {
        "messages": new_messages,
        "custom_field": value
    }
    
# 避免：直接修改 state 对象
@before_model
def bad_update(state, runtime):
    state["messages"].append(new_msg)  # 不推荐
    return None
```

---

## Python 关联知识

### 装饰器链

```python
# Middleware 本质是多层装饰器
@wrap_model_call
@log_calls
@measure_time
def model_call(request, handler):
    pass

# 等价于
model_call = wrap_model_call(log_calls(measure_time(model_call)))
```

### 高阶函数

```python
# Middleware 是高阶函数
def create_retry_middleware(max_retries: int):
    """创建可配置的重试中间件"""
    
    @wrap_tool_call
    def retry_middleware(request, handler):
        for i in range(max_retries):
            try:
                return handler(request)
            except:
                if i == max_retries - 1:
                    raise
                time.sleep(2 ** i)
    
    return retry_middleware

# 使用
retry_3 = create_retry_middleware(3)
retry_5 = create_retry_middleware(5)
```

---

## 常见陷阱

### 1. 中间件顺序错误

```python
# 错误：权限检查在日志之后
middleware=[
    LoggingMiddleware(),      # 先记录
    PermissionMiddleware(),   # 后检查权限
]

# 正确：权限检查应该在最前面
middleware=[
    PermissionMiddleware(),   # 先检查权限
    LoggingMiddleware(),      # 再记录
]
```

### 2. 忘记返回

```python
@before_model
def bad_middleware(state, runtime):
    state["messages"] = trim(state["messages"])
    # 错误：没有 return！

@before_model
def good_middleware(state, runtime):
    return {"messages": trim(state["messages"])}
```

### 3. 循环依赖

```python
# 避免在中间件中调用 agent
@before_model
def bad_idea(state, runtime):
    # 错误：会导致无限递归！
    result = agent.invoke({...})
    return state
```

---

## 相关概念

- [[LangChain-Agents]] - Agent 核心概念
- [[Python装饰器详解]] - Python 装饰器深入
- [[函数式编程]] - 高阶函数概念
