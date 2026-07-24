# Hermes Memory Providers — Hindsight + SiliconFlow Free Embeddings

> 📌 **Up-to-date class-level skill: `skill_view(name='hermes-memory-providers')`**
> Includes corrected provider configs (the critical fix: `openai` not `openai_compatible`),
> offline pip install technique, reranker config, and pg0-embedded install steps.

Verified 2026-07-09 via official Hermes Agent llms-full.txt + SiliconFlow pricing page.

## Overview

Hermes ships with **8 external memory provider plugins** (one active at a time):

| Provider | Storage | Cost | Tools | Best For |
|----------|---------|------|-------|----------|
| **Hindsight** | Cloud or local embedded PostgreSQL | Free (local) / Paid (cloud) | `retain`/`recall`/`reflect` (3 tools) | Knowledge graph + entity resolution + cross-memory synthesis — **most capable**, has unique `reflect` tool |
| Honcho | Cloud | Free tier | 5 tools | Multi-agent context sharing, dialectic reasoning |
| OpenViking | Local container | Free | — | Self-hosted |
| Mem0 | Cloud | Paid | — | — |
| Holographic | Cloud/Local | Free/Paid | — | Local SQLite FTS5 |
| RetainDB | Local | Free | — | Minimal |
| ByteRover | Cloud | Paid | — | — |
| Supermemory | Cloud/Local | Free/Paid | — | — |

## Hindsight — Deep Dive

### Capabilities

- **Knowledge graph** — entities and relationships between memories, auto-extracted
- **Entity resolution** — deduplicates references to the same entity across sessions
- **Multi-strategy retrieval** — semantic search, entity-based, hybrid
- **Cross-memory synthesis** — unique `hindsight_reflect` tool that LLM-synthesizes across stored memories

### Tools Provided

| Tool | Purpose |
|------|---------|
| `hindsight_retain` | Store new information with automatic entity extraction; supports per-call tags |
| `hindsight_recall` | Search stored memories (semantic, entity graph, hybrid) |
| `hindsight_reflect` | **Unique** — LLM-powered cross-memory synthesis; no other provider has this |

### How It Integrates

When active, Hermes automatically:
1. Injects provider context into system prompt (what the provider knows)
2. Prefetches relevant memories before each turn (background, non-blocking)
3. Syncs conversation turns to the provider after each response
4. Extracts memories on session end (for providers that support it)
5. Mirrors built-in memory writes to the external provider
6. Adds provider-specific tools (`hindsight_*`)

Built-in MEMORY.md / USER.md continue working independently — the external provider is additive.

## Setup: Hermes Studio Path (no hermes CLI)

When running via Hermes Studio (Desktop App), the `hermes` CLI is not available on PATH. Configuration must go through the Hermes Studio Web UI API plus direct file writes.

### Step 1: Install Dependencies

The Hermes runtime uses its bundled Python. Install packages via `uv pip install --python`:

```bash
uv pip install --python "C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe" hindsight-client>=0.6.1
uv pip install --python "C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe" hindsight-embed>=0.1.0
# heavy: includes PostgreSQL, takes 3-5 min:
uv pip install --python "C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe" hindsight-all
```

The required packages:
- `hindsight-client` (0.8.4) — API client library
- `hindsight-embed` (0.8.4) — embedded daemon CLI (manages profiles, starts/stops daemon)
- `hindsight-all` (0.8.4) — full bundle: `hindsight-client` + `hindsight-embed` + `hindsight-api-slim[all]` (PostgreSQL)

### Step 2: Set memory.provider via Web UI API

```json
// Read current config
GET /api/hermes/config?section=memory

// Set provider
PUT /api/hermes/config
{
  "section": "memory",
  "values": {
    "memory_enabled": true,
    "user_profile_enabled": true,
    "memory_char_limit": 10000,
    "user_char_limit": 10000,
    "provider": "hindsight"
  }
}
```

### Step 3: Create config.yaml at ~/.hermes/

Create `~/.hermes/config.yaml`:
```yaml
memory:
  provider: hindsight
```

Also copy to profile dir: `~/.hermes/profiles/default/config.yaml`

### Step 4: Create Hindsight config

Create `~/.hermes/hindsight/config.json`:

```json
{
  "mode": "local_embedded",
  "bank_id": "hermes",
  "recall_budget": "mid",
  "memory_mode": "hybrid",
  "auto_retain": true,
  "auto_recall": true,
  "retain_async": false,
  "retain_context": "conversation between Hermes Agent and the User",
  "llm_provider": "openai",      # ⚠️ NOT openai_compatible — that's not a valid provider
  "llm_model": "Pro/deepseek-ai/DeepSeek-V4-Flash",
  "llm_base_url": "https://api.siliconflow.cn/v1"
}
```

For local_embedded mode, Hindsight needs an LLM API key for memory extraction/synthesis. The LLM provider config:
- `llm_provider`: `openai`, `anthropic`, `gemini`, `groq`, `openrouter`, `minimax`, `ollama`, `lmstudio`, or `openai_compatible`
- `llm_model`: Model name for the provider
- `llm_base_url`: Only needed for `openai_compatible` — the base URL

### Step 5: Set environment variables

Add to `~/.hermes/.env`:
```
# LLM API key for Hindsight local mode memory extraction/synthesis
HINDSIGHT_LLM_API_KEY=sk-jedattdxgjzvsorcnouxjtloyniravjwbbyvttaizqupzbep
HINDSIGHT_MODE=local_embedded
```

### Step 6: Restart gateway

The Hermes agent gateway process must be restarted to pick up the new memory provider:
```python
import psutil, signal, os
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmd = ' '.join(proc.info['cmdline'] or [])
        if 'hermes_cli.main' in cmd and 'gateway' in cmd.lower():
            os.kill(proc.info['pid'], signal.SIGTERM)
            break
    except: pass
```

The Hermes Studio auto-restarts the gateway process. The Hindsight daemon starts lazily on first use (first chat session that triggers memory operations).

### Step 7: Verify

- Check logs: `~/.hermes/logs/hindsight-embed.log` (created after first daemon startup)
- Check runtime: `hindsight-embed -p hermes profile list -o json`
- Open local UI: `hindsight-embed -p hermes ui start`

## Config File Reference

All config keys for `~/.hermes/hindsight/config.json`:

| Key | Default | Description |
|-----|---------|-------------|
| `mode` | `cloud` | `cloud`, `local_embedded`, or `local_external` |
| `bank_id` | `hermes` | Memory bank name |
| `bank_id_template` | — | Dynamic bank name template (`{profile}`, `{user}`, etc.) |
| `recall_budget` | `mid` | `low`/`mid`/`high` — recall thoroughness |
| `recall_prefetch_method` | `recall` | `recall` (raw facts) or `reflect` (LLM synthesis) |
| `recall_max_tokens` | `4096` | Max tokens for recall results |
| `recall_types` | `observation` | Fact types surfaced by recall. Changed from all-3-types by default (now only observations). To restore: `"observation,world,experience"` |
| `auto_recall` | `true` | Auto-recall before each turn |
| `auto_retain` | `true` | Auto-retain conversation turns |
| `retain_every_n_turns` | `1` | Retain every N turns |
| `memory_mode` | `hybrid` | `hybrid` (context + tools), `context` (inject only), `tools` (tools only) |
| `llm_provider` | `openai` | LLM for extraction/synthesis (local mode only) |
| `llm_model` | per-provider | Model name |
| `llm_base_url` | — | Endpoint for `openai_compatible` |

## SiliconFlow Free Embedding API

