---
name: product-lifecycle-management
description: >
  当用户需要管理产品全生命周期（4阶段18步）时使用。
  覆盖：战略洞察→定义聚焦→落地执行→上市增长，状态机驱动。
  不要用于：单次产品分析（走pm-skills中的对应skill）、开发任务跟踪。
  触发词：产品生命周期、PLM、产品管理、产品规划、从0到1
tags:
  - product-management
  - lifecycle
  - pm-skills
  - state-machine
  - workflow
triggers:
  - 产品生命周期
  - PLM
  - 产品管理
  - 产品规划
  - 从0到1

---

# 产品生命周期管理 — 可执行状态机

## 触发方式

### 从默认 profile 路由到 PM 角色

你在默认 profile 中说以下任意一句，我**自动扮演产品经理角色**执行流水线：

> "让产品经理做一个【产品名】的产品规划"
> "让产品经理调研一下【领域】"
> "让PM写一个【功能】的PRD"
> "产品经理，帮我做【产品名】的生命周期管理"

**不需要你切 profile，不需要你手动转任务**。你说"让产品经理做XXX"，我就在当前对话中承担 PM 角色，加载状态机开始执行。

### 直接触发（PM 场景下）

当本技能已加载时，也可以直接说：

> "帮我设计一个新功能"
> "启动产品生命周期"
> "做产品调研"
> "写PRD"
> "新项目立项"

## 架构原则

**不依赖 Profile 切换。** 主 Agent（当前 session）负责：
- 意图理解 + 任务拆分
- 通过 `delegate_task` 派发给 subagent 执行具体工作
- 接收结果并汇总交付

Profile（engineering-director, qa-director 等）是独立的 Session，不支持跨 Profile 工具调用和上下文共享。正确的多角色协作方式是 `delegate_task`，**不是** Profile 切换。

### 三种编排方式（按复杂度选择）

| 复杂度 | 方式 | 适用场景 |
|--------|------|---------|
| 低（2-5步） | **对话中直接编排** — 我手动走每一步，问你确认 | 一次性流程，不需要复用 |
| 中（6-20步） | **Orchestrator 脚本** — `plm_orchestrator.py` 状态机 | 可复用的多步骤流水线 |
| 高（DAG 图） | **Hermes Studio Web UI 工作流** — API创建，画布可视化 | 条件分支/并行节点/审批节点，需长期复用 |

**Web UI 工作流创建方式：** 通过 `hermes_studio_use_workflow_create` API 创建带节点+连线的可视化工作流。节点类型为 `agentNode`，需配置 label、model、provider、prompt。创建后可在 Web UI 画布拖拽修改。

subagent 通过 `context` 字段接收背景信息，结果自动回传。

## 文件清单

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 本文件 — 触发指令 + 执行流程 |
| `~/AppData/Local/hermes/scripts/plm_orchestrator.py` | Python 状态机引擎（管理4阶段18步） |
| `~/.product-lifecycle-state.json` | 跨 session 持久化状态文件 |

## 执行前提

运行 orchestrator 需要 Hermes Bundled Python:

```bash
python ~/AppData/Local/hermes/scripts/plm_orchestrator.py <command>
```

状态机脚本位于 `~/AppData/Local/hermes/scripts/plm_orchestrator.py`。状态文件写入 `~/.product-lifecycle-state.json`，跨 session 持久化。

## 状态机命令

所有命令通过 orchestrator 执行：

| 用户说 | 等价命令 | 效果 |
|--------|---------|------|
| "开始做一个新产品【产品名】" | `start <产品名>` | 初始化状态机，定位到第1步 |
| "下一步" / "继续" | `next` | 当前步标记完成，推进到下一步 |
| "现在到哪了" | `status` | 显示当前阶段/步骤/完成度 |
| "回退一步" / "上一步" | `rollback` | 回退到上一步 |
| "跳到【步骤名】" | `step <step_id>` | 跳转到指定步骤 |
| "全部阶段" / "列出来" | `list` | 显示全部18步及对应技能 |
| "重置" / "重新开始" | `reset` | 清空状态机 |
| "产出物:xxx" | `set-output <key> <value>` | 记录阶段产出物 |

