# 五阶段编排架构 — 参考文档

## 架构概述

这是用户设计的多 Agent 任务编排模式，运行在 Loop Engine 之上。适用于需要多模型协作、SMART 验证、可视化反馈的复杂任务。

## 数据流全景

```
用户任务
  │
  ▼
Phase 1: 任务触发 ──── [审批模型: deepseek-v4-pro]
  │  ├─ Prompt Engineering（优化用户原始指令）
  │  ├─ Sequential Thinking MCP（结构化分解）
  │  └─ SMART 验证 → 《任务定义文档》(→ Checker 验收标准)
  │  [human_gate]
  ▼
Phase 2: 规划 ──────── [默认模型: orchestrator]
  │  ├─ MOA Mind-Daily（4份 COT，含 OKR/方法论/成功率/风险/时长）
  │  ├─ 比对: 矛盾点 + 共同风险 + 方法科学性
  │  ├─ 打分排序 + matplotlib PNG 流程图
  │  └─ 选路径 或 群聊讨论（5位总监profile）
  │  [human_gate]
  ▼
Phase 3: 执行准备 ──── [默认模型]
  │  ├─ tavily 搜索各步骤所需信息
  │  ├─ 筛选 /goal 相关内容 → 注入 COT 作为节点
  │  └─ 匹配工具 → 工具选择表
  │  [human_gate]
  ▼
Phase 4: 执行 ──────── [子Agent: deepseek-v4-flash]
  │  ├─ Loop Engineering 递归（状态文件驱动）
  │  ├─ 严格按流程图步骤执行（Maker → Checker）
  │  ├─ 并行原则: 请示和执行不串行阻塞
  │  └─ 授权点/异常 → 暂停等待用户
  ▼
Phase 5: 反馈 ──────── [默认模型]
     ├─ matplotlib PNG 流程图（200dpi, 绿蓝黄红编码）
     ├─ 8维度评分 + 归因分析
     ├─ 回滚确认 / 决策点预判 / 优化建议
     └─ 全部存入 Obsidian Note
```

## 用户设计的完整流程

### Phase 1: 任务触发阶段

**参与者**: 默认 profile 的默认模型 → 委托审批辅助模型

1. 默认模型接到任务指令后，委托 **审批辅助模型**（`custom:183399/deepseek-v4-pro`）做首轮分析
2. 审批模型以 **Prompt Engineer** 角色优化用户提示词
3. 调用 **Sequential Thinking MCP** 服务做结构化分解和目标具体化
4. 用 **SMART 框架** 验证：
   - Specific（具体）
   - Measurable（可衡量）
   - Achievable（可实现）
   - Relevant（相关）
   - Time-bound（有时限）
5. 输出以 `/goal` 为中心的 **《任务定义文档》**，此文档是后续 checker 的验收标准
6. **human_gate**: 用户确认文档无误

### Phase 2: 规划阶段

**参与者**: 默认模型（orchestrator）+ MOA Mind-Daily

#### 第 1 步：MOA 多角度 COT

- 默认模型接到《任务定义文档》后，委托 **MOA "Mind-Daily"** 预设（4 模型并行）
- 各模型出具包含以下维度的 COT：
  - 围绕 /goal 的 OKR 式分解
  - 任务方法思想
  - 任务成功率预估
  - 任务失败风险点预判
  - 任务预计时长
  - 人工干预/审批点

#### 第 2 步：COT 方案选择

- 默认模型**比对**各 COT：
  1. 矛盾点
  2. 共同风险点
  3. 方法科学性（哪个方法最合理而非"邪修"）
- **输出**:
  1. 各 COT 的方法思想和核心关键点简述 + 文档位置
  2. **matplotlib PNG 流程图**，标注路径选择理由和可能风险
  3. 各 COT 打分排序（成功率高+时间短+人工干预少 得分最高）
- **human_gate**: 询问用户使用哪条路径
  - 如果用户说"先讨论一下" → **自动发起群聊 session**（5位总监 profile）
  - 群聊结果 + 矛盾点高亮 → 你审批

### Phase 3: 执行准备阶段

**参与者**: 默认模型

#### 第 1 步：信息与上下文清单

- 沿用户选定的 COT 路径，列出每个步骤所需信息
- 委托 subAgent 用 **tavily 搜索** 获取信息
- 筛选与 /goal 相关的内容 → 注入到 COT 步骤信息中 → 成为流程图节点
- 排除不相关信息

#### 第 2 步：工具与资源匹配

- 针对每个信息需求匹配可用工具
- 生成**工具选择表**
- **human_gate**: 用户确认

### Phase 4: 执行阶段

**参与者**: 默认模型 → 子Agent（deepseek-v4-flash）

- 默认模型将任务拆分为子任务
- 委托 **deepseek-v4-flash** 子Agent 执行
- 严格按流程图执行（Loop Engineering 模式）
- **并行原则**: 请示和执行不串行阻塞，能边跑边问的不先问再跑
- 遇到 **授权点/决策点/异常** 必须暂停请示

### Phase 5: 执行反馈阶段

**参与者**: 默认模型

#### 第 1 步：执行流程汇报

**matplotlib PNG 流程图**，200dpi：
- 颜色编码：绿=开始/结束，蓝=执行步骤，黄菱形=决策判断，红虚线=失败/回退
- 节点包含：主标题 + 数据值小字
- 底部附图例

#### 第 2 步：复盘与改进

1. **自评打分**: 8 个维度逐项给分 + 解释
2. **归因分析**: 具体到某个数据/某步决策，用流程图标记症结
3. **回滚确认**: 问用户是否回到 Phase 2 重规划
4. **预判决策点**: 告诉用户后续哪个步骤需要做什么决策
5. **优化复盘**: 如果再做一次，会怎样优化 COT、执行流程中的数据采纳、工具、关键决策

## 已配置的基础设施

| 组件 | 配置详情 |
|:----|:--------|
| 审批辅助模型 | `custom:183399/deepseek-v4-pro`, timeout=30s |
| MOA Mind-Daily | reference_models: Qwen3.7+/DeepSeek-V4-Pro/GLM-5.2/MiniMax-M3, aggregator: GPT-5.5 |
| Sequential Thinking MCP | command: `npx -y @modelcontextprotocol/server-sequential-thinking` |
| matplotlib | v3.11.0, Agg backend, installed under Hermes Python |
| tavily | api_key configured in web_providers |
| 群聊房间 | roomId: mrdpq9qfjiw2g3, inviteCode: arch-review |
| 5 个 profile | product-manager(dsv4-pro), engineering-director(qwen3.7+), qa-director(glm-5.2), operations-director(mm-m3), bigdata-director(dsv4-pro) |
| Loop Engine | scripts/loop_engine.py |

## 使用注意

- 此模式**不适合简单任务**（单步 Loop 即可）
- MOA + 群聊会增加耗时，适合重大决策场景
- matplotlib 用 `FancyBboxPatch` 做圆角矩形（`corner_radius` 在 matplotlib 3.11 已移除）
- Sequential Thinking MCP 需要重启 Hermes 才会生效
- 子Agent用 deepseek-v4-flash（便宜模型）省成本
