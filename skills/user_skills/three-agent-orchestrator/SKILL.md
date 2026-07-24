---
name: three-agent-orchestrator
title: 三Agent编排：Hermes + OpenCode + Coze
description: >
  当用户需要跨Agent协作完成任务时使用。
  
  决策规则：
  - 开发任务（写代码、造工具、重构）→ 调 OpenCode（走 `dev-pipeline-cli`，CLI 模式）
  - 已预置在 Coze 中的自动化工作流 → 调 Coze（走 `coze-workflow-api`，纯管道模式）
  - 部署/查日志/改配置等基础操作 → Hermes 自己用 terminal 搞定
  - 简单的对话/查询/分析 → Hermes 自己处理
  
  不要用于：简单的单步操作、不需要跨Agent协作的任务。
  
  触发词：三Agent、跨Agent协作、调OpenCode、调Coze、帮我写代码然后部署、开发并执行
version: 4
triggers:
  - 三Agent
  - 跨Agent协作
  - 调OpenCode
  - 调Coze
  - 帮我写代码然后部署
  - 开发并执行
tags:
  - three-agent-orchestr
  - three

---

# 三Agent编排架构

## 三个 Agent 的定位

| Agent | 角色 | 做什么 | 不做什么 | 通讯方式 |
|-------|------|--------|---------|---------|
| **Hermes** | 🧠 大脑 | 决策、协调、简单操作（terminal） | 不写复杂代码、不做已预置在 Coze 的自动化 | CLI |
| **OpenCode** | ✋ 码农 | 写代码、造工具、重构（TDD） | 不决策、不部署、不做 Coze 的活 | CLI |
| **Coze** | 🔌 外挂插件箱 | 执行已预置的自动化工作流 | 不写代码、不决策 | HTTP API（纯管道） |

## 决策门（Decision Gate）

```
用户说需求
  │
  ▼
判断任务类型：
  │
  ├── 写代码/造工具/重构/开发功能 → 调 OpenCode
  │     └─ terminal("opencode '{需求}'")
  │
  ├── 已预置在 Coze 中的自动化工作流 → 调 Coze API
  │     └─ coze-workflow-api skill（纯管道，Hermes 不加任何推理）
  │
  ├── 部署到服务器 / 查日志 / 改配置 / 跑脚本
  │     └─ Hermes 自己用 terminal 搞定
  │
  └── 其他 → Hermes 自己处理
```

## Coze 的使用原则（重要）

Coze 的定位是**外挂插件箱**，不是第二个"大脑"：

1. **纯管道模式**：调用 Coze 工作流 API 拿到数据直接返回，Hermes 不加任何推理和思考
2. **不替代 skill**：用户已经在 Coze 里做了完整的思考设计，不需要 Hermes 再分析
3. **插件生态**：Coze 有很多插件（API 未知、数据库未知），Hermes 无法复刻，只能沿用
4. **省 token**：复杂逻辑在 Coze 跑，比在 Hermes 写复杂的 skill 省 token

```
用户："用扣子执行 XXX"
  → 命中 coze-workflow-api skill
  → 调 Coze 工作流 API（stream_run）
  → 实时返回 SSE 事件（Message / Interrupt / Done）
  → 遇到 Interrupt → 暂停问用户 → 用户回复后 Resume
  → 遇到 Done → 直接输出结果，结束
  → Hermes 全程不加任何推理
```

## OpenCode 的使用原则

1. **CLI 模式**：通过 terminal 调用，不走 ACP 协议
2. **TDD 模式**：先写测试用例，再调 OpenCode 写实现
3. **文件系统握手**：OpenCode 写文件，Hermes 读文件验证

## 已安装的环境

- **OpenCode** v1.17.9: `C:\Users\Admin\AppData\Roaming\npm\opencode.cmd`
- **Coze CLI** v0.3.4: `C:\Users\Admin\AppData\Roaming\npm\coze.cmd`
- **Coze API Token**: 已配置在 coze-workflow-api skill 中
- **Coze 已登录**：用户 moon85（麦兜），PAT 永不过期