---
name: coze-workflow-automation
description: >
  当用户说「用扣子运行...」触发Coze工作流自动化时使用。
  通过Coze CLI执行工作流，处理数据、调用API、执行自动化任务。
  不要用于：手动对话式操作（走正常对话）、非Coze的自动化流程。
  触发词：用扣子运行、扣子自动化、coze工作流、扣子帮我执行
version: "1.0.0"
triggers:
  - 用扣子运行
  - 扣子自动化
  - coze工作流
  - 扣子帮我执行
tags:
  - coze-workflow-automa
  - coze

---

# Coze Workflow Automation (Class-Level Skill)

## When to Load

Load this skill when the user says or implies anything about running Coze (扣子) workflows or dialog flows.

## What This Skill Does

- Receives user requests like "用扣子运行xxx"
- Calls Coze Workflow/Dialog Flow API
- Returns all Coze output directly to user in real-time
- Handles multi-turn interactions (Interrupt → Resume)
- Ends only when Coze returns `Done` event

## What This Skill Does NOT Do

**Pure pipeline mode — zero LLM processing of Coze output.**

This is an external API tool, like `curl`. Do not:
- Analyze, summarize, or explain Coze responses
- Use any AI model to "think about" or "process" Coze output
- Draw conclusions from Coze's answers
- Make decisions based on Coze content

## Execution Flow

```
User request → Extract workflow_id + params → Call Coze API → Parse SSE
    ↓
Message event → Print content immediately
    ↓
Interrupt event → Print question → Wait for user reply
    ↓
User reply → Resume API → Continue parsing
    ↓
Done event → End
```

## Quick Start

```python
import requests, json

API_TOKEN = "sat_1PpkmE68m9HDTHdwilucRZXf7Hr0e7E9rb2VjQif2PcQPBWql0tSoM5NpY6chi1J"
WORKFLOW_ID = "7657002468341006336"
VERSION = "v0.0.8"  # MUST specify explicitly

# Execute
url = "https://api.coze.cn/v1/workflow/stream_run"
resp = requests.post(url,
    headers={"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"},
    json={
        "workflow_id": WORKFLOW_ID,
        "workflow_version": VERSION,
        "parameters": json.dumps({"input": "雨水", "pics": [], "Voice": "", "check": False, "pre_WF": {}})
    },
    stream=True)

# Parse + Passthrough
for line in resp.iter_lines(decode_unicode=True):
    if line.startswith("event:"): ev = line[6:].strip()
    elif line.startswith("data:"):
        d = json.loads(line[5:])
        if ev == "Message": print(d.get("content",""))
        elif ev == "Interrupt": ...
        elif ev == "Done": print("\n✅ Done")
```

## Parameter Types (Critical)

| Type | Correct | Wrong |
|------|---------|-------|
| string | `"value"` | - |
| array | `[]` | `null`, missing |
| bool | `false` | `""`, `"false"` |
| object | `{}` | `null` |

**Common errors:**
- `"can't convert to bool"` → param is `""` instead of `false`
- `"Missing parameter"` → param is `null` instead of `[]`

## Getting the Right Version

Coze caches versions. ALWAYS check current version first:

```bash
GET https://api.coze.cn/v1/workflows/{workflow_id}/versions
Authorization: Bearer {token}
```

Use the latest version (`items[0].version`) in requests.

## Supported Workflows

| ID | Name | Latest Version | Description |
|----|------|----------------|-------------|
| 7657002468341006336 | test | v0.0.8 | Test workflow for AI sentence generation |

## Coze as Subordinate Agent in Multi-Agent Architecture

Beyond direct user-to-Coze usage, Coze can serve as an **execution-layer worker** in a multi-agent architecture:

```
中层协调 Agent (e.g. Hermes)
  → 通过 Coze API 直接调用工作流
  → 轮询或等待 Webhook 回调
  → 结果写回飞书看板（多维表格）
  → 只在异常时汇报群聊
```

### Communication options

| Method | When to use |
|--------|------------|
| Coze HTTP API (`/v1/workflow/run`) | 中层协调者直接调，同步等或轮询 |
| `@coze/cli` (npm) | Agent 在后台通过 CLI 操作扣子平台 |
| Coze 3.0 coze-bridge (ACP) | 需要 ACP 协议兼容时，基于 JSON-RPC 2.0 |

### Key difference from direct usage

- **Direct mode** (this skill): user ↔ Coze, pure passthrough
- **Agent mode** (new): Hermes ↔ Coze API, Hermes owns orchestration and state

## Related Skills

- `feishu-cli` — if workflow needs data from Feishu bitable
- `libtv-feishu-auto` — for LibTV + Feishu integration
- `orchestrator-loop` — for heavyweight multi-agent orchestration (alternative to lightweight mode)
- `orchestrator-loop/references/lightweight-async-multiagent-pattern.md` — lightweight async pattern with group chat + kanban