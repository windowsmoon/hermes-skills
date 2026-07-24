---
name: orchestrator-loop
description: >
  当用户给出复杂任务（需要多步规划、多Profile协作、或跨Agent调度）时自动触发。
  五阶段：任务触发→多模型COT规划→执行准备→Loop执行→复盘反馈。
  不要用于：简单对话/单步任务（走正常对话）、已有明确skill的任务（先查skill注册中心）。
  触发词：任务：、开始任务、执行任务、新任务、帮我把这个项目做完
engine: loop-engine
category: architecture
triggers:
  - 任务：
  - 开始任务
  - 执行任务
  - 新任务
  - 帮我把这个项目做完
tags:
  - orchestrator-loop
  - orchestrator

---

# Orchestrator Loop — 通用任务编排工作流

## 触发条件

包含以下触发词之一：`任务：` / `开始任务` / `执行任务` / `新任务`。简单任务不触发。

## 三种编排方式选择（2026-07-20 更新）

### 核心原则：按宏观→微观排序

```
Hermes-OpenCode-Coze（跨Agent / 跨企业合作）
  > Kanban（跨Profile / 跨部门协作）
    > delegate_task（同Profile / 部门内群聊）
```

### 组织类比

| 架构层 | 组织类比 | 通信方式 | 看到什么 | 审计能力 |
|--------|---------|---------|---------|---------|
| **Hermes-OpenCode-Coze** | 跨企业合作 | ACP/API 标准协议 | 只看最终交付物 | ❌ 三方独立体系 |
| **Kanban** | 跨部门协作 | 共享看板（Kanban DB） | 任务状态+结果 | ❌ 看不到部门内部对话 |
| **delegate_task** | 部门内群聊 | 直接对话分配 | 实时可见每一步 | ✅ 可审计所有子任务对话 |

> 详见 `references/three-layer-architecture.md` — 完整类比、选择逻辑、信息可见度对比

### 关键约束：跨 Profile 无法看到其他 Profile 的 Session 对话内容

Kanban 派出去的任务，你（default Profile）只能看到看板上的 `result` 字段，看不到 `engineering-director` 执行时的完整对话。这是 Profile 隔离机制决定的。

### 三种方式详解

#### 方式 A：Kanban 调度（推荐用于跨 Profile 异步协作）
利用 **Hermes Studio 内置 Kanban 系统**（SQLite 共享数据库），通过 `kanban_create` 创建任务并指派给指定 Profile，Gateway 内置 Dispatcher 自动轮询并 spawn Worker 执行。
- **适用场景**：跨多个 Profile 协作、任务执行时间长、发出去不用盯
- **配置**：`~/.hermes/config.yaml` 中 `toolsets: ["hermes-cli", "kanban"]` + `kanban:` 配置块
- **详见**：`references/hermes-kanban-config.md`

#### 方式 B：delegate_task 子任务（推荐用于当前 Session 内同步协作）
在当前 Session 内直接派 SubAgent，结果自动回传当前对话。
- **适用场景**：子任务在当前 Session 内就能完成、需要拿到结果继续走下一步
- **不依赖**：Profile 切换、Kanban 配置、外部服务

#### 方式 C：Hermes-OpenCode-Coze 三Agent（推荐用于工程开发协作）
Hermes 做大脑，terminal 调用 OpenCode（写代码造工具）和 Coze（执行操作）。
- **适用场景**：需要写完整工程代码、需要调用外部 API 执行部署、需要独立技术栈
- **详见**：`skills/hermes/three-agent-orchestrator/SKILL.md` + `references/lightweight-async-multiagent-pattern.md`

### 选择决策树

