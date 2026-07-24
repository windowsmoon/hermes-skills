# 多Agent架构模式 (Multi-Agent Architecture Patterns in Hermes)

There are four distinct approaches to multi-agent work in Hermes. Understanding the differences helps choose the right pattern for the task.

## 1. MOA (Mixture of Agents) — 组合模型

**How it works**: Multiple LLMs process the SAME input independently, then an aggregator model merges their outputs.

```
User Query
  ├──→ Reference Model A (e.g., Qwen3.7-plus)  ──→ individual answer
  ├──→ Reference Model B (e.g., DeepSeek-V4-Pro) ──→ individual answer
  ├──→ Reference Model C (e.g., GLM-5.2)       ──→ individual answer
  └──→ Reference Model D (e.g., MiniMax-M3)    ──→ individual answer
              ↓
       Aggregator Model (e.g., GPT-5.5)
              ↓
       Final output (merged/synthesized)
```

**Config**: via Web UI `/api/hermes/config/moa` endpoint or "Mind-Daily" preset.

| Aspect | Detail |
|--------|--------|
| Use when | Need high-quality, multi-perspective answer on a single query |
| Cost | Most expensive — every query calls N+1 models |
| Context | Each model sees full context independently |
| User action | Configure preset once, works transparently |
| Visual | None — automatic fusion |

## 2. Group Chat — 群聊

**How it works**: Multiple agents share one conversation room in Hermes Studio Web UI. Users @mention specific agents.

```
     ┌─────────────────────────────────┐
     │    Shared Conversation Room      │
     │                                   │
     │  User: @架构师 分析这个需求       │
     │  @架构师 Agent: 方案设计...       │
     │  @开发 Agent: 我来实现            │
     │  @Review Agent: 代码需要修改...   │
     └─────────────────────────────────┘
```

| Aspect | Detail |
|--------|--------|
| Use when | Need human-in-loop multi-role collaboration |
| Cost | Medium — each agent responds when @mentioned |
| Context | Shared — all agents see entire conversation |
| User action | Must @mention to direct work |
| Visual | ✅ Chat UI in Hermes Studio |

## 3. delegate_task Pipeline — 分层流水线

**How it works**: The agent spawns subagents with `delegate_task`, each in an isolated context. Orchestrator subagents can further delegate.

```
[Parent Agent]
  │  delegate_task(role='orchestrator', goal='Build feature X')
  │
  ├──→ [Architect Subagent] (strong model)
  │       Writes design doc, splits into modules
  │       Further delegates:
  │         ├──→ [Module A Coder] (cheap model)
  │         └──→ [Module B Coder] (cheap model)
  │
  └──→ [Reviewer Subagent] (strong model)
          Reviews all modules, validates quality
```

**Config**: Must enable orchestrator role:
```yaml
delegation:
  orchestrator_enabled: true
  max_spawn_depth: 9999
  max_concurrent_children: 3
```

| Aspect | Detail |
|--------|--------|
| Use when | Large projects needing cost-efficient tiering |
| Cost | Cheapest — use cheap models for routine work, expensive only for critical reasoning |
| Context | Isolated per subagent — only sees its relevant fragment, saves tokens |
| User action | None — fully automated via `delegate_task` |
| Visual | ❌ No native UI (results return as summaries) |

### Community Pattern: Multi-Tier Collaboration

Hermes PM (splits tasks, writes requirement docs) → Architect/expensive model (designs) → Coders/cheap models (implement per module) → Reviewer/expensive model (validates). Quality ultimately depends on the strongest model's review capability.

## 4. Workflow / DAG — 工作流

**How it works**: Pre-defined directed acyclic graph on Hermes Studio Web UI canvas. Nodes = steps, edges = execution order.

```
[Start Node] ─→ [Step A: fetch data] ─→ [Step B: process] ─→ [End]
                     │                        │
                     ↓                        ↓
              [Step C: validate] ──────→ [Step D: output]
```

| Aspect | Detail |
|--------|--------|
| Use when | Repeatable automation with persistent run tracking |
| Cost | Medium — per-node model calls |
| Context | Per-node workspace with file change tracking |
| User action | Define once, trigger runs later |
| Visual | ✅ Canvas UI in v0.6.27+ Web UI |

## Comparison Matrix