## 执行流程

### Stage 0：启动新产品
用户提出需求 → 我执行:
```bash
python ~/AppData/Local/hermes/scripts/plm_orchestrator.py start "<产品名>"
```
→ 状态机初始化，定位到 **p1s1 产品愿景**

### Stage 1：战略洞察期（产品未立项）
**核心目标：找方向、选战场、判生死。不做具体功能，只回答"我们值不值得做"。**

| 步 | 任务 | 技能 | 产出 |
|----|------|------|------|
| p1s1 | 产品愿景（Vision） | product-vision | Mission Statement |
| p1s2 | SWOT分析 | swot-analysis | 优劣势威胁矩阵 |
| p1s3 | 市场细分 | market-segments | 目标细分市场 |
| p1s4 | 竞品分析 | competitor-analysis | 竞品定位空白点 |
| p1s5 | 用户调研 | analyze-feature-requests | 未满足痛点清单 |
| p1s6 | 用户画像 | user-personas | 典型Persona |

**退出条件：** 定位通过内部及核心用户访谈验证，具备强差异化

### Stage 2：定义聚焦期（产品立项）
**核心目标：确定唯一的核心指标和差异化锚点。决定产品的灵魂。**

| 步 | 任务 | 技能 | 产出 |
|----|------|------|------|
| p2s1 | 战略画布 | (通用PM方法论) | 价值曲线图 |
| p2s2 | 定位 | positioning-ideas | 核心差异化口号 |
| p2s3 | 北极星指标 | north-star-metric | 长期健康指标 |
| p2s4 | 机会树 | opportunity-solution-tree | 可拆解指标+杠杆 |
| p2s5 | 功能优先级 | prioritize-features | MVP Backlog |

**退出条件：** 北极星指标和定位通过团队共识，MVP范围锁定

### Stage 3：落地执行期（从需求到上线）
**核心目标：拆解任务、保障质量、合规避险。从抽象战略转为具体工单。**

| 步 | 任务 | 技能 | 产出 |
|----|------|------|------|
| p3s1 | 写PRD | create-prd | 8段式PRD文档 |
| p3s2 | 用户故事 | user-stories | 开发任务拆分 |
| p3s3 | Sprint规划 | sprint-plan | 迭代计划 |
| p3s4 | 测试场景 | test-scenarios | 验收用例集 |
| p3s5 | NDA/隐私终审 | draft-nda | 合规文件 |

**阶段3完成后 → delegate_task → engineering-director（技术评估）+ qa-director（测试评审）**

**退出条件：** 核心链路测试通过率100%，法务NDA/隐私政策签署完毕

### Stage 4：上市增长期（上线后）
**核心目标：把产品推出去，并形成自增长闭环。**

| 步 | 任务 | 技能 | 产出 |
|----|------|------|------|
| p4s1 | GTM策略 | gtm-strategy | 定价/渠道/推广计划 |
| p4s2 | 增长飞轮 | growth-loops | 留存自传播正循环 |

**退出条件：** 增长飞轮无需外部干预自行加速，LTV > 3×CAC

### 三环迭代逻辑

产品管理不是线性流程，而是**三个闭环的螺旋迭代**：

```
🧠 底层基建层（贯穿全生命周期）
  产品愿景 → SWOT → 竞品分析 → 用户调研 → 用户画像
  NDA/隐私政策 ← 合规红线卡点

🎯 战略探索环（季度/年度迭代）
  市场细分 → 战略画布 → 定位 → 北极星指标 → 机会树 → 功能优先级
  ↕ 战略环输出给执行环 ↕

⚙️ 执行交付环（双周Sprint迭代）
  写PRD & 用户故事 → Sprint规划 → 测试场景验收 → 版本上线
  ↕ 上线反馈修正战略 ↕

🚀 增长放大环（上线后持续）
  GTM策略 → 增长飞轮 → 市场/用户行为数据
  ↕ 数据驱动下一轮迭代 ↕
```

