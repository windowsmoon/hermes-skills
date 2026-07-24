---
name: dev-pipeline-cli
title: 开发流水线 - OpenCode CLI 模式（TDD）
description: >
  当用户要求开发完整的程序/功能/模块时使用。
  通过 OpenCode CLI 完成代码编写，不走 ACP 协议。
  
  TDD模式：先写测试用例 → 调 OpenCode 写实现 → 运行测试通过后交付。
  
  不要用于：简单的代码片段修改（直接在对话中改）、部署/运维操作（走 Coze 或 operations-director）。
  
  触发词：帮我开发、帮我写一个程序、开发一个功能、写一个XXX、实现一个、帮我造一个工具
tags:
  - development
  - opencode
  - cli
  - tdd
  - pipeline
triggers:
  - 帮我开发
  - 帮我写一个程序
  - 开发一个功能
  - 写一个XXX
  - 实现一个
  - 帮我造一个工具

---

# 开发流水线 (Dev Pipeline) — OpenCode CLI + TDD 模式

## 核心原则

**通过 OpenCode CLI 写代码，通过 CLI 标准输出拿结果，不走 ACP 协议。**

```
Hermes（编排器）
  │
  ├─ terminal("opencode '写一个XXX'", pty=true) → OpenCode 写代码
  │     ↓ stdout + 文件系统 ← 返回结果
  │
  └─ 验证 → 测试 → delegate_task QA → 交付
```

## 架构

```
你: "帮我开发一个XXX"
  ↓
Hermes：TDD 编排 + 任务分解
  ├── 需求分析 → 技术方案 → 任务拆解
  ├── 步骤1：先写测试用例（Hermes 自己写，因为测试用例是轻量级的）
  ├── 步骤2：调 OpenCode 写实现代码
  │     └─ terminal("opencode '根据以下测试用例编写实现代码...'", pty=true, timeout=300)
  ├── 步骤3：验证测试是否通过
  ├── 步骤4：delegate_task → QA subagent → 代码审查
  └── 步骤5：交付
```

## 工作流程

### 第1步：需求分析与技术方案
- 分析需求，明确功能边界
- 确定技术栈和测试框架
- 输出：技术方案，确定文件路径

### 第2步：写测试用例
- Hermes 自己写测试文件（测试用例轻量，不需要调 OpenCode）
- 测试用例覆盖：正常路径、边界条件、异常处理
- 输出：`tests/test_xxx.py`

### 第3步：调 OpenCode 写实现代码（核心改动）
```bash
# 不再用 execute_code 自己写，而是调 OpenCode
opencode "根据 /path/to/tests/test_xxx.py 中的测试用例，编写实现代码。
         要求：遵循 TDD 流程，实现代码必须通过所有测试用例才算完成。
         不要生成多余功能，刚好通过测试即可。
         实现文件放在 /path/to/src/xxx.py"
```

- 通过 terminal(pty=true) 调用 OpenCode
- OpenCode 写完后，Hermes 读取文件验证
- 如果测试没通过，再次调 OpenCode 修复

### 第4步：测试验证
- 运行测试套件，确认全部通过
- 如果失败，返回第3步

### 第5步：质量检测
- delegate_task → QA subagent
- 检查：测试覆盖率、代码质量、安全审计

### 第6步：交付
- 输出测试报告 + 代码文件清单

## 关键命令

```bash
# 调 OpenCode 写代码（CLI 模式，不走 ACP）
opencode "写一个Python内存监控脚本，输出到 /tmp/monitor.py"

# 调 OpenCode 修复问题
opencode "修复 /tmp/monitor.py 中的bug：xxx"

# 查看 OpenCode 版本
opencode --version
```

## 环境

| 组件 | 状态 |
|------|------|
| OpenCode CLI | ✅ v1.17.9 (C:\Users\Admin\AppData\Roaming\npm\opencode.cmd) |
| 通讯方式 | ✅ CLI 标准输出 + 文件系统，不走 ACP |
| 测试框架 | 按项目语言选择（pytest / jest / unittest） |

## 参考文档

| 文件 | 说明 |
|------|------|
| `references/tdd-integration-pattern.md` | TDD 原则层（SOUL.md）+ 执行层（Pipeline）两层级联设计 |
| `references/external-cli-integration-pattern.md` | 外部 CLI 工具集成模式 |
| `D:/Obsidian/Note/Profile能力矩阵.md` | 所有 Profile 的能力清单 |
| `skills/hermes/three-agent-orchestrator/SKILL.md` | 三Agent决策门：何时调 OpenCode vs Coze |