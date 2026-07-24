---
name: skill-governance
description: >
  当用户需要了解或管理Skill治理体系时使用。
  覆盖：入口治理（description写边界）、手册治理（skill写成地图）、错误治理（纠错沉淀）。
  不要用于：具体某个skill的重写（走skill-description-rewriter）、安装新skill。
  触发词：skill治理、三条原则、入口治理、skill标准
tags:
  - skill-management
  - governance
  - cross-agent
  - registry
  - find-skills
triggers:
  - skill治理
  - 三条原则
  - 入口治理
  - skill标准

---

# Skill Governance — 统一 Skill 治理体系

## 概述

跨 Agent（Hermes / OpenCode / Coze / Claude Code / Codex）、跨 Profile 的 skill 全生命周期管理。包括查找、安装、治理、沉淀、复用。

## 三层架构

```
注册中心（Obsidian MD） → 索引所有skill的元信息（名称/描述/安装位置/来源）
安装分发（多CLI）       → 按类型装到对应Agent（开发类→OpenCode，业务类→Profile，Coze类→Coze）
进化治理（SkillClaw）   → 自动提炼/去重/进化（后台daemon）
```

## 搜索阶梯（2026-07-21 更新）

### 搜索顺序

```
任务需要某个能力
  │
  ① 本地已安装（hermes skills list + 注册中心MD）
  ② 并行搜索（三个独立工具，同时执行，互不依赖）
     ├── find-skills → npx skills find <关键词>
     │    使用 skills.sh 的 CLI 搜索工具
     ├── hermes skills search → hermes skills search <关键词>
     │    使用 Hermes 内置的 skills.sh 搜索接口
     └── 两者都通过各自的 CLI 工具搜索 skills.sh 数据库
  ③ 各技能资源站（浏览器，modelscope/虾评/clawhub/skillhub，无公开API）
  ④ 广义网络搜索（web_search "API/CLI/MCP for X"）
  ⑤ 都找不到 → 确认无结果，附搜索记录
```

### 三个工具的关系（重要）

**三者是独立的关系，不是谁搜谁。**

| 工具 | 本质 | 命令 | 搜索范围 |
|------|------|------|---------|
| **find-skills** | 已安装的 Hermes skill | `npx skills find <关键词>` | skills.sh 数据库（通过 CLI 工具） |
| **hermes skills search** | Hermes 内置 CLI 命令 | `hermes skills search <关键词>` | skills.sh 数据库（通过 Hermes 接口） |
| **skills.sh** | 网站 | 浏览器访问 | skills.sh 市场（Web 界面） |

**不是说 find-skills 去搜 skills.sh 这个网站，** 而是 find-skills 和 hermes skills search 都通过各自的 CLI 工具访问 skills.sh 的数据库。skills.sh 网站本身是 Web 界面。三者并行执行可以提高命中率，因为接口不同、返回结果可能有差异。

### 搜索关键词规则

`[能力领域] + [动作]`，先用英文搜（skills.sh以英文为主），搜不到换中文，先宽后窄。

### 执行质量原则（重要）

> **不要给我省token，认真做，好好做。** 宁可多用token确保质量，也不要为了省token而偷工减料。
> 搜索工具时搜不到就换方向继续搜，搜3个方向以上才说"没有"。
> 重写description时每条都要有边界、排除场景、触发词，缺一不可。

### 各技能资源站的搜索工具可用性

| 网站 | 有无CLI/API搜索工具 | 搜索方式 | 技能数 |
|------|-------------------|---------|--------|
| **skills.sh** | ✅ `npx skills find` + `hermes skills search` | CLI，可被Agent直接调用 | 94万+ |
| **xiaping.coze.com**（虾评） | ❌ 无公开API/CLI | 仅Web搜索框+分类筛选 | 2251 |
| **clawhub.ai/skills**（OpenClaw） | ❌ 无公开API/CLI | 仅Web搜索框+分类筛选 | 大量 |
| **modelscope.cn/skills**（阿里魔搭） | ❌ 无公开API/CLI | 仅Web搜索框 | 7.6万+ |
| **skillhub.club**（聚合排行） | ❌ 无公开API/CLI | 仅Web页面 | 聚合 |

**结论：只有 skills.sh 有可被Agent直接调用的CLI搜索工具。** 其他网站都只能通过浏览器手动搜索。

### 用户指定 Skill 名称但找不到

当用户说"安装一个叫 XXX 的 skill"但精确匹配不到时：
1. 搜根词/部分匹配（如 "true-damand" → "demand"）
2. 跨 skills.sh + ClawHub 两个市场搜
3. 列出最接近的 alternatives 问用户
4. 详细流程见 `references/skill-resources.md` → "用户指定 Skill 名称但找不到时的处理流程"

### 搜索关键词规则

`[能力领域] + [动作]`，先用英文搜，搜不到换中文。

## 安装位置规则

| Skill 类型 | 安装到 | 命令 |
|-----------|--------|------|
| 开发类（React/Next.js/API设计等） | OpenCode + engineering-director | `npx skills add <包名>` |
| 业务操作类（发邮件/数据分析等） | 对应 Hermes Profile | `hermes skills install <标识符>` |
| Coze 插件类 | Coze | `coze plugin install` |
| 通用类 | default Profile | `hermes skills install <标识符>` |
| 系统维护类 | helper (SRE) Profile | `hermes skills install <标识符>` |

Hermes 可通过 terminal 工具为任何有 CLI 的 Agent 安装 skill（OpenCode / Coze / Claude Code / Codex）。

## Skill Governance 三条原则

### 原则1：入口治理 — description 写边界，不写能力