### 三大生存铁律
1. **北极星不是定完就死的** — 增长期数据回流发现指标定错，必须回滚修正北极星 → 机会树 → 优先级
2. **隐私合规是硬卡点** — Sprint中涉及新数据采集但NDA未覆盖，必须阻断执行环
3. **增长飞轮是检验真理的唯一标准** — 飞轮不转，90%是定位问题，必须带新数据重走0→1探索

## 18步速查表

| ID | 步骤 | 技能 | 产出 |
|----|------|------|------|
| p1s1 | 产品愿景 | product-vision | Mission Statement |
| p1s2 | SWOT分析 | swot-analysis | 优劣势威胁矩阵 |
| p1s3 | 市场细分 | market-segments | 目标细分市场 |
| p1s4 | 竞品分析 | competitor-analysis | 竞品定位空白点 |
| p1s5 | 用户调研 | analyze-feature-requests | 未满足痛点清单 |
| p1s6 | 用户画像 | user-personas | 典型Persona |
| p2s1 | 战略画布 | (通用方法论) | 价值曲线图 |
| p2s2 | 定位 | positioning-ideas | 核心差异化口号 |
| p2s3 | 北极星指标 | north-star-metric | 长期健康指标 |
| p2s4 | 机会树 | opportunity-solution-tree | 可拆解指标+杠杆 |
| p2s5 | 功能优先级 | prioritize-features | MVP Backlog |
| p3s1 | 写PRD | create-prd | 8段式PRD文档 |
| p3s2 | 用户故事 | user-stories | 开发任务拆分 |
| p3s3 | Sprint规划 | sprint-plan | 迭代计划 |
| p3s4 | 测试场景 | test-scenarios | 验收用例集 |
| p3s5 | NDA/隐私终审 | draft-nda | 合规文件 |
| p4s1 | GTM策略 | gtm-strategy | 定价/渠道/推广计划 |
| p4s2 | 增长飞轮 | growth-loops | 留存自传播正循环 |

## 产出物归档

每步完成后，产出物：
1. 记录到状态机：`set-output <step_id> <描述>`
2. 实际文档保存到 `D:\\Obsidian\\Note\\_product\\{产品名}\\`
3. 全部完成后汇总到 Obsidian

## 全技能触发词速查表

本表覆盖所有已安装 skill 的触发方式。分类为三类：
- **系统/外部** — Hermes 预装或第三方 source 安装（不可编辑）
- **用户自定义** — 你要求我创建的 skill
- **pm-skills 子技能** — 从 GitHub 安装的 68 个 PM 框架技能

> 详细分类清单见 `references/all-skills-trigger-matrix.md`（本 skill 目录下）
> 架构决策模式（Orchestrator vs Web UI 工作流 vs 对话编排）见 `references/architecture-patterns.md`
> 参数呈现原则（用户偏好：选择题格式，不做填空题）见 `references/parameter-presentation.md` 和 `references/user-preference-parameter-presentation.md`

| 触发词 / 你说 | 路由到的 Skill | 分类 | 说明 |
|---------------|--------------|------|------|
| `让产品经理做...` | product-lifecycle-management | 用户自定义 | 启动产品生命周期4阶段状态机 |
| `任务：...` / `开始任务` | orchestrator-loop | 用户自定义 | 多阶段任务编排框架 |
| `帮我开发一个...` | acp-dev-pipeline | 用户自定义 | ACP 协议调度 OpenCode 编码 |
| `帮我优化提示词：...` | prompt-optimizer | 用户自定义 | LLM API 优化提示词 |
| `处理这个目录` / `解析文档` | document-parsing | 用户自定义 | MinerU 批量转 Obsidian |
| `心虫评估：...` / `心虫分享：...` | heartflow (外部) | 系统/外部 | 逐字稿深度复盘与认知分析 |
| `帮我发一封邮件` | agently-mail | 用户自定义 | 通过 Agent QQ 邮箱发件 |
| `我最近收到了哪些邮件？` | agently-mail | 用户自定义 | 收件箱查询 |
| `在小红书搜一下...` | xhs-cli | 用户自定义 | 小红书笔记搜索 |
| `帮我把这些剪一下` | video-use | 用户自定义 | AI 视频剪辑 |
| `帮我生成一张图...` | apikey-image-gen | 系统/外部 | 文生图 API |
| `hyperframes` / `remotion` | hyperframes / remotion | 系统/外部 | AI 视频创建 |
| `用扣子运行...` / `用扣子做...` | coze-workflow-automation | 系统/外部 | 扣子工作流执行 |
| `在小红书搜一下...` (旧) | xhs-cli | 用户自定义 | CLI 模式搜索 |
| `帮我生成...` (LibTV) | libtv-cli / libtv-feishu-auto | 系统/外部 | LibTV 画布操作 |
| `飞书...` / `lark...` | feishu-cli / feishu-multimodal-params | 系统/外部 | 飞书 API 操作 |

