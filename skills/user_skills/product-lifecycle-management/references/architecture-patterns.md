# 架构决策模式：Orchestrator 脚本 vs Web UI 工作流

## 问题背景
Hermes 中实现多步骤串联流程时，有 3 种可选架构。选择取决于流程复杂度、是否需要可视化、是否需要跨 Session 复用。

## 三种架构对比

| 维度 | 对话编排（默认） | Orchestrator 脚本 | Web UI 工作流 |
|------|----------------|------------------|---------------|
| **原理** | 我在对话中读产出 → 问用户 → 调下一步 | Python 状态机管理步骤流转 | 可视化节点+连线，API 驱动 |
| **适用场景** | 2-3 步简单串联 | 4-18 步复杂流程 | 需要可视化+保存复用的流程 |
| **状态持久化** | ❌ 靠对话历史 | ✅ JSON 文件（跨 session） | ✅ 工作流引擎自带 |
| **条件分支** | ✅ 灵活（我问用户） | ⚠️ 要预设分支逻辑 | ⚠️ 汇合策略需手动配 |
| **修改流程** | ✅ 对话中随时改 | ❌ 改脚本 | ⚠️ 回画布拖拽 |
| **可视化** | ❌ | ❌ | ✅ |
| **跨 Session 复用** | ❌ | ✅ 状态文件可恢复 | ✅ 工作流模板 |

## 当前采用情况

| 流程 | 采用架构 | 说明 |
|------|---------|------|
| 产品生命周期 18 步 | Orchestrator 脚本 | `plm_orchestrator.py`，JSON 状态持久化 |
| Smart PPT 流水线 | 对话编排 + Shell 脚本 | `smart_ppt.py`，状态在对话中 |
| ACP 开发流水线 | 对话编排 + delegate_task | 无持久化，一次性流程 |

## 选择原则

1. **2-3 步 + 不需要复用** → 对话编排（最简单）
2. **4 步以上 + 需要跨 session 恢复** → Orchestrator 脚本（当前推荐的折衷）
3. **需要可视化拖拽 + 团队共享** → Web UI 工作流

## Web UI 工作流注意事项

- 通过 `hermes_studio_use_workflow_create` API 创建
- 节点类型为 `agentNode`，需配置 `data.agent` 字段（含 model/provider）
- 创建后可在 Web UI 画布拖拽修改节点位置和连线
- 当前版本不支持创建后自动运行，需在 Web UI 中手动启动
- 节点格式验证在后端，建议先通过 Web UI 手动创建一个节点，用 `workflow_get` 导出格式再批量创建

## 2026-07-20 更新：新增 Kanban 调度层

### 四层架构（原三层 + Kanban）

| 维度 | 对话编排（默认） | Kanban 调度（新增） | Orchestrator 脚本 | Web UI 工作流 |
|------|----------------|-------------------|------------------|---------------|
| **原理** | 我在对话中读产出 → 调下一步 | 看板任务队列，Gateway 自动派 Worker | Python 状态机管理步骤流转 | 可视化节点+连线，API 驱动 |
| **适用场景** | 2-3 步简单串联 | 跨 Profile 异步协作 | 4-18 步复杂流程 | 需要可视化+保存复用的流程 |
| **状态持久化** | ❌ 靠对话历史 | ✅ SQLite 数据库 | ✅ JSON 文件（跨 session） | ✅ 工作流引擎自带 |
| **跨 Profile 协作** | ❌ | ✅ 原生支持 | ❌ | ❌ |
| **自动调度** | ❌ 手动 | ✅ Gateway Dispatcher 自动轮询 | ❌ 手动触发 | ⚠️ 手动启动 |

### 选择原则（更新版）

1. **2-3 步 + 不需要复用** → 对话编排（最简单）
2. **需要跨 Profile 协作 + 异步执行** → Kanban 调度
3. **4 步以上 + 需要跨 session 恢复** → Orchestrator 脚本
4. **需要可视化拖拽 + 团队共享** → Web UI 工作流

### 关键约束：Profile 是隔离的，不是路由目标（2026-07-20 更新）

**Kanban 改变了这一点。** 通过 Kanban 的共享数据库 + Gateway Dispatcher，现在可以实现跨 Profile 任务调度：

| 你想做的事 | 现在怎么做 |
|-----------|-----------|
| default 派任务给 engineering-director | ✅ Kanban create task --assignee engineering-director |
| 看到 engineering-director 的执行结果 | ✅ 看板 result 字段（但看不到完整 Session 对话） |
| 跨 Profile 共享上下文 | ⚠️ Kanban result + Hindsight 记忆银行 |
| 需要实时看到每一步 | ❌ 走 delegate_task 而非 Kanban |

**所以现在的正确做法变成：**

```
你 → 主 Agent（default profile）
  ↓ 意图理解 + 任务拆分
  ↓ 读 Profile能力矩阵.md
  ├── 当前 Session 能搞定 → delegate_task（实时可见，可审计）
  ├── 需要跨 Profile 协作 → Kanban 后台调度（你零感知）
  └── 需要独立技术栈 → Hermes-OpenCode-Coze（问你同意）
  ↓ 所有结果汇总 → 交付给你
  ↓ 只有出错才报你
```

## 参数呈现原则（2026-07-17 用户偏好）

用户明确反馈「不想做填充题」——所有需要用户选择参数的场景，必须按**选择题格式**呈现：

```
### ① 配色风格
> 选哪种整体配色？
  1. 🔵 科技蓝（深蓝+青绿）
  2. 🟣 赛博朋克（霓虹粉+青蓝）
  3. ⚪ 极简白（白+灰+点缀红）
  4. 🔢 自定义（你说我调）
```

**规则**：Emoji 前缀 + 中文名称 + 括号说明 + 用户只需回复数字 + 必须包含「默认」选项。

## 多层降级架构（Smart PPT 模式）

复杂任务应有多层降级路径，当首选方案不可用时自动 fallback：

```
主路径 → ChatPPT（云端，有额度）
  ↓ code=11500（额度用完）
备用路径 → GordenPPTSkill（离线本地，21套模板）
  └→ HTML演示（frontend-design + uiux-slides，完全免费，零API调用）
```

这种降级模式适用于所有有外部依赖的 skill：先尝试最强大的方案，失败后自动降级到离线/免费方案。

## 注意

Web UI 工作流虽然有可视化画布，但工作流的创建和维护通过 `hermes-studio-use` MCP 中的 API 进行（`workflow_create`/`workflow_update`/`workflow_run_start`）。节点格式为 `agentNode` 类型，需要包含 `data.agent` 字段。当前后端验证较严格，建议通过 Web UI 手工创建后，用 `workflow_get` 检查节点格式再批量添加。