| | MOA | Group Chat | delegate_task Pipeline | Workflow |
|--|:---:|:----------:|:----------------------:|:--------:|
| Config effort | Low (set once) | Medium (create agents) | Low (delegate_task call) | Medium (build DAG) |
| Per-run cost | **Highest** (N+1 models) | Medium | **Lowest** | Medium |
| Context efficiency | Worst (full dup) | Medium | **Best** (fragmented) | Per-node |
| Automation | Auto | Manual (@mentions) | Fully auto | Run lifecycle |
| Best for | Quality-critical Q&A | Multi-role discussion | Cost-sensitive projects | Repeatable pipelines |
| Visual UI | ❌ | ✅ Chat UI | ❌ | ✅ Canvas |



### Pitfalls

- **Profiles are per-CLI, not per-Web-UI by default**. After creating CLI profiles, you must also register them in Web UI's `profiles/` directory (Step 4 above) or the `hermes-studio-use` MCP tools will reject auth for them.
- **`hermes config set` is the only safe way** to write profile `config.yaml`. Direct `patch`/`write_file` to `config.yaml` is refused by Hermes security.
- **MOA is NOT the same as Group Chat or delegate_task**. MOA = same input, multiple models, merged output. Group Chat = same conversation, multiple roles. delegate_task = isolated subagents with fragment context. All three can be combined but serve different purposes.
- **Workflow UI version dependent**: v0.6.12 PDF says no visual workflow page. v0.6.27 has it. Always check the live Web UI.
- **Pipeline context isolation is both strength and weakness**: Cheap models get narrow context → potentially miss cross-cutting concerns. The reviewer step is essential.
- **Group Chat API `profile` field is required** — it maps to a Hermes CLI profile. If the profile doesn't exist, the API returns 200 but the agent won't respond in the room.

## 5. Building a Multi-Agent Pipeline: Full Stack Example

This section covers the complete setup for a Group Chat-based multi-agent collaboration, validated on Hermes Studio v0.6.27.

### Architecture: Combined Pipeline

```
Task Input
  │
  ▼
 1️⃣ MOA Analysis (via Mind-Daily preset — 4 models)
        Qwen3.7+ / DeepSeek-V4-Pro / GLM-5.2 / MiniMax-M3
        → Each produces a COT from its perspective
        → GPT-5.5 aggregator merges
  │
 2️⃣ Conflict Detection (performed by orchestrator agent)
        Compare MOA outputs for contradictions
  │
  ├── Contradictions Found → 3️⃣ Group Chat Room
  │                              Multiple role-specific profiles debate
  │                              → Resolved conclusion
  │
  └── No Contradictions → Skip to 4️⃣
  │
 4️⃣ User Approval Gate (clarify tool or Web UI)
  │
 5️⃣ Execution Dispatch (delegate_task → cheap models)
```

### Step-by-Step: Setting Up Group Chat Profiles

#### Step 1: Create CLI profiles

```bash
# Using the Hermes Studio API
POST /api/hermes/profiles
Body: {"name": "product-manager", "clone": false}
# Repeat for each role
```

Profiles are created at `C:\Users\Admin\AppData\Local\hermes\profiles\<name>\`.

#### Step 2: Write SOUL.md (role personality)

Each profile needs a `SOUL.md` file in its directory (defines the personality/behavior):

```python
with open(f"C:/Users/Admin/AppData/Local/hermes/profiles/{name}/SOUL.md",
          'w', encoding='utf-8') as f:
    f.write("""# SOUL.md — 产品经理
你是资深产品经理，擅长：
- 需求分析和用户故事拆分
- 从用户价值和商业价值角度评估功能优先级
- 产出清晰的PRD和验收标准
""")
```

#### Step 3: Configure model via CLI

```bash
hermes -p <profile-name> config set model.default <model-id>
hermes -p <profile-name> config set model.provider <provider-name>
```

**Known-working model-to-role assignments** (OpenCode Go provider):

| Role | Profile Name | Model | Rationale |
|------|-------------|-------|-----------|
| 🧑‍💼 产品经理 | `product-manager` | `deepseek-v4-pro` | Strong analysis, good PRD |
| 👨‍🔧 研发总监 | `engineering-director` | `qwen3.7-plus` | Best Chinese technical model |
| 🕵️ 测试与质量总监 | `qa-director` | `glm-5.2` | Rigorous logic, fault-finding |
| 📈 运营总监 | `operations-director` | `minimax-m3` | Creative, growth-oriented |
| 📊 大数据总监 | `bigdata-director` | `deepseek-v4-pro` | Data analysis capability |

#### Step 4: Register in Web UI

The Web UI needs a `.model-run-token` for each profile:

```python
import os, shutil
webui_dir = "C:/Users/Admin/.hermes-web-ui/profiles"
src = os.path.join(webui_dir, "default", ".model-run-token")
for name in ["product-manager", "engineering-director", ...]:
    os.makedirs(os.path.join(webui_dir, name), exist_ok=True)
    shutil.copy2(src, os.path.join(webui_dir, name, ".model-run-token"))
