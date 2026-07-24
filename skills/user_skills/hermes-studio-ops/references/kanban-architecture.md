# Hermes Studio Kanban 架构详解

> 基于源码分析（hermes_cli 0.18.2）

## 核心设计原则

> "Profiles intentionally collapse onto a shared board: it IS the cross-profile coordination primitive."

看板是 Hermes 的**跨 Profile 协调原语**。所有 Profile 共享同一个看板数据库，这是有意为之的设计。

## 源码模块

### 1. `kanban_db.py` — 数据库层（~360KB，8644行）

**路径**: `~/.hermes-web-ui/.../hermes_cli/kanban_db.py`

**数据模型**：
- `tasks` — 任务表（id, title, body, assignee, status, priority, tenant, workspace_kind, workspace_path, branch_name, project_id, created_by, created_at, started_at, completed_at, result, skills, max_retries, session_id...）
- `task_links` — 任务关联（parent-child 关系）
- `task_comments` — 任务评论（含 structured JSON 用于 swarm blackboard）
- `task_events` — 事件日志

**状态机**：`todo → ready → running → done`（含 blocked, archived, triage）

**并发策略**：
- WAL mode + `BEGIN IMMEDIATE` for write transactions
- CAS (compare-and-swap) on `tasks.status` and `tasks.claim_lock`
- SQLite serializes writers via WAL lock → at most one claimer wins

**多看板支持**：`boards/<slug>/` 目录，每个板独立 DB。`HERMES_KANBAN_BOARD` 环境变量 pin 到特定板。

### 2. `kanban.py` — CLI 层（~112KB，2766行）

**入口函数**：`kanban_command(args)` → 根据 args 分发到 `kanban_db` 函数

**子命令**：
- `kanban create` — 创建任务
- `kanban list` — 列出任务（支持 `--status`, `--assignee`, `--board` 过滤）
- `kanban claim` — 认领任务
- `kanban complete` — 完成任务
- `kanban block` — 阻塞任务
- `kanban decompose` — 分解任务
- `kanban swarm` — 创建 swarm 拓扑
- `kanban specify` — 展开 triage 任务
- `kanban boards` — 管理多看板
- `kanban diagnostics` — 诊断

**状态图标**：
```
◻ todo     ▶ ready    ● running    ⏱ scheduled
⊘ blocked   ✓ done     — archived
```

### 3. `kanban_decompose.py` — 任务分解器（~16KB，398行）

**核心流程**：
1. 读取 triage 任务（rough idea，通常只有标题）
2. 调用 auxiliary LLM，传入 profile roster（name + description）
3. LLM 返回 JSON `{fanout, rationale, tasks: [{title, body, assignee, parents}]}`
4. 原子创建子任务 + 链接到根任务
5. 根任务 `triage → todo`

**系统提示词要点**：
- `"parents"` 是 tasks 数组的 0-based 索引
- 不存在的 assignee 自动降级为 default_assignee
- 子任务 NEVER 有 `assignee=None`

### 4. `kanban_swarm.py` — 拓扑层（~9KB，199行）

**Swarm 拓扑**：
```
planning root (completed immediately)
    ├─ parallel specialist workers (ready)
    └─ verifier (todo until all workers done)
         └─ synthesizer (todo until verifier done)
```

**共享黑板**：结构化 JSON 评论写在 root task 上，前缀 `[swarm:blackboard]`

**创建函数**：`create_swarm(conn, *, goal, workers, max_retries...)` → `SwarmCreated(root_id, worker_ids, verifier_id, synthesizer_id)`

### 5. `kanban_specify.py` — 任务说明器（~9KB，194行）

**流程**：triage task → LLM 生成 `{title, body}` → `triage → todo`

**body 结构**：**Goal** / **Approach** / **Acceptance criteria** / **Out of scope**

**设计**：one-shot，无重试循环，JSON 解析 lenient（容忍 markdown code fence）

### 6. `kanban_diagnostics.py` — 诊断层（~42KB，1028行）

**Diagnostic 结构**：`{kind, severity(warning|error|critical), title, detail, suggested_actions[]}`

**规则**：stateless, read-only, 按需计算（dashboard load 时 / CLI 主动调用）

