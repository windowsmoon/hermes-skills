---
name: loop-engine
description: >
  当需要递归自动化执行任务（循环/重试/状态机模式）时使用。
  支持：循环执行、状态持久化、重试退避、条件分支、超时控制。
  不要用于：一次性任务、简单顺序执行、需要人类交互的场景。
  触发词：循环执行、自动化循环、重试机制、状态机、递归任务
category: architecture
triggers:
  - 循环执行
  - 自动化循环
  - 重试机制
  - 状态机
  - 递归任务
tags:
  - loop-engine
  - loop

---

# Loop Engine Pattern — All Skill Scripts Should Follow This

## Why Loop Instead of delegate_task

`delegate_task` = 派子Agent → 等它回来 → 等不到 → 死在那。  
**Loop** = 每次执行都把结果写盘 → 下次 run() 从磁盘恢复 → 不依赖回调。

这是本 session 从用户否决 delegate_task 方案中验证的核心教训。

## Quick Start

```python
import sys
sys.path.insert(0, "C:/Users/Admin/AppData/Local/hermes/skills/loop-engine/scripts")
from loop_engine import Loop, Step, StepResult

def maker_load(ctx):
    return StepResult(data={"content": ctx["tools"]["read_file"](ctx["input_path"])})

def check_nonempty(ctx, output):
    return bool(output.get("content", "").strip())

loop = Loop(name="My Task", state_path="C:/path/to/state.md", steps=[
    Step("load", maker_load, check_nonempty, description="Load input"),
    Step("process", lambda ctx: StepResult(), human_gate=True, description="Wait approval"),
    Step("final", lambda ctx: StepResult(data={"ok": True}), description="Done"),
], tools={"read_file": read_file})

state = loop.run()
if state["status"] == "waiting_approval":
    state = loop.approve(state)
    state = loop.run()
```

## Core Architecture

```
load_state() → current_step() → maker() → checker() → save_state() → LOOP
                                      ↑ fail? → jitter retry ×3 → blocked
                                      ↑ human_gate → waiting_approval → approve()
```

## Loop Engineering 哲学

> **你不应该再手动 prompt 你的 Agent。你应该设计一个 loop，它自己 prompt Agent、检查结果、决定下一步。**  
> — Peter Steinberger / Boris Cherny (Claude Code)

传统的 `delegate_task` = 一次性派发 → 等子Agent返回 → 死在那。  
Loop = **递归自动化**：读状态 → 执行 → 验证 → 写状态 → 找下一项 → 重复。

### 循环的五要素（来自 Loop Engineering 原文）

| 要素 | 作用 | Loop Engine 映射 |
|:----|:----|:----------------|
| **Automations** | 定时心跳，发现 + 分类任务 | `cron_tick()` 函数 |
| **Worktrees** | 并行隔离，互不干扰 | 每个 Loop 独立 state 文件 |
| **Skills** | 将项目知识写下来，不用每次重新解释 | 本 Skill 本身就是 |
| **Plugins/Connectors** | 连接外部工具 | `ctx["tools"]` 注入 |
| **Sub-agents** | Maker（写）和 Checker（查）分离 | `Step.maker` / `Step.checker` |
| **State（第六要素）** | 磁盘上的记忆，Agent 会忘但文件不会 | `state_path` 指向的 .md 文件 |

为什么不能用 delegate_task 代替：**子Agent 返回不回，会死在那**。Loop 用状态文件驱动——每个步骤的结果都写盘，下次 run() 从磁盘恢复，不依赖任何回调通知。

## 核心模式

```
┌──────────────────────────────────────────────────────────┐
│  🔄 Loop Engine (loop_engine.py)                          │
│                                                           │
│  1. load_state()   ← 从 .md 文件恢复上次运行状态            │
│  2. current_step() ← 找到第一个未完成步骤                   │
│  3. maker(ctx)     ← 执行（写文件、调 API、跑子Agent）      │
│  4. checker(ctx,out) ← 验证结果是否合格                     │
│     ├─ PASS → 标记完成 → 前进一步                            │
│     ├─ FAIL → 重试+抖动 → 3次仍失败 → 标记阻塞              │
│     └─ human_gate → 暂停等你审批 → approve() 继续           │
│  5. save_state()   ← 每一步都写回磁盘                       │
│  6. LOOP ← 递归，直到完成或阻塞                             │
│                                                           │
│  触发方式:                                                  │
│  - execute_code() 手动 (推荐，有5min超时)                   │
│  - terminal(background) 后台进程 (长任务)                   │
│  - Cron 定时触发 (cron_tick)                               │
│  - Workflow 节点编排                                       │
└──────────────────────────────────────────────────────────┘
```