```
任务来了（用户只跟 default Profile 说话）
  │
  ├── 我（default Profile）自动拆解任务
  │
  ├── 读 Profile能力矩阵.md → 判断哪个 Profile 有合适工具
  │
  ├── 只需要换个专业视角？（分析/评估/审查/建议）
  │     → delegate_task 派 SubAgent（当前 Session 内）
  │     例：审代码→工程总监、写测试用例→QA总监
  │
  ├── 涉及多个 Profile 协作？（异步，发出去不用盯）
  │     → Kanban 后台调度（你零感知）
  │     例：研发写代码 → QA 测试 → 运维部署
  │
  ├── 需要写工程代码 + 外部执行？（独立技术栈）
  │     → Hermes-OpenCode-Coze（问你同意后才走）
  │     例：开发并部署一个完整 Web 应用
  │
  └── 找不到工具？
        → 先翻 Hermes 已有生态 → 搜3个方向 → 能集成则集成
        → 不能则问用户要不要走 Coze
```

### 用户零感知执行原则

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

### 搜索工具的行为规则（2026-07-20 用户纠正）

当需要找新工具时，**禁止**搜一次就说"没有"：
1. ✅ 先翻 Hermes 已有生态（skills、MCP、CLI、插件）—— 反复犯过忽略已有能力的错误
2. ✅ 再用 web_search 搜至少 3 个不同方向（'API for X'、'CLI for X'、'MCP server for X'）
3. ✅ 搜不到才说没有，附上搜索记录（搜了什么方向、什么关键词）
4. ✅ 让用户补充方向，而不是直接下结论

> 历史教训：session mrqillm6y8pujm 中用户要找视频剪辑工具，我直接说"没有"，但实际有 ChatCut MCP、NemoVideo OpenClaw、pyJianYingDraft 等多个方案。session 3813bcd4-3c90-4c19-a782-bd46dc865a14 中我忽略了 Hermes 已有插件就能解决问题。

## 重型模式：5 阶段流水线（默认，适用于长期复杂项目）
适用于长期复杂项目（>2天），需严格规划。以下 9 步流水线。

### 轻量模式：两层架构 + 直接 CLI 调用
适用于快速迭代的小型 Agent 团队（2-3个Agent）。
见 `references/lightweight-async-multiagent-pattern.md`。

## 9 步流水线（重型模式）

```
Phase 1: task-trigger    [Agent执行] 审批模型 + Sequential Thinking → /goal 声明
Phase 2: moa-analysis    [Agent执行] MOA 4模型 + SeqThink → 5份COT → 比对
Phase 2b: cot-selection  [人类选择] 选定 COT 路径（或 "先讨论"→群聊）
Phase 2c: cot-grill      [Agent执行] adversarial review(deepseek-v4-pro) 烤问选定 COT
Phase 3: prep-info       [Agent执行] Kanban 并行搜索(tavily/Exa/Firecrawl) → 筛选
Phase 3b: prep-tools     [人类确认] 工具匹配表确认
Phase 4: execute         [Agent执行] Kanban 角色流水线(research/execute/review) + Auditor
Phase 5a: report         [Agent执行] matplotlib 200dpi 实际执行路径流程图
Phase 5b: retrospective  [Agent执行] 7维复盘(目标完成度/工具性能/CoT正确性/资源效率/用户满意度/信息有效性/可改进点)
```

## 执行模式

### 质量原则（2026-07-20 用户强调）

> **不要给我省token，认真做，好好做。**
> 宁可多用token确保质量，也不要为了省token而偷工减料。
> 搜索工具时搜不到就换方向继续搜，不要搜一次就说"没有"。
> 重写description时每条都要有边界、排除场景、触发词，缺一不可。

### 步骤类型
- **[Agent执行]**：Maker 写指令到 workspace → 返回 blocked → Agent 读指令执行 → loop.advance()
- **[人类选择]**：human_gate=True，Loop 暂停等你审批/选择

## 关键架构原则（Session 修正记录）

### 原则 1：Sequential Thinking 的定位
**不是**任务分解器。它的两个产出：
1. **预判信息缺口** → 驱动用户补充细节（默认模型不会追根究底）
2. **作为第5份独立 COT** → 交给默认模型打分比较

跟 MOA 的 4 份 COT 分工明确：MOA 出方法论和实现步骤，SeqThink 出信息缺口和逻辑预判。

