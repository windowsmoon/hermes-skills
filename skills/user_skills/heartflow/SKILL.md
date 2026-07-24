---
name: heartflow
description: >
  当需要进行AI引擎认知状态分析、意图分类和决策路由时使用。
  心虫认知引擎，提供31个MCP工具用于认知状态分析。
  不要用于：用户心理画像、日常对话认知分析。
  触发词：心虫、HeartFlow、认知引擎、状态分析
tags:
  - heartflow
  - cognitive
  - analysis
  - mcp
  - engine-state
triggers:
  - 心虫
  - HeartFlow
  - 认知引擎
  - 状态分析

---

# 心虫 HeartFlow — 认知分析引擎

## ⚠️ 重要：心虫的实际能力边界

心虫是一个 **AI Agent 认知预处理引擎**，不是用户心理分析工具。它的 31 个 MCP 工具主要做两件事：
1. **分析 AI 引擎自身的认知状态**（认知负荷、注意力焦点、决策质量衰减）
2. **对输入文本做浅层分类**（general/calculation/emotion/plan 等类型标签）

**不要用它来做深度用户心理学分析**——`heartflow_emotion` 对真实用户文本返回 `type=unknown, intensity=0`，`heartflow_think` 返回模板化判断。用我自己的分析能力反而更准。

## 触发方式（关键词唤醒，非自动）

> **心虫评估：** 分析这段对话
> **心虫分享：** 复盘沟通历史
> **心虫分析：** 看看聊天的质量

## 实用工具（实测可用的）

| 工具 | 实际效果 | 可以用吗 |
|------|---------|---------|
| `heartflow_think` | 返回通用分类（general/calculation）+ 模板化判断 | ⚠️ 浅层，参考价值有限 |
| `heartflow_decision_router` | 分析评估结果并返回决策指令 | ✅ 引擎自检可用 |
| `heartflow_status` | 返回版本/模块健康/记忆层状态 | ✅ 服务健康检查 |
| `heartflow_emotion` | 对真实用户文本返回 unknown | ❌ 对用户文本无效 |
| `heartflow_agent_psychology` | 分析引擎自身7维认知状态 | ✅ 引擎自检 |
| `heartflow_persona_stance_detector` | 返回引擎内部场域数据(U/D/A/H) | ❌ 对用户分析无效 |
| `heartflow_memory_search` | 跨层记忆检索 | ⚠️ 需引擎有记忆数据 |

## 架构

```
你说 "心虫评估：..."
  ↓
我 → HTTP POST JSON-RPC 2.0 → HeartFlow MCP Server (localhost:8099/mcp)
  ↓
心虫返回 → 我判断是否有价值 → 呈现给用户
（如果心虫返回空/模板化响应，我会用自己的分析补充）
```

## 服务信息

- **地址**: http://127.0.0.1:8099/mcp
- **Auth Token**: hf_test123
- **进程管理**: `node bin/daemon.js status/stop/start` (PM2)
- **安装位置**: ~/Developer/mark-heartflow-skill/

## 调用示例

```python
# JSON-RPC 2.0 调用
POST http://127.0.0.1:8099/mcp
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "heartflow_think",
        "arguments": {"input": "分析这段对话..."}
    }
}
```