## 引擎 API 参考

```python
from loop_engine import Loop, Step, StepResult

# --- Maker（执行者）---
def maker_collect(ctx):
    tools = ctx["tools"]
    data = tools["read_file"]("input.txt")
    return StepResult(data={"lines": data.split("\\n")})

# --- Checker（验证者）---
def checker_collect(ctx, output):
    return len(output.get("lines", [])) > 0

# --- 组装 Loop ---
loop = Loop(
    name="示例任务",
    state_path="C:/path/to/state.md",
    steps=[
        Step("采集", maker_collect, checker_collect,
             description="采集原始数据"),

        # human_gate=True 的步骤会暂停等你审批
        Step("分析", maker_analyze, human_gate=True,
             description="AI分析（等你审批）"),

        # 无 checker = 不做验证，直接通过
        Step("完成", lambda ctx: StepResult(data={"ok": True}),
             description="收尾"),
    ],
    tools={"read_file": read_file, "write_file": write_file},
)

# --- 启动 Loop（递归直到完成或阻塞）---
state = loop.run()

# --- 人类审批 ---
if state["status"] == "waiting_approval":
    # 在我调 approve() 之前，状态文件停在当前步骤
    state = loop.approve(state)   # 批准 → 继续
    # 或 loop.reject(state, "原因")  # 驳回 → 标记 blocked
    state = loop.run()            # 继续执行下一轮
```

## Retry Jitter（重试抖动）

每次重试使用 **全抖动 (Full Jitter)**：`uniform(0, min(2^attempt * 5s, 120s))`

```
固定退避: Retry1=5s  Retry2=10s  Retry3=20s  ← 所有实例同时重试，打爆API
全抖动:   Retry1=0-5s Retry2=0-10s Retry3=0-20s ← 随机化，防雪崩
```

## 五阶段编排模式（Orchestrator Pattern）

这是高阶架构，运行在 Loop Engine 之上。详见 `skills/orchestrator-loop/SKILL.md`。

核心结构：
```
Phase 1: 任务触发  — 审批模型 + Sequential Thinking → /goal
Phase 2: 规划      — MOA(4模型) → 5COT → 比对打分 → 你选定
Phase 2c: COT烤问  — adversarial review grilling
Phase 3: 准备      — Kanban并行搜索 → 工具匹配
Phase 4: 执行      — Executor(v4-flash) + Auditor(v4-pro) 双Agent
Phase 5: 反馈      — matplotlib流程图 + 7维复盘
```

### 已配置的基础设施

| 组件 | 状态 | 说明 |
|:----|:----:|:-----|
| **审批辅助模型** | ✅ | `custom:183399/deepseek-v4-pro`，30s 超时 |
| **MOA Mind-Daily** | ✅ | Qwen3.7+/DeepSeek-V4-Pro/GLM-5.2/MiniMax-M3 + GPT-5.5聚合 |
| **Sequential Thinking MCP** | ✅ | `npx -y @modelcontextprotocol/server-sequential-thinking` |
| **matplotlib** | ✅ | v3.11.0，Agg 后端，可生成 200dpi PNG |
| **tavily 搜索** | ✅ | 已配 API key |
| **群聊房间** | ✅ | 5位总监 profile + SOUL.md + 邀请码 arch-review |
| **Loop Engine** | ✅ | 通用引擎，以上五阶段建立在此之上 |

## Cron 集成

```python
from loop_engine import cron_tick

state = cron_tick(loop)  # 一次 Cron 调用
# - 已完成 → 自动重置为 running（重新开始）
# - 阻塞/等审批 → 跳过，等人来处理
# - 运行中 → 继续执行一轮
# - 错误 → 重置
```

## needs_Agent Status & advance() Pattern

当 Maker 无法自行完成执行（需要 LLM 调用、浏览器操作、外部搜索等），用 advance() 模式代替阻塞：

