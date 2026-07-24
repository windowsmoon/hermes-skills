---
name: enterprise-agent-deployment
description: >
  当用户需要将 Agent 基础设施（Hermes / Codex / WorkBuddy）部署到企业级多部门组织时使用。
  覆盖：GLOBAL/ 共享底座模板、部门级 Profile 隔离、Token 预算管理、跨部门 Skill 治理、三阶段实施路线。
  不要用于：单机 Heremes 配置、产品生命周期管理（走 product-lifecycle-management）、
  Agent 技能治理（走 skill-governance）、跨 Agent 协议集成（走 A2A 调研）。
  触发词：企业级部署、跨部门 Agent、部门隔离、Token 管理、先做后说、统一底座、多部门协作
tags:
  - enterprise
  - deployment
  - governance
  - department-isolation
  - token-management
  - hermes-base
  - adoption-strategy
triggers:
  - 企业级部署
  - 跨部门 Agent
  - 部门隔离
  - Token 管理
  - 先做后说
  - 统一底座
  - 多部门协作
---

# Enterprise Agent Deployment — 企业级统一 Agent 底座

## 概述

在组织中跨部门部署 Agent 基础设施（Hermes / Codex / WorkBuddy），实现：
- **规则统一**：所有部门共享同一份 GLOBAL 上下文
- **数据隔离**：部门间 Profile 互不可见，数据不互通
- **成本可控**：Token 预算归部门，超额自动告警
- **技能共享**：通用 Skill 全局可用，部门专用 Skill 仅本部门可见

## 跟 personal-agent-foundation 的关系

| 维度 | PAF（跨客户端基座） | 本方案（企业级部署） |
|------|-------------------|-------------------|
| 目标 | 跨客户端统一上下文 | 跨部门统一治理 |
| 核心问题 | 换 Agent/设备不丢人设 | 多部门安全协作 + Token 管控 |
| 新增能力 | — | 部门隔离、Token 预算、成员管理、审计 |
| 关系 | 基础层 | 继承 PAF 的 GLOBAL 模板理念，增加企业级治理层 |

## 跟 A2A 协议的关系

| 维度 | A2A（网络协议） | 本方案（企业级部署） |
|------|---------------|-------------------|
| 解决的问题 | 多个 Agent 实时协同干活 | 多部门统一规则 + 安全隔离 |
| 技术栈 | HTTP REST + JSON + SSE | 文件系统 + Hermes Profile |
| Agent 关系 | Client-Server 紧密耦合 | 松散耦合，各自独立 |
| 互补性 | 上层实时协作 | 下层统一规则 |

## 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                    企业级统一 Hermes 底座                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                    GLOBAL/ 共享底座                      │   │
│  │  (全局上下文 · Skill 依赖 · 账号路由 · 知识库 · 项目)     │   │
│  └──────────────────────┬─────────────────────────────────┘   │
│                         │ 只读挂载                             │
│          ┌──────────────┼──────────────┐                     │
│          │              │              │                     │
│  ┌───────▼───────┐ ┌───▼───────┐ ┌───▼───────┐             │
│  │  运营部        │ │  研发部    │ │  人事部    │  ...       │
│  │  Profile 隔离  │ │  Profile  │ │  Profile  │             │
│  │  部门 Skill    │ │  隔离      │ │  隔离      │             │
│  │  Token 预算    │ │  Token     │ │  Token     │             │
│  │  部门记忆      │ │  预算      │ │  预算      │             │
│  └───────────────┘ └───────────┘ └───────────┘             │
└──────────────────────────────────────────────────────────────┘
```

## 目录结构

```
D:\hermes-data\enterprise\
├── ENTERPRISE_README.md          ← 架构总览
├── ROADMAP.md                    ← 三阶段路线图
├── GLOBAL\                        ← 共享底座（只读挂载）
│   ├── GLOBAL_CONTEXT.md          ← 全局上下文
│   ├── SKILL_DEPENDENCIES.md      ← 技能依赖清单
│   ├── DEPARTMENTS.md             ← 部门注册表
│   ├── TOKEN_MANAGEMENT.md        ← Token 预算与用量
│   ├── LARK_PROFILES.md           ← 飞书多账号路由
│   ├── GITHUB_ACCOUNTS.md         ← GitHub 多账号
│   ├── OBSIDIAN_LINK.md           ← 知识库连接
│   ├── KNOWLEDGE_BASES.md         ← 多知识库索引
│   ├── PROJECTS.md                ← 项目注册中心
│   └── .agents\skills\            ← 跨部门通用 Skill
├── DEPARTMENTS\                    ← 部门隔离层
│   └── {department-name}\
│       ├── profile\               ← 独立的 Hermes Profile
│       ├── skills\                ← 部门专用 Skill
│       ├── memory\                ← 部门记忆
│       ├── token.yaml             ← 部门 Token 预算
│       └── README.md              ← 部门说明
└── SCRIPTS\                        ← 管理脚本
    ├── init_department.py          ← 创建新部门
    └── token_usage_report.py       ← 用量统计