### 原则 2：MOA vs 搜索工具的边界
| 工具 | 做什么 | 不做什么 |
|:----|:------|:--------|
| **MOA (Mind-Daily)** | 方法论、实现步骤、总体思想 | ❌ 不负责搜外部数据 |
| **tavily / Exa / Firecrawl** | 采集外部信息和事实数据 | ❌ 不生产方法论 |

MOA 的上下文是用来决定"怎么做"的，不是用来提供"外部是什么情况"的。

### 原则 3：三张流程图各司其职
| 阶段 | 图 | 记录什么 |
|:----|:---|:--------|
| Phase 2 | **原始骨架图** | 各 COT 的原始计划路径，标注选择理由+风险，用于横向比较 |
| Phase 4 前 | **增强版（改进）图** | 用户选定 COT + 整合其他 COT 优势 + 注入搜索数据后的执行计划 |
| Phase 5 | **实际执行图** | 真实走过的路——必然有偏差，但完整记录策划→定案→最终路径 |

**不要试图合并成一张图。** 路径不可能预告精准，三张图记录的是决策演变过程，全景复盘需要三张都保留。

### 原则 4：人类交互密度是设计特性，不是缺陷
现阶段（观察期）所有门禁都保留：
- Phase 1 SMART 验证 → 必问
- Phase 2b COT 选择 → 必选
- Phase 3b 工具确认 → 必确认
- Phase 4 授权点 → 必暂停

当默契建立后，门禁逐步关，你主动提优化。这不是技术问题，是渐进信任问题。

### 原则 5：Phase 4 失败 ≠ 灾难
Phase 4 挂了某个节点 → **不是回退到 Phase 2**。
记录：①哪个环节 ②失败原因 ③跟策划的哪条预判对不上 → 交给 Phase 5 正常复盘 →
Phase 5 输出经验教训 → 下一次 Phase 1 做 COT 时注入作为已知风险。
失败是素材，不是回退信号。

## 核心设计

### Phase 2c: COT Grilling
Checker 扮演 adversarial reviewer，逐条质问选定 COT（假设/边界/替代/缺失），最多3轮迭代，写入 grill-report.md，ALL_RESOLVED 才放行。

### Phase 3 & 4: Hermes Studio Kanban 并行化（2026-07-20 更新）
利用 Hermes Studio 内置 Kanban 系统做跨 Profile 并行调度。需先配置 `toolsets: ["hermes-cli", "kanban"]` 并确保 Gateway Dispatcher 运行中。
- Phase 3：每条信息缺口 = 一个 Kanban task card → 指派给搜索 Worker → 完成统一筛选
- Phase 4：三列流水线 — research(搜索) / execute(实现) / review(验证)，依赖任务 block→unblock，Auditor 每3节点审计
- 调度方式：Gateway 内置 Dispatcher 自动轮询 `ready` 任务，按 `assignee` spawn Worker


### Phase 3: prep-info + prep-tools（并行执行）

Phase 3 同时做两件事，**互不依赖，并行执行**：

```
Phase 3: prep-info + prep-tools（并行）
  │
  ├── prep-info（数据采集）← 找数据原材料
  │     Kanban 并行搜索 tavily/Exa/Firecrawl
  │     → 筛选 → 整理 → 输出给 Phase 4 使用
  │
  └── prep-tools（工具对接）← 8步任务执行流程
        ① 感知 → ② 拆解 → ③ 读能力矩阵
        → ④ 决策路径 → ⑤ 找不到工具时搜索
        → ⑥ 执行 → ⑦ 汇总 → ⑧ 更新能力矩阵
```

**Phase 4 需要同时拿到数据和工具才能执行。** 如果任何一条没完成，Phase 4 就卡住。

---

#### 管线 A：prep-info — 数据采集（原逻辑不变）

- Kanban 并行搜索（tavily / Exa / Firecrawl）
- 每条信息缺口 = 一个 Kanban task card
- 完成 → 统一筛选 → 整理数据原材料
- 输出给 Phase 4 的 research/execute 节点使用

#### 管线 B：prep-tools — 工具对接（8步任务执行流程）

详细流程见 `references/prep-tools-pipeline.md`。核心步骤：

