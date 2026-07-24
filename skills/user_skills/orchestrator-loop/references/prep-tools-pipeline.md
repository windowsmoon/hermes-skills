# prep-tools 管线 — 8步任务执行流程

> 2026-07-21 更新：搜索优先级调整，第2层改为 find-skills + hermes skills search 并行。
> 与 prep-info（数据采集）并行执行，互不依赖。

## 8步流程总览

```
你说话
  ↓
① 感知 → 是不是任务？不是→正常对话
  ↓
② 拆解 → 复杂任务拆子任务
  ↓
③ 读能力矩阵 → 哪个Profile有什么工具？
  ↓
④ 决策 → delegate_task / Kanban / OpenCode / Coze / 混合
  ↓
⑤ 找不到工具 → 搜3个方向以上 → 能集成就集成 → 不能就问你要不要走Coze
  ↓
⑥ 执行 → 你零感知，全自动调度
  ↓
⑦ 汇总 → 所有结果回到default Profile
  ↓
⑧ 更新 → 新增能力就更新Profile能力矩阵.md
```

## 第1步：感知 — 是不是任务？

| 用户说 | 判为任务？ | 原因 |
|--------|-----------|------|
| "帮我分析/开发/写/做一个 XXX" | ✅ 是 | 有明确产出需求 |
| "帮我审查/评估/建议 XXX" | ✅ 是 | 有明确行动需求 |
| "XXX 是什么？" | ❌ 否 | 知识问答 |
| "你怎么看 XXX？" | ❌ 否 | 观点讨论 |

**判断标准：** 用户是否明确要求我**产出某个结果或执行某个行动**？

## 第2步：拆解

1. 明确任务目标：用户要什么产出？
2. 识别任务类型：分析/开发/操作/混合？
3. 评估复杂度：简单（单步完成）还是复杂（多步/跨部门）？
4. 拆分子任务：复杂任务拆成多个可独立执行的子任务

## 第3步：读 Profile 能力矩阵

执行复杂任务前，先读 `D:/Obsidian/Note/Profile能力矩阵.md`，判断：

1. 哪个 Profile 有合适的 skill/工具？
2. 哪个 Profile 有相关的记忆/经验？
3. 哪个 Profile 的 SOUL 最适合这个任务？

### 第3b步：查 skill 注册中心（跨 Agent 统一查找）

如果本地 Profile 没有合适工具，进入**统一 skill 查找流程**（详见 `skills/devops/skill-governance/SKILL.md`）：

```
本地没有合适工具
  │
  ① 查统一 Skill 注册表（Profile能力矩阵.md → 统一Skill注册表）
  │ 有 → 调对应的 Agent/Profile 执行
  │ 没有 → 进入搜索流程
  │
  ② 搜索流程（第2层并行，都搜skills.sh市场94万+技能）
  │ ├── find-skills: npx skills find <关键词>
  │ ├── hermes skills search <关键词>（并行执行）
  │ ├── 各技能资源站（skills.sh / 虾评 / 魔搭 / ClawHub，无公开API，需浏览器）
  │ └── 都找不到 → 确认无结果
  │
  ③ 找到 skill → 判断安装位置
  │ ├── 开发类 → OpenCode + engineering-director
  │ ├── 业务操作类 → 对应 Profile
  │ ├── Coze 插件类 → Coze
  │ └── 通用类 → default Profile
  │
  ④ 安装 → 更新注册中心 MD → 执行任务
```

**搜索关键词规则：** `[能力领域] + [动作]`，先用英文搜，搜不到换中文。

**安装后必须：** 更新 `Profile能力矩阵.md` 的「统一Skill注册表」，记录名称/描述/安装位置/来源。

**skill 治理标准：** 每次新增或修改 skill，对照三条原则：
- 入口治理：description 写边界，不写能力
- 手册治理：skill 写成地图，不是百科全书
- 错误治理：每次纠错沉淀回 skill

**判断依据：**

| 任务类型 | 最合适的 Profile | 原因 |
|---------|----------------|------|
| 产品需求/市场分析 | product-manager | 68个 pm-skills + 产品视角 SOUL |
| 架构设计/代码编写 | engineering-director | 技术架构 SOUL + TDD规则 + OpenCode |
| 测试用例/代码审查 | qa-director | 测试覆盖 SOUL |
| 部署/运维/监控 | operations-director | 运维 SOUL |
| 数据分析/报表 | bigdata-director | 44个 Excel skill + 数据 SOUL |
| Hermes 系统维护 | helper (SRE) | 故障排查 SOUL + OpenCode |
| 能自己干的 | default (我自己) | delegate_task 派 SubAgent |

## 第4步：决策路径

```
任务拆解后，每个子任务走哪条路？

  ├── default Profile 自己能干？
  │     → delegate_task 派 SubAgent（当前Session内）
  │     结果实时回传，可审计
  │
  ├── 其他 Profile 更合适？
  │     → Kanban 后台调度（自动）
  │     我自动创建任务 → 自动派发 → 自动收集结果
  │     你零感知，只有出错才报你
  │
  ├── 需要写工程代码（独立项目/迭代开发）？
  │     → 派给 engineering-director（Kanban）
  │       engineering-director 内部调 OpenCode ACP
  │
  ├── 需要调外部 API/执行操作？
  │     → 看能不能在 Hermes 内直接对接
  │       ├── 能 → 集成后走 delegate_task
  │       └── 不能 → 走 Coze（问你是否同意）
  │
  └── 以上组合（复杂跨部门任务）
        → 我后台 Kanban 调度多个 Profile
          → 各 Profile 内部自选工具
          → 结果自动汇总回你
```

