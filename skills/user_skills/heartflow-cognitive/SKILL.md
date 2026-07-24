---
name: heartflow-cognitive
description: '当需要进行AI引擎认知状态分析、意图分类、决策路由时使用。 31个MCP工具：认知状态分析、意图分类、决策路由、情绪感知、记忆检索、梦境分析。 不要用于：用户心理学画像分析（心虫分析的是引擎自身状态，不是用户心理）。
  触发词：心虫、认知分析、分析我的状态、决策路由、意图分类

  '
tags:
- cognitive
- mcp
- heartflow
- decision-routing
- emotion
triggers:
- 心虫
- 认知分析
- 分析我的状态
- 决策路由
- 意图分类
---

# HeartFlow 心虫认知引擎

## 定位

HeartFlow 是一个 **AI 认知预处理引擎**，不是用户心理画像工具。
它在 Agent 回复前运行，用来**感知意图、分类任务类型、检测认知偏差**，
从而让下游模型做更少的逻辑错误和 Token 消耗。

## 安装

```bash
# 仓库位置
~/Developer/mark-heartflow-skill/

# 启动 MCP 服务（PM2 守护）
cd ~/Developer/mark-heartflow-skill
node bin/daemon.js start
# 服务运行在 http://localhost:8099/mcp
```

## MCP 工具分类（31个）

### 意图认知（最常用）
| 工具 | 用途 | 参数 |
|------|------|------|
| `heartflow_think` | 完整思维链：分类输入→路由→推理→输出 | `input`（必填）|
| `heartflow_think_fast` | 快速推理判断模式，低 Token | `input`（必填）|
| `heartflow_decision_router` | 决策路由：分析评估结果→匹配决策规则 | `input`（必填）|
| `heartflow_emotion` | PAD 三维情绪分析 | `input`（必填）|

### 记忆与知识
| 工具 | 用途 |
|------|------|
| `heartflow_memory_search` | 跨层记忆检索 |
| `heartflow_dream` | 记忆离线整合升华 |
| `heartflow_knowledge_query` / `_add_node` / `_stats` | 知识图谱 |

### 引擎自检（分析引擎自身状态，不是用户）
| 工具 | 用途 | 说明 |
|------|------|------|
| `heartflow_agent_psychology` | 引擎自身7维认知心理状态 | ❌ 不是分析用户 |
| `heartflow_cognitive_check` | 引擎认知状态签到 | ❌ 不是分析用户 |
| `heartflow_status` | 服务健康检查 | ❌ 不是分析用户 |
| `heartflow_self_heal` | 自愈策略推荐 | ❌ 不是分析用户 |

## 重要提示（踩坑记录）

- `heartflow_agent_psychology`、`heartflow_cognitive_check`、`heartflow_engine_pacing` 等工具分析的是 **HeartFlow 引擎自身的认知状态**，不是用户的心理画像。
- 如果用户要求"分析我"或"分析我的认知水平"，不要使用 `heartflow_agent_psychology` —— 这个工具返回的是引擎内部 U/D/A/H 场域状态，对用户分析没有意义。
- 正确的做法是：用 `heartflow_think` 结合对话上下文做输入分析，或直接用 LLM 自己的分析能力。

## 触发词

> 心虫评估：... / 心虫分享：...

## Auth Token

配置在环境变量中。MCP 端口 8099。
