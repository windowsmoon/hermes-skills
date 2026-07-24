---
name: hermes-memory-providers
description: >
  当用户需要hermes-memory-providers时使用。
  不要用于：无关场景。
  触发词：配置记忆Provider、部署记忆、Hindsight
author: agent
version: "1.0.0"
tags:
  - hermes
  - memory
  - providers
  - hindsight
  - rag
  - knowledge-graph
triggers:
  - 配置记忆Provider
  - 部署记忆
  - Hindsight

---

# Hermes External Memory Providers

Hermes ships with 8 external memory provider plugins. Only **one** can be active at a time (built-in MEMORY.md/USER.md is always active alongside it).

## Quick Start

```bash
hermes memory setup              # Interactive picker + configuration
hermes memory status             # Check what's active
hermes memory off                # Disable external provider
```

Or in `~/.hermes/config.yaml`:
```yaml
memory:
  provider: hindsight   # or honcho, mem0, openviking, holographic, retaindb, byterover, supermemory
```

## When Active

The provider automatically:
1. Injects context into system prompt (what the provider knows)
2. Prefetches relevant memories before each turn
3. Syncs conversation turns after each response
4. Extracts memories on session end
5. Adds provider-specific tools (`hindsight_retain`, `hindsight_recall`, etc.)

## Config Storage

- **Config file**: `$HERMES_HOME/<provider>/config.json` (profile-local)
- **Environment**: `$HERMES_HOME/.env`
- **Database**: per-provider (pg0 embedded, SQLite, or external)

## Hindsight + SiliconFlow Deployment

See `references/hindsight-siliconflow.md` for a complete step-by-step recipe.

## Multi-Agent Shared Memory (Profiles)

Hermes Studio supports multiple agent profiles sharing the same Hindsight memory bank. When multiple profiles exist, configure them all to use the same `bank_id` so knowledge learned by one agent is accessible to others.

### Profile Discovery

Hermes Studio profiles live in the SQLite database (`~/.hermes-web-ui/hermes-web-ui.db`), NOT under `~/.hermes/profiles/`. To list them:

```bash
# Via Hermes Studio API
GET /api/hermes/profiles

# Via file system
ls ~/.hermes-web-ui/profiles/
```

Each profile gets a directory with a `.model-run-token` file. The `~/.hermes/profiles/` directory only holds CLI-based profiles (e.g. `default`).

### Enabling Shared Memory Across Profiles

1. **Set a shared `bank_id`** in the Web UI config's `hindsight` section:
   ```bash
   PUT /api/hermes/config
   {"section":"hindsight","values":{"bank_id":"hermes","mode":"local_embedded"}}
   ```

2. **Sync daemon config** at `~/.hermes/hindsight/config.json`:
   ```json
   {
     "mode": "local_embedded",
     "bank_id": "hermes",
     "api_url": "http://127.0.0.1:9100",
     "auto_retain": true,
     "auto_recall": true,
     "memory_mode": "hybrid"
   }
   ```

3. **Increase memory char limits** for shared pool capacity (default 10k is too small for 6+ agents):
   ```bash
   PUT /api/hermes/config
   {"section":"memory","values":{"memory_char_limit":50000,"user_char_limit":50000}}
   ```

4. **Restart MCP servers** for the config to take effect:
   ```bash
   POST /api/hermes/mcp/reload
   # or run PUT /api/hermes/config with "restart":true
   ```

See `references/multi-agent-shared-memory.md` for a complete example with 6 profiles.

### Profile: Default Config
Each profile's `~/.hermes/profiles/<name>/config.yaml` should contain:
```yaml
memory:
  provider: hindsight
```

All profiles sharing the same `bank_id` will read/write from the same memory store.

## Memory Char Limit (2026-07-22 Update)

Default `memory_char_limit: 10000` is too small for production. Recommended: 30000-50000.

```yaml
# config.yaml
memory:
  memory_char_limit: 40000
  user_char_limit: 40000
```

## Tagged Memory Format (2026-07-22)

MEMORY.md entries should use category tags for better semantic search:

| Tag | Meaning |
|:----|:--------|
| `[user]` | User preferences, style |
| `[knowledge]` | Verified technical facts |
| `[experience]` | Lessons learned, bugs |
| `[rule]` | Distilled principles |
| `[task]` | Status updates |

Example:
```
§ [experience] delegate_task 子Agent 经常不返回 → 改用 Loop Engine
§ [rule] 零成本优先：能用免费工具不付费
```

