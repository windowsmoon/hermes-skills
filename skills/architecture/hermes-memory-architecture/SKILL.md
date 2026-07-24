---
name: hermes-memory-architecture
description: |
  Hermes 记忆系统架构与迁移指南。覆盖 hindsight 向量记忆、MEMORY.md/USER.md 文件记忆、
  Obsidian RAG 知识库三层的关系、迁移时的备份恢复策略、以及记忆分类标签规范。
  触发词：记忆系统、记忆迁移、记忆备份、hindsight配置、记忆分类
version: "1.0.0"
triggers:
  - 记忆系统
  - 记忆迁移
  - 记忆备份
  - hindsight配置
  - 记忆分类
  - MEMORY.md
  - 记忆架构
tags:
  - memory
  - hindsight
  - architecture
  - migration
---

# Hermes 记忆系统架构

## 三层记忆体系

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: hindsight 向量记忆（语义搜索）                      │
│  Provider: hindsight (local_embedded)                        │
│  Bank: hermes（所有 profile 共享）                            │
│  引擎: 硅基流动 embedding API                                │
│  作用: 语义检索，相似度匹配                                   │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 文件记忆（文本备份）                                │
│  MEMORY.md (53KB) — Agent 的持久记忆                        │
│  USER.md (10KB)   — 用户画像                                │
│  位置: ~/.hermes/memories/                                   │
│  作用: 文本备份，不依赖向量数据库                              │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Obsidian RAG（外部知识库）                          │
│  D:/Obsidian/Note/ + FAISS 向量索引                          │
│  更新: 每日 9AM 自动索引                                      │
│  作用: 长期知识沉淀，跨 Agent 迁移                            │
└─────────────────────────────────────────────────────────────┘
```

## 记忆分类标签规范（2026-07-22 更新）

MEMORY.md 中的每条记忆使用以下标签分类：

| 标签 | 含义 | 示例 |
|:----|:----|:----|
| `[user]` | 用户偏好、风格、要求 | 用户偏好选择题而非填空题 |
| `[knowledge]` | 已验证的技术事实 | 豹剪 API Key: sk-xxx |
| `[experience]` | 踩坑教训、Bug 经验 | delegate_task 子Agent 经常不返回 |
| `[rule]` | 提炼的通用原则 | 零成本优先、不要盲目重试 |
| `[task]` | 已完成/进行中的状态 | orchestrator-loop 已搭建完成 |

## 迁移清单

换电脑/换 Agent 时，需要迁移的内容：

| 优先级 | 内容 | 位置 | 迁移方式 |
|:------|:----|:----|:--------|
| P0 | MEMORY.md | ~/.hermes/memories/ | 直接拷贝 |
| P0 | USER.md | ~/.hermes/memories/ | 直接拷贝 |
| P0 | hindsight config | ~/.hermes/hindsight/config.json | 直接拷贝 |
| P1 | 所有 skills | ~/.hermes/skills/ | 整个目录打包 |
| P1 | Obsidian Note | D:/Obsidian/Note/ | 同步或拷贝 |
| P2 | Cron jobs | ~/.hermes/cron/jobs.json | 直接拷贝 |
| P2 | Profile SOUL.md | ~/.hermes/profiles/*/SOUL.md | 直接拷贝 |

## 与 Agent 平台的解耦

### 不能直接迁移的部分
- **hindsight 向量数据库** — 绑定 Hermes 运行时，其他 Agent 无法读取
- **硅基流动 API Key** — 需要在新环境重新配置

### 可以跨平台迁移的部分
- **MEMORY.md / USER.md** — 纯文本，任何 Agent 都能导入
- **Obsidian Note** — Markdown 文件，任何笔记软件都能读
- **SKILL.md** — 需要转换格式，但知识内容可复用

### 换到 Codex/Coze 时的策略
1. 把 MEMORY.md 内容作为初始上下文注入
2. 把 Obsidian Note 作为知识库上传
3. 把核心 skill 的逻辑转写成目标平台格式

## 每周反思 Cron（2026-07-22 配置）

每周日 20:00 自动执行：
1. 读取 MEMORY.md 中 `[experience]` 标签的条目
2. 提炼通用规则
3. 写入 `[rule]` 标签
4. 报告给用户

## 已知问题

### memory 工具的 10,000 字符限制
- **这是 Hermes 内置工具的硬编码限制，与 Hindsight 无关**
- `memory` 工具用于读写 MEMORY.md/USER.md 文件，上限 10,000 字符
- Hindsight 是独立的向量记忆后端，不受此限制
- 当 memory 满时，需要批量清理旧条目腾出空间

### Hindsight 运行时依赖（2026-07-22 发现）
**问题链：** 删除旧版 Hermes 运行时 → Hindsight 被删 → 当前 Python 缺 stdlib → 无法重装

**根因：** Hermes 0.18.2 的 Python 是精简版，缺少 `encodings`、`importlib`、`DLLs/` 等核心模块

**修复步骤：**
```python
# 1. 从 0.19.0 拷贝 stdlib 到 0.18.2
# 2. 安装 hindsight-client 到 0.19.0 Python
# 3. 设置 PYTHONHOME 指向 0.19.0 目录
```

**验证命令：**
```bash
python -c "import hindsight_client; print('OK')"
```

### hindsight daemon 不会自动启动
- local_external 模式需要手动启动 daemon
- 建议用 local_embedded 模式（自动管理）