**路径对比表：**

| 路径 | 你感知到 | 适合场景 | 审计能力 |
|------|---------|---------|---------|
| **delegate_task** | 结果直接回你（实时） | 当前 Session 能完成的单步任务 | ✅ 可搜到完整对话 |
| **Kanban** | 最终结果回你（零感知） | 跨 Profile 协作、异步执行 | ❌ 只看结果，看不到其他 Profile 对话 |
| **OpenCode ACP** | 通过 Profile 间接执行 | 写工程代码、修复本地代码 | 通过 engineering-director 审计 |
| **Coze** | 问你同意后才走 | 调用外部 API/工作流 | 通过 Coze 平台审计 |
| **Hermes-OpenCode-Coze** | 问你同意后才走 | 需要独立技术栈的完整项目 | 三方独立 |

## 第5步：找不到工具时（prep-tools 核心流程）

当能力矩阵 MD 里没有任何 Profile 有合适的工具时：

```
需要某个工具但 MD 里没有
  │
  ├── 1. 先翻 Hermes 已有生态
  │     ├── 已有的 skills（~/AppData/Local/hermes/skills/）
  │     ├── 已有的 MCP 服务器
  │     ├── 已有的 CLI 工具
  │     └── 已有的 API Provider
  │
  ├── 2. 如果 Hermes 生态没有 → 上网搜索
  │     ├── web_search "API for X"
  │     ├── web_search "CLI for X"
  │     ├── web_search "MCP server for X"
  │     ├── web_search "X 工具"（中文）
  │     └── 至少搜索 3 个不同方向
  │
  ├── 3. 如果还找不到 → 搜技能市场
  │     ├── hermes skills search <关键词>（搜索 skills.sh 等市场）
  │     ├── 如果找到现成 skill → hermes skills install → 更新能力矩阵 → 执行
  │     └── 如果没找到 →
  │
  ├── 4. 找到工具后
  │     ├── 能在 Hermes 直接对接？（CLI/API/MCP）
  │     │   ├── 能 → 安装配置 → 更新能力矩阵 MD → 执行任务
  │     │   └── 不能 → 看 Coze 能不能做？
  │     │       ├── 能 → 问你："这个要用 Hermes-OpenCode-Coze 路径吗？"
  │     │       │     你同意 → 通过 ACP/Coze CLI 对接
  │     │       └── 不能 → 报错："找不到合适的工具，已搜索了 X、Y、Z 方向"
  │
  └── 5. 搜索失败 → 附上搜索记录 → 问用户有没有其他方向
```

**搜索底线（纠正过往问题）：**
- ❌ **禁止**搜一次就说"没有"
- ✅ **必须**先检查 Hermes 已有生态，再搜外部
- ✅ **必须**至少搜 3 个不同方向的关键词
- ✅ **必须**附上搜索记录，方便用户补充方向

## 第6步：执行（用户零感知）

- 你只跟 default Profile 说话
- 所有调度、协调、执行都是我的事
- 你零感知中间过程，只有结果和报错
- 出问题时才中断流程报给你

## 第7步：汇总

所有子任务完成后：
1. 收集所有结果（Kanban 结果 + delegate_task 结果 + ACP 信息）
2. 整合成完整报告
3. 汇总到 default Profile 对话中给用户
4. 只有出错才中断流程报给用户

## 第8步：更新能力矩阵

每次任务执行过程中：
- ✅ 新增了 skill → 更新 Profile能力矩阵.md
- ✅ 安装了 CLI 工具 → 更新 Profile能力矩阵.md
- ✅ 配置了 MCP 服务 → 更新 Profile能力矩阵.md
- ✅ 对接了新 API → 更新 Profile能力矩阵.md
- ✅ 修复了 Hermes 故障 → helper 更新记忆 + 创建 skill
- ✅ 发现了新的踩坑经验 → 更新对应 Profile 的记忆

## 示例：完整路径

```
你: "帮我做用户登录模块"
  ↓
① 感知：是任务
  ↓
② 拆解：写代码 + 写测试 + 部署
  ↓
③ 读能力矩阵：
   engineering-director 有 TDD SOUL + OpenCode → 适合写代码
   qa-director 有测试 SOUL → 适合写测试
   operations-director 有运维 SOUL → 适合部署
  ↓
④ 决策：
   Kanban 派 engineering-director → 写代码（内部调 OpenCode）
   Kanban 派 qa-director → 写测试
   Kanban 派 operations-director → 部署
  ↓
  并行：
    prep-info → 搜索数据原材料
    prep-tools → 对接工具、更新能力矩阵
  ↓
⑤ 执行（你零感知）：
   Dispatcher 自动派 Worker → 各 Profile 自动执行
  ↓
⑥ 汇总：
   我回收所有结果 → 整合报告
  ↓
⑦ 给你：
   报告 + 代码路径 + 部署地址
   （只有出错才报你）
```