1. **感知** — 用户的话是不是任务？
2. **拆解** — 复杂任务拆成子任务
3. **读能力矩阵** — 哪个 Profile 有什么工具？
   3b. **查 skill 注册中心** — 如果本地 Profile 没有合适工具，查统一 Skill 注册表
       （见 `D:/Obsidian/Note/统一Skill治理体系.md`）
       - 查本地已安装（hermes skills list + 注册中心MD）
       - find-skills（npx skills find <关键词>）
       - hermes skills search <关键词>
       - 各技能资源站（浏览器搜索）
       - 找到后判断安装位置（开发类→OpenCode / 业务类→Profile / Coze类→Coze）
       - 安装 → 更新注册中心MD
4. **决策路径** — delegate_task / Kanban / OpenCode / Coze / 混合
5. **找不到工具时** — 搜3个方向以上 → 能集成就集成 → 不能就问你要不要走Coze
6. **执行** — 用户零感知，全自动调度
7. **汇总** — 所有结果回到 default Profile
8. **更新** — 新增能力就更新 Profile能力矩阵.md

**搜索底线：** 禁止搜一次就说"没有"。先翻 Hermes 已有生态，再搜至少 3 个方向，搜不到才说没有并附上搜索记录。

### Phase 4: Executor + Auditor 双 Agent
Executor(v4-flash) 干活，Auditor(v4-pro) 判定。5条准则：
① /goal 达成 → done；② 无可执行节点 → done；③ 死局 → stop；④ 预算超限 → stop；⑤ → continue。
结果写入 execution-result.json，Phase 5 用来复盘。失败不是灾难，是素材。

### 7 维度复盘
①目标完成度(30%) / ②工具性能(15%) / ③CoT逻辑正确性(20%) / ④资源效率(10%) / ⑤用户满意度(15%) / ⑥信息值有效性(5%) / ⑦可改进点(5%)

## SOUL 配置
5 个总监 Profile 的 SOUL.md 已通过 agency-agents-zh 增强。详见 `references/agency-agents-soul-updates.md`。

## Kanban 增强规范

### 结果标准化

所有通过 Kanban 执行的任务，`result` 字段必须遵循以下 JSON 格式：

```json
{
  "status": "success | failed | partial",
  "summary": "简要描述执行结果（不超过500字）",
  "artifacts": [
    {"type": "feishu-table | file | url | image", "url": "..."},
    {"type": "file", "path": "C:/path/to/output"}
  ],
  "duration_seconds": 120,
  "errors": []
}
```

### 验证门禁

关键任务（代码/部署/数据采集/配置修改）完成后，Kanban Enhancer 会自动创建验证子任务，分配给 default Profile 进行人工复核。

### 工具亲和性检查

Kanban create/decompose 时，会自动检查分配的目标 Profile 是否拥有执行该任务所需的工具。如果存在不匹配，会记录到 kanban-enhanced 日志中。

### 失败升级

任务失败后自动按以下链升级：
1. 原 Profile 重试 2 次
2. 同级 Profile 接盘（研发↔测试，运营↔数据）
3. 升级到 default（人工介入）
4. 终极停止

> 详见 `devops/kanban-enhancer` skill

## 依赖

| 组件 | 用途 |
|:-----|:-----|
| 审批模型(deepseek-v4-pro) | Phase 1 Prompt Engineering + Phase 2c Grilling |
| Sequential Thinking MCP | Phase 1 预判信息缺口 + 补充第5份COT |
| MOA Mind-Daily | Phase 2 多模型COT产出 |
| 5总监Profile + 群聊(mrdpq9qfjiw2g3) | Phase 2b 争议讨论 |
| tavily / Exa / Firecrawl | Phase 3 外部信息采集(Kanban并行) |
| matplotlib | Phase 2/5 流程图生成 |
| Hermes Studio Kanban | Phase 3 并行搜索 + Phase 4 角色流水线。需配置 toolsets=["hermes-cli","kanban"] |
| kanban-enhancer | Phase 4 增强：工具亲和性检查 + 结果标准化 + 失败升级 + 验证门禁 |
| Loop Engine | 全部阶段递归 + advance() |
