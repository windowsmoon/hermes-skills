# Hermes Studio Kanban 配置与使用指南

> 2026-07-20 发现并配置。Hermes Studio 内置 Kanban 是一个 SQLite 共享数据库驱动的跨 Profile 异步任务调度系统，不是飞书多维表格。

## 架构概览

```
你（当前对话，default profile 作为调度者）
  │  kanban_create task --assignee engineering-director
  │  kanban_create task --assignee qa-director
  ▼
Kanban DB（共享 SQLite，~/.hermes/kanban.db）
  │  tasks: [triage → todo → ready → running → done]
  ▼
Gateway 内置 Dispatcher（后台轮询，默认60秒一次）
  │  发现 ready 任务 → 按 assignee 匹配 profile
  │  自动 spawn: hermes -p <profile> chat -q "..."
  ▼
各 Profile Worker 独立执行
  │  完成 → kanban_complete() 更新状态
  │  阻塞 → kanban_block() 更新状态
  ▼
你收到通知 ← auto_subscribe_on_create 自动推送
```

## 配置步骤

### 1. 开启 Kanban 工具集

```yaml
# ~/.hermes/config.yaml
toolsets:
  - hermes-cli
  - kanban            # ← 添加这一行，agent 才能调用 kanban 工具
```

### 2. 配置 Kanban 调度参数

```yaml
# ~/.hermes/config.yaml
kanban:
  auto_subscribe_on_create: true        # 创建任务后自动订阅通知
  dispatch_in_gateway: true             # 调度器跑在 Gateway 进程内
  dispatch_interval_seconds: 60         # 每60秒轮询一次可执行任务
  failure_limit: 2                      # 连续失败2次后自动阻塞
  orchestrator_profile: "default"       # 任务分解器用 default profile
  default_assignee: "default"           # 找不到 assignee 时的兜底
  max_in_progress_per_profile: 10       # 每个 Profile 最多同时跑10个任务
  auto_decompose: true                  # 自动分解 Triage 任务
  auto_decompose_per_tick: 3            # 每轮最多分解3个
  dispatch_stale_timeout_seconds: 14400 # 4小时无心跳则回收任务
```

## Kanban 工具集（Agent 可用工具）

| 工具 | 权限 | 用途 |
|------|------|------|
| `kanban_create` | 调度者/Worker | 创建任务，可指定 assignee/board/skills |
| `kanban_show` | 调度者/Worker | 查看任务详情 |
| `kanban_complete` | Worker | 完成任务并提交结果 |
| `kanban_block` | Worker | 阻塞任务，说明原因 |
| `kanban_heartbeat` | Worker | 发送心跳，防止被回收 |
| `kanban_comment` | 调度者/Worker | 添加评论 |
| `kanban_link` | 调度者/Worker | 关联任务 |
| `kanban_list` | 仅调度者 | 列出看板上的任务 |
| `kanban_unblock` | 仅调度者 | 解除阻塞状态 |

## 常用 CLI 命令

```bash
# 创建任务并指派
hermes kanban create "实现登录API" --assignee engineering-director --board project-1

# 查看看板
hermes kanban list --status ready

# 分解 triage 任务为子任务图
hermes kanban decompose <task_id>

# Swarm 并行拓扑（多个 Worker + Verifier + Synthesizer）
hermes kanban swarm \
  --worker "engineering-director:实现API:python,fastapi" \
  --worker "qa-director:编写测试:pytest" \
  --verifier-assignee "product-manager" \
  --synthesizer-assignee "default" \
  "开发用户登录模块"
```

## 三种调度方式对比

| 维度 | Kanban 调度 | delegate_task | OpenCode-Coze |
|------|------------|---------------|---------------|
| **协作范围** | 跨 Profile 异步 | 当前 Session 同步 | 外部工具链 |
| **反馈方式** | 通知推送 | 结果自动回传 | terminal 等结果 |
| **时效性** | 分钟级（60秒轮询） | 秒级 | 秒-分钟级 |
| **适用场景** | 多角色流水线 | 单角色子任务 | 工程开发+部署 |
| **配置要求** | 需 toolsets + kanban 配置 | 零配置 | 需安装 CLI 工具 |

## 关键注意事项

1. **Kanban ≠ 飞书多维表格**。Hermes Studio Kanban 是内置的 SQLite 任务调度系统，飞书表格只是用户自己搭的看板
2. **Dispatcher 必须运行中**。调度器默认嵌入 Gateway 进程，重启 Gateway 后自动恢复
3. **Profile 需存在**。assignee 指定的 Profile 必须在 Profiles 列表中，否则任务会阻塞
4. **并发控制**：`max_in_progress_per_profile: 10` 防止单个 Profile 被任务淹没
5. **任务超时**：`dispatch_stale_timeout_seconds: 14400`（4小时），无心跳自动回收