```

#### Step 5: Create Group Chat room

```bash
POST /api/hermes/group-chat/rooms
Body: {"name": "架构评审会议室", "inviteCode": "my-room"}
→ Returns room.id (e.g. "mrdpq9qfjiw2g3")
```

#### Step 6: Add agents to the room

```bash
POST /api/hermes/group-chat/rooms/{roomId}/agents
Body: {
  "profile": "product-manager",
  "name": "产品经理",
  "description": "资深产品经理，擅长需求分析和用户价值评估",
  "invited": true
}
```

Tune room config:
```bash
PUT /api/hermes/group-chat/rooms/{roomId}/config
Body: {"maxHistoryTokens": 32000, "tailMessageCount": 10, "triggerTokens": 100000}
```

### Known Limitations

- **`hermes_studio_use_provider_add` MCP tool won't work for new profiles** — needs Web UI auth token. Workaround: use `hermes -p <name> config set` CLI commands.
- **Group Chat agents respond to @mentions only** — human-in-loop, not fully automated.
- **CLI gateway must be started for each profile** for independent gateway responses. For Web UI Group Chat, registered + configured is sufficient.
- **`hermes config set` is the only safe way** to write profile `config.yaml`. Direct `patch`/`write_file` is refused by Hermes security.

### ⚠️ Critical Pitfall: delegate_task Subagent Results May Not Arrive as Messages

Subagents dispatched via `delegate_task` always **complete and save their output to disk**, but the background notification mechanism ("result re-enters the conversation as a new message") **fails reliably** in the Hermes Desktop GUI environment.

**The symptom**: The user says "子任务收不回" (subtasks never come back). Subagents appear to run indefinitely with no result.

**The reality**: Results ARE saved — they just don't appear as new messages in the conversation.

**Workaround — check the delegation cache directory**:

```python
import os
cache = "C:/Users/Admin/AppData/Local/hermes/cache/delegation"
files = sorted([f for f in os.listdir(cache) if f.endswith('.txt')])
for f in files:
    fpath = os.path.join(cache, f)
    size = os.path.getsize(fpath)
    with open(fpath, 'r', encoding='utf-8') as fp:
        first_line = fp.readline().strip()[:100]
    print(f"  {f} {size}B → {first_line}")
```

Each file contains the complete subagent summary — page through with `read_file(path, offset=N, limit=M)` to get the full content.

**Pattern**: File names encode completion time: `subagent-summary-0-20260710_004623_356042.txt` = completed at 2026-07-10 00:46:23.356. Newer files appear at the top of a reverse-sorted list.

### Real Session Example: Conflict Detection

From a validated multi-agent analysis of a "全自动内容中台" (automated content hub) project, the pipeline detected four key conflicts between roles:

| Conflict | Product Manager | Engineering Director | Resolution |
|----------|----------------|---------------------|------------|
| **Effort estimate (4× gap)** | MVP 19-25 person-days | Full build 93 person-days / 7 weeks | PM estimated MVP, Eng estimated full scope — different baselines |
| **Architecture complexity** | Simple 6-node pipeline | 8 services + RabbitMQ + PG + Saga | Iterative: start simple, grow into full architecture |
| **MVP boundary** | 5 explicit MVP modules + 4 phase-2 items | No MVP boundary, full scope estimate | Use Operations Director's 4-phase rollout |
| **Data strategy** | — | (not applicable) | Big Data Director: full pipeline; QA Director: 7 critical risks |

**The agent's role**: After collecting all 5 role-specific analyses (via delegate_task), the orchestrating agent compares outputs, identifies contradictions, and presents them to the user for resolution — completing the approval gate step before execution dispatch.

### Full Pipeline Orchestration (Agent's Steps)

When asked to run this pipeline, the agent:

1. Enables MOA if configured (via `GET/PUT /api/hermes/config/moa`)
2. Spawns `delegate_task(role='orchestrator')` for MOA multi-perspective COTs
3. Compares COTs for contradictions in orchestration context
4. If contradictions: creates Group Chat room → adds role agents → returns room invite for user to watch debate
5. Calls `clarify()` for user approval gate
6. Spawns `delegate_task(goal='Implement approved plan')` with cheap model instructions