```

## 核心设计原则

### 1. Profile 隔离
每个部门使用独立的 Hermes Profile，数据完全不互通。Profile 切换通过 `hermes config set --profile` 完成。

### 2. 共享只读
GLOBAL/ 目录对所有部门只读，变更由管理员控制。各部门不得写入 GLOBAL/。

### 3. Skill 分级
- **全局 Skill**：`GLOBAL/.agents/skills/` — 所有部门自动继承
- **部门 Skill**：`DEPARTMENTS/{部门名}/skills/` — 仅本部门可见
- **外部 Skill**：通过 `SKILL_DEPENDENCIES.md` 记录来源

### 4. Token 预算制
每个部门有月度 Token 预算上限，用量达到 80% 告警，100% 暂停非关键任务，120% 全部暂停。

## 实施路线（三阶段）

### Phase 1：先做后说（1-2天）
**目标：** 把自己的 Agent 环境整理成可复用的模板，用结果说话。

1. 创建企业底座目录结构
2. 编写 GLOBAL/ 模板文件
3. 把现有 Skill 依赖整理成 SKILL_DEPENDENCIES.md
4. 把飞书/GitHub 账号整理成对应 MD 文件
5. 跑通"从模板恢复环境"的流程

**关键：** 不提案，不推广，先做出来。发哥看到后说"这个不错"即可。

### Phase 2：部门试点（1-3个月）
**目标：** 等有人主动来找你，而不是你去推。

1. 用 `init_department.py` 创建部门 Profile
2. 部门主管设置 token 预算
3. 部门成员各自有独立 Profile，共享部门 Skill
4. 输出《部门 Agent 运营报告》

**话术：** "你们部门要搞的话，需要确定一个主管来管 token 预算，我来帮你们搭。"

### Phase 3：横向扩展（3-6个月）
**目标：** 形成公司级 Agent 治理规范。

1. 多部门注册到 DEPARTMENTS.md
2. 全局 Skill 市场（部门间共享已验证的 Skill）
3. 网关层（多实例负载均衡，可选）
4. 审计日志
5. 管理员培训

**门槛：** 至少 2 个部门主动接入，有明确的 Token 成本分摊机制。

## 政治策略（关键）

### 为什么不能直接提案

| 角色 | 原因 | 解决方案 |
|------|------|---------|
| 发哥（Hermes） | 没看到"建服务器"对他有什么好处 | 先做后说，让他自己看到价值 |
| 阿展（Codex） | 担心权限不可控 | 部门隔离，互不接触，解决他的顾虑 |

### 正确做法

1. **绝对不要第三次提案** — 已经失败了两次，第三次只会让你更难堪
2. **先做后说** — 自己跑通，让发哥看到价值，他自己来找你
3. **部门隔离是卖点不是缺点** — 阿展反对的是"混在一起"，部门隔离正解决他的顾虑
4. **不主动推，等人来问** — 把自己定位成"帮忙搭"，不是"主导推行"

### 判别标准

- Phase 1 成功：发哥看到后说"这个不错"
- Phase 2 成功：有人问"这个我能用吗？帮我也搞一个"
- Phase 3 成功：公司有明确的 Agent 管理和成本分摊机制

## 启动命令

```powershell
# 1. 进入企业底座目录
cd D:\hermes-data\enterprise

# 2. 查看当前部门注册状态
notepad GLOBAL\DEPARTMENTS.md

# 3. 初始化一个新部门
python SCRIPTS\init_department.py --name 运营部 --manager 张三 --monthly-budget 5000000

# 4. 查看 Token 用量
python SCRIPTS\token_usage_report.py
python SCRIPTS\token_usage_report.py --all
```

## 安全原则

1. **Profile 隔离**：各部门独立 Profile，数据不互通
2. **共享只读**：GLOBAL/ 目录只读，禁止写入
3. **最小权限**：部门主管管预算，不跨部门查看
4. **审计可追溯**：所有操作记录在 Hermes 会话中
5. **数据主权**：所有数据存在本地，不依赖云端

## 参考文档

- `references/adoption-strategy.md` — 先做后说政治策略详解
- `references/comparison-decision-framework.md` — PAF / A2A / agents-hive 方案对比决策框架
- `references/architecture-overview.md` — 架构详细设计
- `D:/Obsidian/Note/Profile能力矩阵.md` — 企业底座章节