**Severity 顺序**：warning(amber) → error(orange) → critical(red)

### 7. `kanban_tools.py` — 工具层（Agent 接口）

**注册条件**：
- `HERMES_KANBAN_TASK` 环境变量被设置（dispatcher-spawned worker）
- 当前 profile 的 `toolsets` 包含 `"kanban"`（orchestrator profile）

**工具分类**：
- **Worker 生命周期工具**（worker 可用）：`kanban_complete`, `kanban_block`, `kanban_heartbeat`
- **Orchestrator 工具**（orchestrator 可用）：`kanban_list`, `kanban_unblock`, `kanban_create`

### 8. `kanban_watchers.py` — 调度层（Gateway 集成）

**功能**：Gateway 后台 tick 驱动，自动：
1. 轮询看板，发现 `ready` 任务
2. 自动 spawn worker subprocess（注入 `HERMES_KANBAN_TASK` 环境变量）
3. 处理 notification 和 artifact 交付
4. `auto_decompose` 开关控制是否自动分解 triage 任务

## DB 路径

| 看板 | 路径 |
|------|------|
| default 看板 | `~/.hermes/kanban.db` |
| 其他看板 | `~/.hermes/kanban/boards/<slug>/kanban.db` |
| 工作空间 | `~/.hermes/kanban/workspaces/` |
| 日志 | `~/.hermes/kanban/logs/` |

## 关键配置

```yaml
# config.yaml
kanban:
  auto_decompose: true           # 自动分解 triage 任务
  auto_decompose_per_tick: 3     # 每轮最多分解 3 个

toolsets:
  - kanban                       # 当前 profile 启用看板工具
```

## 多看板支持

- 命令行：`hermes kanban --board <slug>`
- 环境变量：`HERMES_KANBAN_BOARD=<slug>`
- 当前选择：`~/.hermes/kanban/current`（单行文本，写 slug）
- 默认看板：`default`

## 实践中怎么用

### 方式 A：我（主Agent）直接操作看板
```
"帮我看看看板上有什么任务"
→ 我调 kanban_list 工具 → 返回结果
```

### 方式 B：通过 CLI 命令
```
/kanban list
/kanban create "开发XXX" --assignee engineering-director
```

### 方式 C：Web UI 看板视图
HTTP://localhost:8748 → 左侧导航栏 → 看板视图
拖拽卡片改变状态，右键查看/编辑任务详情

### 方式 D：自动调度
Gateway 自动发现 ready 任务 → spawn worker → 自动执行

## Kanban 增强（kanban-enhancer，2026-07-24）

Kanban 自带的状态机 `todo→ready→running→done` 缺少中间门禁。通过 `devops/kanban-enhancer` skill 增加了 4 项外围增强（不修改核心代码）：

| 增强项 | 触发点 | 做什么 |
|--------|--------|--------|
| 工具亲和性 | `triage/todo` 状态 | 检查分配的目标 Profile 是否有执行任务所需的工具 |
| 结果标准化 | `done` 状态 | 强制 result 字段为 JSON 格式 |
| 失败升级 | `blocked/failed` 状态 | 按链升级：重试→同级互转→default→终极停止 |
| 验证门禁 | `done` 状态（关键任务） | 自动创建 `[Verify]` 子任务分配给 default |

**调度方式**：cron job 每 5 分钟轮询 Kanban DB（SQLite 只读），状态文件 `~/.kanban-enhancer-state.json` 防重复。

**数据源**：`D:/Obsidian/Note/Profile能力矩阵.md` 提供工具-Profile 映射表。

**失败升级链**：
```
Level 1: 原Profile 重试2次（Kanban 内置 failure_limit）
Level 2: 同级Profile接盘（研发↔测试，运营↔数据）
Level 3: 升级到 default（人工介入，human_gate）
Level 4: 终极停止（标记为 blocked，通知用户）
```

**结果标准化格式**：
```json
{
  "status": "success | failed | partial",
  "summary": "简要描述执行结果（不超过500字）",
  "artifacts": [
    {"type": "feishu-table | file | url | image", "url": "..."}
  ],
  "duration_seconds": 120,
  "errors": []
}
```

> 详见 `devops/kanban-enhancer` skill