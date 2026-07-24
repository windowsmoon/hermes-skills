# 三层架构 × 组织类比

> 2026-07-20 用户确认的架构决策框架
> 核心观点：Hermes-OpenCode-Coze、Kanban、delegate_task 分别对应不同层级的协作模式。

## 宏观→微观排序

```
Hermes-OpenCode-Coze（跨Agent / 跨企业合作）
  > Kanban（跨Profile / 跨部门协作）
    > delegate_task（同Profile / 部门内群聊）
```

## 组织类比

| 架构层 | 组织类比 | 通信方式 | 看到什么 | 审计能力 |
|--------|---------|---------|---------|---------|
| **Hermes-OpenCode-Coze** | 跨企业合作 | ACP/API 标准协议 | 只看最终交付物 | ❌ 三方独立体系，无法审计对方内部 |
| **Kanban** | 跨部门协作 | 共享看板（Kanban DB） | 看板上的任务状态+结果 | ❌ 看不到部门内部对话，只看到工单 |
| **delegate_task** | 部门内群聊 | 直接对话分配 | 实时可见每一步 | ✅ 默认 Profile 可审计所有子任务对话 |

## 关键约束

**跨 Profile 无法看到其他 Profile 的 Session 对话内容。** Kanban 派出去的任务，default Profile 只能看到看板上的 `result` 字段，看不到 `engineering-director` 执行时的完整对话。这是 Profile 隔离机制决定的。

## 选择逻辑

```
这个任务我需要：
  ├── 事后审计完整对话？ → delegate_task（同一部门内）
  ├── 跨部门协作，只看结果就行？ → Kanban（看板调度）
  └── 完全独立的技术栈和工具链？ → Hermes-OpenCode-Coze（跨企业合作）
```

## 信息可见度对比

| 方式 | 你能否看到执行过程？ | 结果怎么回来？ | 适合 |
|------|-------------------|---------------|------|
| **delegate_task** | ✅ 实时可见，SubAgent 每一步都回传 | 自动汇入当前对话 | 需要边看边调 |
| **Kanban** | ❌ 看不到 Worker 的 Session 内容 | 看板 `result` 字段 + 通知 | 发出去就不管了 |
| **Hermes-OpenCode-Coze** | ❌ 完全独立系统 | ACP/API 结果返回 | 需要独立工程环境 |

## 用户零感知执行原则

```
你只跟 default Profile 说话
  → 我自动拆解任务
  → 我自动读能力矩阵，决策走哪条路
  → 我自动调度（delegate_task / Kanban / 三Agent）
  → 我自动收集结果
  → 我自动汇总给你
  → 只有出错才报你
你全程不需要碰任何其他 Profile 或 Agent
```


### Kanban Enhancer 增强

从 2026-07-24 起，Kanban 调度增加了 4 项增强能力（通过 `kanban-enhancer` skill 实现）：

1. **工具亲和性检查** — 创建任务时检查分配目标是否有对应工具
2. **结果标准化** — 强制所有 result 字段为 JSON 格式
3. **失败升级链** — 失败任务自动跨 Profile 升级
4. **验证门禁** — 关键任务完成后自动生成验证子任务

> 详见 `devops/kanban-enhancer` skill

## 集成点

- **orchestrator-loop SKILL.md** → 三种编排方式选择章节
- **helper-opencode-integration** → SRE 对接外部 Agent
- **轻量模式 reference** → 两层架构+直接CLI调用