```
❌ 坏：description: "用于内容创作"
✅ 好：description: "当用户提供技术主题、目标受众和传播平台，要求生成技术博客初稿时使用。
                  不要用于短视频脚本、营销海报和客服话术。"
```

**自测标准：** 只看名字和描述，不看正文，也能判断什么时候该用它。

### 原则2：手册治理 — skill 写成地图，不是百科全书

每个 skill 必须包含四类信息：

1. **输入条件** — 用户必须提供哪些信息，任务才能开始？
2. **执行步骤** — 第一步做什么？第二步做什么？第三步做什么？
3. **判断分支** — 缺资料怎么办？目标不清怎么办？输出平台不同怎么办？
4. **失败处理** — 什么时候停下来问用户？什么时候不能继续编？什么时候切换工具？

**自测标准：** skill 文档读完后应该能直接进入执行，而不是只让读者懂更多。

### 原则3：错误治理 — 每次纠错沉淀回 skill

```
agent 犯错后，复盘三件事：
1. 错误来源：入口判断错了？调用了不该调用的 skill？
2. 手册缺口：步骤缺失？分支缺失？失败处理没写？
3. 规则沉淀：把这次错误转成下次能执行的规则
   → 更新 skill description（加边界）
   → 更新 skill 步骤（加分支处理）
   → 更新 skill 失败处理（加错误场景）
```

**自测标准：** agent 可以犯错，但最好只让他犯一次同样的错。

## 统一注册中心

安装在别处的 skill 只记索引到 Obsidian MD，不记完整内容。

### 注册格式

```
## skill名称
- description：一句话描述（带边界）
- 安装位置：OpenCode / Coze / Hermes:engineering-director
- 来源：skills.sh / modelscope / 虾评 / 自建
- 安装命令：npx skills add xxx / hermes skills install xxx
- 用途标签：开发 / 测试 / 数据分析 / 内容创作
- 使用记录：上次使用时间 + 效果评估
- 踩坑记录：常见错误 + 已沉淀的规则
```

## 技能资源站

| 网站 | 说明 | 链接 |
|------|------|------|
| **skills.sh** | 全球最大 Agent Skills 市场（Vercel），94万+技能 | https://www.skills.sh/ |
| **skillhub.club** | 中文 Skill 排行榜 | https://skillhub.club/hot |
| **xiaping.coze.com** | 虾评，Coze 官方社区，2248个技能 | https://xiaping.coze.com/ |
| **clawhub.ai/skills** | OpenClaw 官方 Skill 站 | https://clawhub.ai/skills |
| **modelscope.cn/skills** | 阿里魔搭社区 Skills 中心，7.6万+技能 | https://modelscope.cn/skills |

## 保证下次复用的机制

```
task 来了
  → 读注册中心 MD → 发现 skill 已安装 → 调用
  → 执行过程中出错
  → 复盘三件事（错误来源/手册缺口/规则沉淀）
  → 更新 skill description
  → 更新注册中心 MD（踩坑记录）
  → 下次 task 来了 → 自动避开已知坑
```

## 自动同步脚本

### SkillClaw → Obsidian 注册中心同步

`D:/hermes-data/skillclaw_obsidian_sync.py` — 自动对比 SkillClaw 管理的 skill 与 Obsidian 注册中心 MD 的差异，保持两端口径一致。

| 模式 | 命令 | 说明 |
|------|------|------|
| 预览 | `python skillclaw_obsidian_sync.py` | 对比差异，不写文件 |
| 同步 | `python skillclaw_obsidian_sync.py --apply` | 对比后更新注册中心 MD |
| 监听 | `python skillclaw_obsidian_sync.py --watch` | 每5分钟自动检查同步 |

### 飞书多维表格审计表

`https://swi2cdl2nbg.feishu.cn/base/NoZVbWlR4ahbQesNGFKcStw9n5d` — 212条skill审计记录，7个字段（分类/当前描述/有边界/触发词/触发概率/需要重写/状态）。用于在表格中审批/标记重写进度。

## 踩坑记录

### Windows 下 npx skills find 乱码

在 Windows git-bash/MSYS 终端中，`npx skills find` 的输出可能包含乱码/二进制数据，exit_code=1 但实际可能成功。原因：终端编码问题。

**解决：** 优先使用浏览器搜索技能市场（skills.sh / ClawHub），比 CLI 更可靠。详见 `references/skill-resources.md` → 踩坑记录。

## 集成点

- **orchestrator-loop** → Phase 3 prep-tools 中调用 skill 查找流程
- **helper-opencode-integration** → 系统维护时可调用 skill 安装/治理
- **Profile能力矩阵.md** → 统一 Skill 注册表章节
- **统一Skill治理体系.md** → 完整文档 (Obsidian)

## 参考文档

- `D:/Obsidian/Note/统一Skill治理体系.md` — 完整治理方案
- `D:/Obsidian/Note/Profile能力矩阵.md` — 统一 Skill 注册表
- `skills/devops/helper-opencode-integration/SKILL.md` — SRE 对接 OpenCode
- `skills/orchestrator-loop/SKILL.md` — Phase 3 prep-tools 集成
- `~/.hermes/prefill.json` — 5条铁律，提升 skill 调用率（每次对话自动注入）
- `references/skill-website-search-tools.md` — 各技能资源站搜索工具可用性审计（skills.sh有CLI，其他无）
- `references/cross-agent-portable-manifest.md` — 跨 Agent 可移植 Skill 依赖清单模式（来自 personal-agent-foundation 分析，2026-07-22）
- `references/enterprise-governance-extension.md` — 企业级 Skill 治理扩展（单机→跨部门，2026-07-22）