```python
def maker_gather(ctx):
    with open("phase-instruction.md", "w") as f:
        f.write("Run tavily search for: ...")
    return StepResult(status="blocked", data={
        "instruction_file": "phase-instruction.md"
    })

# Agent 执行后调用 advance() 而非 approve():
state = loop.advance(state)  # 标记当前步骤 completed → 前进
state = loop.run()           # 继续下一轮
```

advance() 与 approve() 区别：approve 用于 human_gate（用户交互），advance 用于 blocked/needs_agent（Agent 执行指令）。

### advance() 实现

```python
def advance(self, state):
    sname = state["current_step"]
    ss = state["steps"].get(sname, {})
    ss["status"] = "completed"
    state["status"] = "running"
    state["blocked_reason"] = ""
    n = self._next_step(sname)
    if n:
        state["current_step"] = n
    else:
        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()
    self.save_state(state)
    return state
```

## State File Format

状态文件是 Markdown，人类可读、Agent 可解析。

```markdown
# Loop: My Task
Status: **running**
Updated: 2026-07-10 10:30

## Phase: load  ✅
> Load input data
- Status: **completed**
- Retries: 0/3
- Output: {"lines": 42}

## Phase: process  🟡
> AI processing, needs human approval
- Status: **waiting_approval** ⚠️ 需审批
- Retries: 0/3
- Errors:
  - Error: [10:28] API timeout, retrying...

## Phase: final  ⏳
> Wrap up
- Status: **pending**
- Retries: 0/3
```

## 已知问题（已修复）

### 问题 1：Parser 读错 current_step
- **症状**：`current_step` 指向文件中**最后一个** Phase 头，而不是实际待处理步骤
- **根因**：`_parse_md` 遍历 Phase 头时不断覆盖，最后一个覆盖了前面的
- **修复**：改为扫描 `step_order`，取第一个非 `completed/skipped` 的步骤

### 问题 2：Gate 标志双写
- **症状**：状态文件显示 `**waiting_approval** ⚠️ 需审批** ⚠️ 需审批`
- **根因**：渲染基于 Step 定义的 `human_gate=True`，而非步骤实际状态
- **修复**：改为当 `status == "waiting_approval"` 时才显示门禁标志

### 问题 3：Approve 打错步骤
- **症状**：`approve()` 操作了错误的步骤（跟问题 1 相关）
- **根因**：依赖了错误的 `current_step`
- **修复**：改为扫描所有步骤找 `waiting_approval` 状态

## 用法模式

### 模式 A：替代 delegate_task（再也不怕子Agent不返回）

```python
def maker_analyze(ctx):
    # 不依赖子Agent"回来"——直接把工作写入文件
    from hermes_tools import terminal
    result = terminal("python analysis.py")
    with open("analysis_result.json", "w") as f:
        f.write(result["output"])
    return StepResult(data={"status": "done", "output_file": "analysis_result.json"})

def checker_analyze(ctx, output):
    import os
    return os.path.exists(output.get("output_file", ""))
```

### 模式 B：多角度 MOA 分析

```python
def maker_moa(ctx):
    """替代 delegate_task 派5个子Agent"""
    perspectives = ["产品", "技术", "质量", "运营", "数据"]
    results = {}
    for p in perspectives:
        # 直接跑分析，不派子Agent。或者派 terminal 后台进程
        result = run_analysis(p, ctx["tools"])
        results[p] = result
        # 立即写盘，不会丢
        with open(f"analysis_{p}.json", "w") as f:
            json.dump(result, f)
    
    # 冲突检测
    conflicts = detect_conflicts(results)
    return StepResult(data={
        "analysis": results,
        "conflicts": conflicts,
    })

def checker_moa(ctx, output):
    return len(output.get("analysis", {})) >= 3  # 至少3个视角完成
```

### 模式 C：Group Chat 冲突解决

在 maker 中检测到冲突后，通过 Hermes Studio API 创建群聊房间：

```python
def maker_resolve(ctx):
    conflicts = ctx["state"]["steps"]["analyze"]["conflicts"]
    if not conflicts:
        return StepResult(status="skipped", skip_reason="No conflicts")
    
    # 调用 hermes_studio_api_request 创建群聊房间
    room = create_group_chat(conflicts)
    wait_for_resolution(room)
    return StepResult(data={"resolved": True, "room_id": room})
```