### 心虫工具使用注意（避免误用）

心虫（HeartFlow）的认知分析工具主要分析**引擎自身状态**，而非用户本人：
- `heartflow_think` — 对输入文本做意图分类和路由决策，不输出用户心理画像
- `heartflow_agent_psychology` — 分析 AI 引擎的 7 维认知心理状态（认知负荷/目标冲突/价值内化等），不是分析用户
- `heartflow_emotion` — PAD 情绪分析（Pleasure-Arousal-Dominance），输入短文本时准确率低
- `heartflow_persona_stance_detector` — 返回引擎场域状态（U/D/A/H），不适合作外部用户分析

**正确的用法：** 心虫适合做对话文本的意图分类和决策路由预处理。如果用户要求分析"自己"的认知水平或性格，应优先基于 User Profile 中的详细画像 + 对话历史自己分析，心虫作为辅助验证。

## 三个硬规则（必须遵守）

1. **永远先 status 再看当前步骤**，不要猜当前走到哪了
2. **每步完成后必须等用户确认**才能 next，不能自动连跑
3. **阶段3的 delegate 是必须执行的**，不能跳过

## 关键设计决策（避免重蹈覆辙）

1. **状态机必须先于文档存在** — 多步流程的 skill 必须有一个可执行的状态机脚本（orchestrator.py），SKILL.md 只是告诉 agent 怎么用它。不能先写文档再「以后补」。
2. **持久化状态是唯一的真实来源** — 不依赖对话上下文记忆当前位置。`~/.product-lifecycle-state.json` 在任何 session 中恢复。
3. **每步一个子技能引用** — 每步指向一个 `pm-skills/{name}` 技能。agent 在步骤执行时先加载该技能获取领域知识，再做产出。
4. **门禁在 agent 侧，不在脚本侧** — orchestrator 只管状态流转。每步是否确认完成、产出是否合格，由 agent 判断（等用户说"继续"才 next）。
5. **委托是硬性阶段出口** — 阶段3完成后必须 delegate 给 engineering-director + qa-director，不能跳过或假装做过。


## 多Agent路由规则

当状态机进入特定步骤时，由我（当前 session）自动路由到对应 Agent：

| 触发条件 | 路由目标 | 动作 |
|---------|---------|------|
| 用户说"让产品经理做XXX" | 我扮演PM | 在当前对话加载本SKILL + 启动状态机 |
| 阶段3完成（写PRD之后） | delegate_task → **engineering-director** | 发PRD给工程总监评估技术方案 |
| 阶段3完成（测试场景之后） | delegate_task → **qa-director** | 发测试场景给QA总监评审 |
| 涉及数据处理 | delegate_task → **bigdata-director** | 发数据需求给大数据总监 |
| 阶段4启动前 | delegate_task → **operations-director** | 发GTM计划给运营总监评审 |

所有 delegate_task 通过 `delegate_task(goal=..., context=...)` 执行，返回结果合并到当前阶段产出中。

### 实现方式

```python
# 示例：委托给 engineering-director
delegate_task(
    goal="评估这个PRD的技术方案可行性",
    context=f"产品: {product_name}\nPRD内容: {prd_content}\n请输出技术方案评估报告",
    role="leaf"
)
```
