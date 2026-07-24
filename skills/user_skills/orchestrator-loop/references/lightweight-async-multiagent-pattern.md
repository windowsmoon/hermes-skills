# 轻量级两层 Agent 协作模式（推荐）

> 适用于：快速迭代的小型 Agent 组织（2-3个Agent），不想上重框架的场景。
> 与 orchestrator-loop 的重型 5 阶段流水线互为补充（轻量 vs 重量，按需选择）。
>
> **V2 更新说明**（2026-07-18）：从"三层架构+群聊总线"演进为"两层架构+直接CLI调用"。
> 群聊降级为报警通道，不再作为消息总线。

## 架构概览（两层，推荐）

```
你（Hermes 对话框说需求）
    │
    ▼
Hermes（大脑/协调器）
    │   拆任务 → 判断"写代码还是执行操作"
    │
    ├──→ OpenCode/Codex（码农） — terminal("opencode '...'")
    │        写代码、造工具、重构
    │        输出结果到文件
    │
    └──→ Coze/扣子（操作手） — terminal("coze workflow run ...")
             跑工作流、部署、调 API
             返回执行结果
```

**就两层，不搞三层。** Hermes 是唯一的大脑，Worker 是它的两只手。

## 核心思想

1. **Hermes 直接 CLI 调用 Worker** — 不走群聊轮询，terminal 一把梭
2. **群聊降级为报警通道** — 只发 ERROR/审批/DONE，不发进度
3. **飞书看板 = 唯一事实来源** — 只有 Hermes 写，Worker 只输出文件/返回结果

## 为什么从三层变两层

| 维度 | 三层（原方案） | 两层（推荐） |
|------|--------------|-------------|
| 中层查底层 | 定时翻群聊记录 | 直接 CLI 等结果 |
| 群聊 | 消息总线（全发） | 报警通道（只发需要人的） |
| 协调者 | 单独一个"中层"角色 | Hermes 自己就是大脑 |
| 复杂度 | 🔴 高 | 🟢 低 |

**关键教训**：你已经在和 Hermes 对话了，Hermes 就是你的大脑，再加一个中层是多此一举。

## 组件职责

| Agent | 角色 | 做 | 不做 | 通信方式 |
|-------|------|---|------|---------|
| **Hermes** | 🧠 大脑 | 拆任务、决策、调人、写看板、通知你 | 不写代码、不执行部署 | 你→对话，Worker→terminal |
| **OpenCode/Codex** | ✋ 码农 | 写代码、造工具、审查 | 不决策、不部署 | Hermes 发 terminal 指令 |
| **Coze** | ✋ 操作手 | 跑工作流、部署、调 API | 不决策、不写代码 | Hermes 发 CLI/API 指令 |

## 决策逻辑

```
if "写代码" or "造工具" or "重构" → terminal("opencode '{需求}'")
elif "部署" or "执行任务" or "调API" → terminal("coze workflow run ...")
else → Hermes 自己处理
```

这个逻辑写在 Hermes 的系统提示词或 skill 里即可。

## 各 Agent 的 ACP/CLI 可用性

| Agent | CLI | ACP 协议 | 接入方式 |
|-------|-----|---------|---------|
| **Hermes** | ✅ `hermes` | ✅ Paseo ACP 目录 | 原生 |
| **OpenCode** | ✅ `opencode` | ✅ **原生** `opencode acp --port 3100` | CLI 或 ACP server |
| **Coze/扣子** | ✅ `@coze/cli` (npm) | ✅ Coze 3.0 coze-bridge (JSON-RPC 2.0) | CLI 或 HTTP API |
| **Codex CLI** | ✅ `codex` | ✅ Paseo ACP 目录 | CLI 或 ACP |
| **Kun** (类 Codex) | ✅ `kun serve` | ❌ 自有 HTTP API (非 ACP) | HTTP API，需适配层 |

### 关键发现：Coze 的 ACP 支持

Coze 3.0（2026年6月发布）包含 **coze-bridge** 组件：
- 基于 JSON-RPC 2.0 实现 ACP 协议
- 支持云端与本地 AI 编程助手之间的协议转换
- 原生支持 Claude Code、Codex CLI 等 ACP 兼容 Agent 的一键接入
- 配合 `@coze/cli`，Agent 可直接在后台操作扣子平台

### 关键发现：OpenCode 的 ACP 支持

OpenCode 原生支持 ACP 服务器模式：
```bash
opencode acp --port 3100   # 以 ACP 子进程模式启动，通过 stdio JSON-RPC 通信
```

### 关键发现：Kun 的接入

Kun (https://github.com/KunAgent/Kun) 是带 GUI 的编程工作台，有 `kun serve` HTTP API 但**不支持 ACP 协议**。可接受触发任务但需 HTTP 适配层。许可证：PolyForm Noncommercial 1.0.0，不可商用。

## 实操实现

### Hermes → OpenCode（编程）

在 Hermes 里配置一条 skill 规则：
```
当用户说"写一个..." / "帮我开发..." / "造一个工具"
→ terminal("opencode '{用户的需求}'")
→ 读输出文件验证
→ 写结果到飞书多维表格
```

### Hermes → Coze（执行）

```
当任务需要"部署" / "执行" / "运行" / "发送"
→ terminal("coze workflow run --workflow-id '{ID}' --params '...'")
→ 轮询或等回调
→ 写结果到飞书多维表格
→ 异常连续3次 → 飞书群通知你
```

### 看板规则

- **Hermes 统一写**飞书多维表格（唯一事实来源）
- OpenCode 只写 **文件系统**（产出代码）
- Coze 只返回 **执行结果** 给 Hermes
- 避免多人同时写看板导致覆盖

## 与重型模式的选择依据

| 场景 | 推荐模式 |
|------|---------|
| 长期复杂项目（>2天），需严格规划 | orchestrator-loop 重型模式 |
| 快速迭代的小型 Agent 团队（2-3个Agent） | **轻量两层模式（推荐）** |
| 单个任务开发，不需要跨 Agent 协作 | 直接对话，不套框架 |

## 关键坑点

1. **Hermes 单点故障**：协调者若离线整条链断裂。异常需升级通道（ERROR 直通知顶层用户）
2. **Worker 调用超时**：terminal() 调用需设合理 timeout + 重试退避
3. **看板写冲突**：只用飞书多维表格（行级锁），或加字段级权限，仅 Hermes 写
4. **OpenCode/Coze 不需要改代码**：OpenCode 有 CLI，Coze 有 API，直接在 Hermes 里 terminal 调用即可