- `llm_provider: openai_compatible` is **not valid** for hindsight-api-slim. Use `openai` instead and set `llm_base_url` to the custom endpoint.
- `reranker_provider: none` is **not valid**. Use `rrf` (algorithm-based, no API), `siliconflow`, or another supported value.
- Local embedded mode (`local_embedded`) depends on `pg0-embedded` for PostgreSQL — install via `uv pip install pg0-embedded` or `hindsight-api-slim[embedded-db]`.
- `local_embedded` mode auto-manages the daemon; `local_external` mode requires you start it manually via `hindsight-embed -p <profile> daemon start`.
- File lock conflicts happen when the Hermes gateway is running during pip install — kill the gateway first via the Profiles API (`POST /api/hermes/profiles/{name}/gateway/restart`) or `taskkill`.
- `hindsight-all` is the all-in-one bundle (~500MB) — prefer installing components incrementally.
- The Hermes gateway cannot start with `hindsight-embed daemon` already holding the env file lock. Start daemon first, THEN restart gateway.
- `hindsight-embed -p <profile> daemon start` runs the daemon in foreground by default — use a background terminal for persistent runtime.
- The Control Center (`control start`) uses a random token per session — save the URL with token when first launched.
- **Web UI hindsight section must match daemon config**: `~/.hermes/hindsight/config.json`'s `mode` field and the Web UI config's `hindsight.mode` must be the same value. If they drift (e.g., one is `local_embedded` and the other `local_external`), memory operations may silently fail or use separate banks. Sync both when changing modes.

- **`local_external` requires the daemon to be running**: If mode is `local_external` but the daemon at `127.0.0.1:9100` is unreachable, memory operations fall through silently. Check daemon health: `curl http://127.0.0.1:9100/health`. If port 9100 is not listening, either start the daemon (`hindsight-embed -p <profile> daemon start`) or switch mode to `local_embedded` (embedded mode auto-manages the daemon inside the Hermes process).

- **`local_external` → `local_embedded` migration flag**: Switching modes requires BOTH the Web UI config AND `~/.hermes/hindsight/config.json` to be updated. Use `PUT /api/hermes/config` with body `{"section":"hindsight","values":{"mode":"local_embedded","bank_id":"hermes"},"restart":true}` to apply and restart simultaneously.

- **`write_file` tool may fail on `~/.hermes/` paths**: On Windows (git-bash), the `write_file` tool can produce encoding errors when writing to `~/.hermes/hindsight/config.json`. Workaround: use `execute_code` with Python's `open()` + `json.dump()` instead. The file is a standard UTF-8 JSON file regardless of the terminal encoding.
  ```python
  import json, os
  config = {"mode": "local_embedded", "bank_id": "hermes", ...}
  path = os.path.expanduser("~/.hermes/hindsight/config.json")
  with open(path, 'w') as f:
      json.dump(config, f, indent=2)
  ```

- **`.env` vs `config.json` mode drift**: The `~/.hermes/.env` file may specify `HINDSIGHT_MODE=local_embedded` while `~/.hermes/hindsight/config.json` has `"mode": "local_external"`. These two must agree. When in doubt, prefer `local_embedded` (auto-manages the daemon lifecycle) over `local_external` (requires separate daemon start). Check both files when troubleshooting silent memory failures.

- **Daemon health check always fails on fresh install**: The hindsight daemon at `127.0.0.1:9100` may not be running even though `hindsight/config.json` specifies `local_external` mode. The daemon logs (`hindsight_daemon.log`, `hindsight_autostart.log`) are often 0 bytes. This is normal — `local_external` requires manual daemon start. Switch to `local_embedded` mode if the daemon never starts spontaneously.
- **Memory char limits too small for multi-agent**: Default 10,000 chars per profile is insufficient when 6+ agents share the same bank. Bump both `memory_char_limit` and `user_char_limit` to 50,000 or higher via `PUT /api/hermes/config` (section=memory).

## Hermes Studio API Config

When `hermes` CLI is not available (Hermes Studio env), configure memory provider via the Web UI API:

```bash
# Set memory provider
curl -X PUT http://127.0.0.1:8748/api/hermes/config \
  -H "Content-Type: application/json" \
  -d '{"section":"memory","values":{"provider":"hindsight","memory_enabled":true}}'

# Verify
curl http://127.0.0.1:8748/api/hermes/config?section=memory
```

## Control Center

Start the Hindsight web control center for memory browsing and management:

```bash
hindsight-embed -p <profile> control start
# Opens at http://localhost:7878/?token=<random-token>
```

Features: memory bank browsing, search, config management, daemon status.

