# Multi-Agent Shared Memory Configuration

Real-world example: 6 Hermes Studio profiles sharing the same Hindsight memory bank.

## Profile Inventory

Discovered via `~/.hermes-web-ui/profiles/` directory listing:

| Profile | Role | Discovered |
|---------|------|------------|
| `default` | Default session | ~/.hermes/profiles/ |
| `bigdata-director` | 大数据主管 | Web UI SQLite |
| `engineering-director` | 工程主管 | Web UI SQLite |
| `operations-director` | 运营主管 | Web UI SQLite |
| `product-manager` | 产品经理 | Web UI SQLite |
| `qa-director` | 质量主管 | Web UI SQLite |

## Architecture

```
bigdata-director ⟍
engineering-director ─→ Hindsight (local_embedded) ─→ 共享记忆银行 "hermes"
operations-director ─→     ↕ auto_recall / auto_retain     ↕ SQLite
product-manager   ⟀
qa-director      ⟀
default          ⟅
```

## Two Config Layers

There are TWO hindsight configuration locations that must stay in sync:

### 1. Web UI Config (via API)

```
PUT /api/hermes/config
{"section":"hindsight","values":{"bank_id":"hermes","mode":"local_embedded"}}

PUT /api/hermes/config
{"section":"hindsight","values":{"bank_id":"hermes","mode":"local_embedded"},"restart":true}
```
The `"restart":true` flag triggers an MCP server restart so the config takes effect immediately. Without it, changes may not apply until the next Hermes restart.

Memory limits must be increased for multi-agent sharing:

```\nPUT /api/hermes/config\n{\"section\":\"memory\",\"values\":{\"provider\":\"hindsight\",\"memory_enabled\":true,\"memory_char_limit\":50000,\"user_char_limit\":50000}}\n```

Default 10,000 chars per profile is insufficient when 6+ agents share the same bank. 50,000 each for memory and user profile is a proven working configuration.

### 2. Daemon Config (file system)

`~/.hermes/hindsight/config.json`:
```json
{
  "mode": "local_embedded",
  "api_url": "http://127.0.0.1:9100",
  "bank_id": "hermes",
  "recall_budget": "mid",
  "memory_mode": "hybrid",
  "auto_retain": true,
  "auto_recall": true,
  "retain_context": "conversation between Hermes Agent and the User"
}
```

### Sync Rule

Both configs must have:
- Same `mode` (both `local_embedded` or both `local_external`)
- Same `bank_id` (e.g., `"hermes"`)

If they drift, the memory may not work correctly or different profiles may use different banks.

## Per-Profile Config

Hermes CLI profiles (`~/.hermes/profiles/<name>/config.yaml`):
```yaml
memory:
  provider: hindsight
```

Hermes Studio profiles (in Web UI SQLite) don't need individual config — they inherit from the global Web UI memory section.

## Verification

```bash
# Check Web UI hindsight config
GET /api/hermes/config?section=hindsight
# → {"hindsight":{"bank_id":"hermes","mode":"local_embedded"}}

# Check Web UI memory config
GET /api/hermes/config?section=memory
# → {"memory":{"memory_enabled":true,"user_profile_enabled":true,"provider":"hindsight","memory_char_limit":50000,"user_char_limit":50000}}

# Check daemon config
cat ~/.hermes/hindsight/config.json

# Check env drift: the .env file may disagree with config.json
grep HINDSIGHT_MODE ~/.hermes/.env
# If .env says local_embedded but config.json says local_external → fix config.json

# List profiles
GET /api/hermes/profiles
# → {"profiles":[{"name":"default",...},{"name":"bigdata-director",...},...]}
```

## Troubleshooting: Daemon Not Running / Config Drift

If the hindsight daemon at `127.0.0.1:9100` is unreachable:
1. Check mode in both config locations — if `config.json` says `local_external` but no process is listening on 9100, the old daemon was never auto-started
2. `hindsight_daemon.log` and `hindsight_autostart.log` being 0 bytes is normal — `local_external` expects manual start via `hindsight-embed -p <profile> daemon start`
3. Python health probe: `urllib.request.urlopen("http://127.0.0.1:9100/health")` → `WinError 10061` = daemon is down
4. Recovery: switch both config layers to `local_embedded`, apply with `restart:true`

If env/config drift is found (`.env` says `local_embedded` but `config.json` says `local_external`):
- Always trust `config.json` — it is the active runtime config
- Update it to match `.env` with Python (`json.dump` via execute_code, not write_file which may fail on git-bash)
- Restart after fixing

## New Profile Creation (Shared)

```bash
# Via Hermes Studio API
POST /api/hermes/profiles
{"name":"new-agent","clone":true}

# The new profile automatically inherits the global memory provider=hindsight
# and bank_id=hermes → it shares memory with all other profiles.
```
