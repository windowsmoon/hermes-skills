---
name: helper-opencode-integration
description: >
  当helper(SRE) Profile需要调用OpenCode ACP进行本地代码修复时使用。
  用于：Hermes系统故障排查、配置文件修复、代码修改、日志分析。
  不要用于：日常开发任务（走engineering-director）、非Hermes系统的维护。
  触发词：修复Hermes、排查故障、修代码、helper帮我修一下
tags:
  - sre
  - opencode
  - acp
  - maintenance
  - helper
triggers:
  - 修复Hermes
  - 排查故障
  - 修代码
  - helper帮我修一下

---

# SRE Helper × OpenCode ACP 集成

## 概述

helper profile 通过 OpenCode ACP（Agent Client Protocol）协议调用外部编码 Agent，实现 Hermes 系统的本地代码修复和配置维护。

## 工具链条

```
helper profile（SRE）
  │
  ├── OpenCode ACP (localhost:3100)
  │     HTTP POST /api/chat/completions
  │     JSON: {"model": "deepseek-v4-flash", "messages": [...], "tools": [...]}
  │
  ├── Hermes 内置工具
  │     read_file / write_file / patch / terminal / execute_code
  │
  ├── Hermes Studio MCP
  │     hermes-studio-api → 查询会话/工作流/看板
  │     hermes-studio-use → 查看可用模型/配置
  │
  └── Kanban
        创建任务 / 完成任务 / 查看看板状态
```

## 数据管线

### 故障排查管线
```
用户报告问题
  → 读取 Hermes 日志（各 profile 的 logs/ 目录）
  → 读取配置文件（~/.hermes/config.yaml）
  → 定位根因
  → 调用 OpenCode ACP 修复代码
  → 验证修复（运行测试 / 语法检查）
  → 保存为 skill（skill_manage create）
  → 更新 memory（记录故障特征）
```

### 配置修改管线
```
用户请求修改配置
  → 读取当前配置文件
  → 备份原文件（.bak）
  → 修改配置
  → 验证 YAML/JSON 格式
  → 重启服务（如需要）
  → 验证生效
```

## OpenCode ACP 调用方式

### 1. 启动 ACP Server（后台运行）
```bash
opencode acp --port 3100 --print-logs
```

### 2. 通过 HTTP 调用
```bash
curl -X POST http://localhost:3100/api/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "修复这个文件中的 bug"}]
  }'
```

### 3. 通过 Hermes terminal 工具调用
```python
from hermes_tools import terminal
result = terminal("curl -X POST http://localhost:3100/api/chat/completions ...")
```

## 常见故障场景处理

### 场景1：Hermes 更新后配置不兼容
1. 读取新版本 changelog/release notes
2. 对比新旧配置差异
3. 调用 OpenCode 修改配置
4. 验证配置格式
5. 保存为 skill

### 场景2：Kanban 数据库损坏
1. 检查 `~/.hermes/kanban/` 目录
2. 运行诊断：`hermes kanban diagnostics`
3. 如有备份，恢复最近的备份
4. 保存修复步骤为 skill

### 场景3：某个 Profile 无法启动
1. 读取该 profile 的 `logs/` 目录下的错误日志
2. 检查 `config.yaml` 格式
3. 检查 `.env` 配置
4. 修复后验证
5. 保存为 skill

## 故障恢复分级（2026-07-20 更新）

### 第一级：Hermes 正常运行时

通过 Kanban 或 delegate_task 派发修复任务给 helper profile：

```
你（default Profile）遇到问题
  │
  ├── Kanban create task --assignee helper
  │     → helper 自动接收任务
  │     → 读日志 → 定位根因 → 调 OpenCode ACP 修复 → 验证 → 保存 skill
  │     → 完成任务，result 写回看板
  │
  └── 或 delegate_task 给 helper SubAgent
        → 结果实时回传当前对话
```

### 第二级：Hermes 完全瘫痪（兜底）

当 Hermes Studio 无法打开或无法发送消息时，**helper profile 也失效了**。此时走 OpenCode TUI 兜底：

```
你打开一个终端（Windows Terminal / cmd / PowerShell / git-bash）
  │
  ├── opencode D:\\Program\\Hermes\\ Studio
  │     ↓
  │     OpenCode TUI 启动（终端界面，完全独立）
  │     ↓
  │     在 TUI 里跟 AI 对话：
  │       "读取 Hermes 的日志"
  │       "检查 config.yaml 格式"
  │       "修复这个 bug"
  │       "重启 Hermes"
  │
  └── 修好后，重新打开 Hermes Studio
```

### OpenCode 的三种模式（兜底场景使用）

| 模式 | 命令 | 依赖 Hermes？ | 场景 |
|------|------|--------------|------|
| **TUI（终端界面）** | `opencode [项目目录]` | ❌ 完全独立 | 兜底修复 Hermes |
| **ACP Server** | `opencode acp --port 3100` | ❌ 完全独立 | Hermes 正常时通过工具调用 |
| **Attach** | `opencode attach http://localhost:4096` | ❌ 完全独立 | 连到已运行的 OpenCode 服务 |

> 完整故障恢复手册见 `D:/Obsidian/Note/Hermes故障恢复.md`

## 知识沉淀规范

每次修复后必须执行：
1. `skill_manage action=create name=fix-<问题关键词>` → 保存修复步骤
2. `memory action=add target=memory content="<故障特征: 修复方案>"` → 记录特征
3. 在 Kanban 任务中更新 result 字段，写明根因和修复过程

## 关联系统

- **skill-governance**（`skills/devops/skill-governance/`）— 跨 Agent 统一 Skill 治理体系，用于 skill 查找、安装、治理、沉淀
- **orchestrator-loop**（`skills/orchestrator-loop/`）— Phase 3 prep-tools 中集成 skill 查找流程
- **统一Skill治理体系.md**（`D:/Obsidian/Note/统一Skill治理体系.md`）— 完整治理方案文档