# 跨 Agent 可移植 Skill 依赖清单模式

> 来源：DongLiStudio/personal-agent-foundation 的分析记录（2026-07-22）
> 该项目的核心思路是：用文件系统做单一事实来源，不同 Agent 读同一份文件，换 Agent 时重新跑安装流程恢复同样的行为。

## 问题背景

不同 Agent 宿主（Hermes / Codex / WorkBuddy / Claude Code）各有自己的 Skill 格式、会话存储方式和认证机制。用户一旦换 Agent、换项目或换设备，长期规则、项目经验、身份路由、工具授权和协作方式就很难继续复用。

## 方案对比

| 维度 | Hermes 现有做法 | personal-agent-foundation 做法 |
|------|----------------|-------------------------------|
| Skill 管理 | `hermes skills install` + SkillClaw 治理 + 注册中心 MD | `SKILL_DEPENDENCIES.md` 清单 + `.agents/skills/` 自维护目录 |
| 跨 Agent 同步 | 无（Hermes 独有格式） | 同一份 GLOBAL 目录，各 Agent 读取 |
| 迁移方式 | 灾难恢复备份（3层备份脚本） | 重新跑一遍 `install-agent-scaffold` 安装流程 |
| 上下文 | Prefill + 记忆 + 会话 DB | `GLOBAL_CONTEXT.md` 纯文本文件 |
| 多账号路由 | 各 Profile 独立配置 | `LARK_PROFILES.md` + `GITHUB_ACCOUNTS.md` 统一文件 |
| 知识库链接 | Obsidian RAG（FAISS 向量索引） | `OBSIDIAN_LINK.md` 结构理解 + 入口记录 |

## SKILL_DEPENDENCIES.md 清单模式

### 记录原则

**需要记录：**
- 自维护的全局 Skill（存在 `.agents/skills/` 目录下，跨 Agent 通用）
- 主动安装的外部 Skill（来自 GitHub / skills.sh / NPM 等）
- 需要特定安装命令的 Skill（如 `npx skills add`、`hermes skills install`、`npm install -g`）
- 有版本依赖或特定 commit 引用的 Skill

**不需要记录：**
- 默认预装 Skill、系统 Skill、插件自动附带的 Skill
- 插件缓存 Skill、运行时缓存和临时目录
- 宿主 Agent 自带的原生功能

### 一条记录的格式

```markdown
### skill-name
- 来源：`https://github.com/org/repo/tree/commit-hash/skills/skill-name`
- 安装方式：`npx skills add skill-name` 或 `hermes skills install skill-name`
- 用途：一句话说明
- 依赖：需要哪些外部工具/CLI
```

### 跟 SkillClaw 治理体系的关系

| 维度 | SkillClaw 治理体系 | SKILL_DEPENDENCIES.md |
|------|-------------------|----------------------|
| 定位 | 日常 skill 全生命周期管理 | 跨 Agent 迁移时的依赖恢复清单 |
| 粒度 | 每个 skill 的完整元数据（描述/边界/触发词/踩坑） | 只记录来源 + 安装方式 |
| 自动同步 | ✅ SkillClaw → Obsidian 同步脚本 | 手动维护（安装时写入） |
| 跨 Agent | 仅当前 Hermes Profile | 文件级共享，任何 Agent 可读 |

**结论：两者互补。** SkillClaw 管日常治理，SKILL_DEPENDENCIES.md 管灾备迁移。

## GLOBAL 工作区结构

```
AGENT_ROOT/
├── GLOBAL/                    # 全局资产空间（版本控制）
│   ├── GLOBAL_CONTEXT.md      # 全局上下文（工作区模型/核心路径/协作规则）
│   ├── SKILL_DEPENDENCIES.md  # Skill 依赖清单
│   ├── LARK_PROFILES.md       # 飞书多账号路由
│   ├── GITHUB_ACCOUNTS.md     # GitHub 多账号路由
│   ├── OBSIDIAN_LINK.md       # 知识库链接
│   ├── PROJECTS.md            # 项目索引
│   ├── SCHEDULE_PREFERENCES.md# 日程偏好
│   ├── README.md              # 入口说明
│   └── .agents/skills/        # 自维护全局 Skill 目录
│       ├── init-agent-project/
│       ├── github-cli/
│       ├── feishu-profile/
│       ├── feishu-task/
│       ├── decide-next-action/
│       ├── personal-schedule-planner/
│       ├── record-skill-dependency/
│       ├── visual-iteration-workflow/
│       ├── align-agent-projects-with-global/
│       └── migrate-agent-root/
├── 项目A/                     # 具体项目（与 GLOBAL 同级）
└── 项目B/
```

### 核心原则

1. **GLOBAL 不放具体项目任务** — 只放全局规则、账号路由、Skill 索引
2. **项目在 AGENT_ROOT 下与 GLOBAL 同级** — 每个项目独立目录，独立上下文
3. **GLOBAL 内容注入每个 Agent 的 System Prompt** — 新会话不从头开始
4. **账号信息只存"标识"不存"凭据"** — OAuth token / API Key 各 Agent 各自管理

## 对你的 Hermes 环境的启示

你的环境在功能完备度上已经远超这个项目。但以下 3 个概念值得借鉴：

1. **SKILL_DEPENDENCIES.md 作为灾备清单** — 你的 SkillClaw 治理体系已经管了日常，但缺一个"跨 Agent 恢复时该装什么"的清单。每个 Profile 可以加一个 `SKILL_DEPENDENCIES.md`
2. **GLOBAL_CONTEXT.md 的结构化上下文模板** — 你的 Prefill 5 条铁律 + 任务执行规则 8 步流程已经覆盖，但可以借鉴"工作区模型""核心路径""Skill 源头模型"等结构来优化全局上下文
3. **多账号路由的统一文件管理** — 你的飞书多 Profile 和 GitHub CLI 各自独立，可以统一记在一个 `账号路由表.md` 里

## 参考资料

- 项目仓库：https://github.com/DongLiStudio/personal-agent-foundation
- 安装 Skill：`skills/install-agent-scaffold/SKILL.md`
- 模板清单：`template-manifest.json`
- GLOBAL 模板：`template/GLOBAL/`