## Windows Startup Automation

See `templates/hermes-hindsight-startup.bat` for a combined daemon + control center startup script.

Place it in Windows Startup folder: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`

## Python Stdlib Dependency (Hermes Bundled Python)

**Critical issue discovered 2026-07-22**: The Hermes bundled Python at `0.18.2/win-x64/python/` is a **stripped-down distribution** that lacks most of the standard library (`encodings`, `importlib`, etc.). When Hindsight needs to import `hindsight-client` in-process (for `local_embedded` mode), the import fails with `ModuleNotFoundError: No module named 'encodings'` even though the package is installed.

Root cause: Hermes deleted the old `0.18.0` runtime (to free ~2GB disk space), which was the original environment where Hindsight was installed. The replacement `0.18.2` is a delta/minimal build.

### Diagnosis Checklist

When Hindsight isn't working:

1. **Check process**: `tasklist | grep hindsight` — no process means daemon wasn't started
2. **Check port**: `curl http://127.0.0.1:9100/health` or socket connect — port 9100 not listening means `local_external` mode has no daemon
3. **Check config**: `~/.hermes/hindsight/config.json` — verify `mode` matches Web UI config's `hindsight.mode`
4. **Check Python stdlib**: Run `python.exe -c "import encodings; import importlib; print('OK')"` in the Hermes bundled Python (`0.18.2/win-x64/python/`). If it fails with `ModuleNotFoundError`, the stdlib is missing
5. **Check correct package**: The package name is `hindsight-client`, **NOT** `hindsight` (which is an unrelated UK test tool). Verify with `python.exe -m pip list | grep hindsight`

### Fix: Replace Missing Stdlib (2026-07-22 Working Solution)

The Hermes `0.19.0` directory has a complete stdlib. The fix that worked:

```python
import os, shutil

py019 = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.19.0/win-x64/python")
py0182 = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/python")

# 1. Copy encodings + DLLs from 0.19.0 to 0.18.2
shutil.copytree(os.path.join(py019, "Lib", "encodings"),
                os.path.join(py0182, "Lib", "encodings"))
shutil.copytree(os.path.join(py019, "DLLs"),
                os.path.join(py0182, "DLLs"))

# 2. Install hindsight-client in 0.19.0 Python (has full stdlib)
# PYTHONHOME must point to 0.19.0 for this to work
env = os.environ.copy()
env["PYTHONHOME"] = py019
subprocess.run([os.path.join(py019, "python.exe"), "-m", "pip", "install", "hindsight-client"],
    env=env, timeout=120)

# 3. Copy installed packages to 0.18.2 site-packages
sp_019 = os.path.join(py019, "Lib", "site-packages")
sp_0182 = os.path.join(py0182, "Lib", "site-packages")
for pkg in ["hindsight_client", "hindsight_client_api", "aiohttp_retry"]:
    src = os.path.join(sp_019, pkg)
    dst = os.path.join(sp_0182, pkg)
    if os.path.isdir(src) and not os.path.isdir(dst):
        shutil.copytree(src, dst)
```

### Alternative: Use 0.19.0 Python with PYTHONHOME

If fixing 0.18.2 is impractical, use the 0.19.0 Python directly for hindsight operations:

```python
import os, subprocess
py019 = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.19.0/win-x64/python/python.exe")
env = os.environ.copy()
env["PYTHONHOME"] = os.path.dirname(os.path.dirname(py019))
result = subprocess.run([py019, "-c", "import hindsight_client; print('OK')"], env=env)
```

### Memory Tool vs Hindsight

| Aspect | `memory` tool (built-in) | Hindsight (external provider) |
|--------|-------------------------|-------------------------------|
| Char limit | Hard 10,000 | Configurable (default 50,000) |
| Scope | Per-entry | Knowledge graph + semantic |
| Tools | `memory` only | `hindsight_retain/recall/reflect` |
| Running? | Always | Only if daemon runs |
| Fix if full | Remove old entries (batch operations) | Install `hindsight-client` + fix Python |

## Useful Links

- Memory Providers docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers
- Hindsight plugin README: https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/hindsight/README.md
- SiliconFlow pricing (free embeddings): https://siliconflow.cn/pricing

## Reference Files

| File | Content |
|------|---------|
| `references/hindsight-siliconflow.md` | Full Hindsight + SiliconFlow deployment recipe (installation, env config, daemon start) |
| `references/multi-agent-shared-memory.md` | Multi-profile shared memory configuration with 6 profiles, two config layers, verification steps |