**Verified free models** (from https://siliconflow.cn/pricing, 2026-07-09):

| Model | Input Price | Output Price | Best For |
|-------|------------|-------------|----------|
| BAAI/bge-m3 | **Free** | — | General purpose, multilingual, 1024-dim |
| BAAI/bge-reranker-v2-m3 | **Free** | — | Re-ranking |
| BAAI/bge-large-zh-v1.5 | **Free** | — | Chinese-only |
| BAAI/bge-large-en-v1.5 | **Free** | — | English-only |
| bge-m3 (Pro) | ¥0.07/M Tokens | — | Higher throughput |

### API Endpoint (OpenAI-compatible)

```bash
curl -X POST https://api.siliconflow.cn/v1/embeddings \
  -H "Authorization: Bearer sk-your-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "BAAI/bge-m3", "input": "text to embed"}'
```

Returns 1024-dimensional vectors. Tested and verified working 2026-07-09.

## Hindsight Modes Comparison

| Mode | Storage | Dependencies | When to Use |
|------|---------|-------------|-------------|
| **cloud** | Hindsight Cloud (api.hindsight.vectorize.io) | `hindsight-client` only | Production, want managed service |
| **local_embedded** | Embedded PostgreSQL (auto-started) | `hindsight-all` (heavy: full bundle with PostgreSQL) | Local dev, privacy, want daemon managed by Hermes |
| **local_external** | Your own Hindsight server | `hindsight-client` only | Already running Hindsight via Docker |

## Comparison: Hindsight vs FAISS RAG

| Decision Factor | Choose FAISS RAG | Choose Hindsight |
|----------------|-----------------|-----------------|
| Goal | Query external documents | Remember across sessions |
| Data | Obsidian vault, PDFs, notes | Conversation history, user facts, entities |
| Query type | Document chunks | Entities, relationships, synthesized memory |
| Setup effort | Manual scripts + cron | `hermes memory setup` or Config API |
| Embedding cost | Free (TF-IDF, no API) | Free (SiliconFlow BAAI/bge-m3) |
| Knowledge graph | No | Yes |
| Run together? | ✅ Yes — orthogonal | ✅ Yes |

## Pitfalls

- **`hindsight-all` is heavy**: Contains PostgreSQL binary and API server. Install in background with `notify_on_complete=true`, takes 3-5 minutes. Total: ~50 packages (~300MB+ including torch 116MB, claude-agent-sdk 76MB, scipy 34MB, onnxruntime 12MB)\n- **Network timeouts with pip/uv on large packages**: When `uv pip install` repeatedly times out on 100MB+ packages, bypass via direct wheel download:\n  ```python\n  import json, urllib.request\n  url = f\"https://pypi.org/pypi/{pkg_name}/json\"\n  data = json.loads(urllib.request.urlopen(urllib.request.Request(url)).read())\n  wheel = [r for r in data['releases'][data['info']['version']] if r['filename'].endswith('.whl')][0]\n  urllib.request.urlretrieve(wheel['url'], local_path)\n  subprocess.run(['uv', 'pip', 'install', '--python', bundled_python, local_path], timeout=120)\n  ```\n  Python's `urllib` handles constrained networks better than pip/uv in some environments.\n- **Cloud mode is the realistic fallback**: When repeated `local_embedded` install attempts fail on network, switch to `cloud` mode. Only needs `hindsight-client` (instant, 0.3MB) + API key from `ui.hindsight.vectorize.io`. Change `mode` to `\"cloud\"` in config.json, set `HINDSIGHT_API_KEY` in `.env`, remove `HINDSIGHT_LLM_API_KEY`.
- **Local embedded daemon is lazy**: Only starts on first memory operation (first chat retain/recall), not at gateway start
- **memory.provider needs multiple config paths**: Web UI API sets it for the Studio, `~/.hermes/config.yaml` sets it for the agent runtime, profile config may also be needed
- **Gateway restart required**: Config changes don't hot-reload — must send SIGTERM to `hermes_cli.main gateway run` process
- **HINDSIGHT_LLM_API_KEY vs HINDSIGHT_API_KEY**: Cloud mode uses `HINDSIGHT_API_KEY`; local_embedded mode uses `HINDSIGHT_LLM_API_KEY` (the LLM key for extraction/synthesis, stored in `.env`)
- **Hermes Studio CLI not available**: The `hermes` CLI command is not on PATH when running via Hermes Desktop. Use `uv pip install --python <bundled>` for package management and the Web UI API for config settings
- **SiliconFlow model name format**: Pro models use `Pro/deepseek-ai/DeepSeek-V4-Flash` format; free models use `BAAI/bge-m3` directly

## Official References

- Hermes docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers
- Hindsight plugin README (local): `C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\Lib\site-packages\plugins\memory\hindsight\README.md`
- SiliconFlow pricing: https://siliconflow.cn/pricing
- Hindsight website: https://ui.hindsight.vectorize.io
