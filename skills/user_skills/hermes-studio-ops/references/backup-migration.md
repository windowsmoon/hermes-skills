# Hermes Backup & Migration (Full Disaster Recovery)

> Last updated: 2026-07-16 — upgraded to full 3-tier disaster recovery.
> Previous version was Tier-1 only (config/data). Now includes browser profile, RAG, WebUI DB, scheduled tasks, startup items, installer, and a restore guide.

## Architecture: Three-Tier Backup

```
TIER 1 — Config & Data (frequently changing)
  Config, memories, skills, scripts, profiles, session DB (state.db),
  kanban, cron, email state, global config, working scripts

TIER 2 — Environment (changes less often)
  Edge browser profile (553 MB — login sessions for automation),
  RAG vector index (114 MB), Web UI database (27 MB), workspace, weixin

TIER 3 — Infrastructure (one-time capture, version-pinned)
  Windows Scheduled Tasks XML (4 tasks: email receiver, fork monitor,
    gateway tunnel, RAG auto-index)
  Startup files (5 .bat files in %APPDATA%\Start Menu\Startup)
  Hermes Studio installer (161 MB, at ~\Downloads)
  Coding program servers (D:\Program\coding本地程序, D:\Program\插件)
```

**Total backup size**: ~961 MB (including installer + browser profile).

**Retention**: Last 4 backups, auto-cleanup of older ones.

## Schedule & Scripts

- **Schedule**: Every Sunday 20:00 (Hermes cron, `0 20 * * 0`)
- **Cron job name**: `Hermes Weekly Backup`
- **Script**: `D:\hermes-data\backup\backup_hermes.py`
- **Batch wrapper**: `D:\hermes-data\backup\weekly_backup.bat`
- **Hermes Python**: `C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.2\win-x64\python\python.exe`
- **Restore guide**: `D:\hermes-data\backup\DR_RESTORE_GUIDE.md` (printed for the new machine)

### Cron Job Definition

Registered in `%LOCALAPPDATA%\hermes\cron\jobs.json`:

```json
{
  "id": "e56e54c14a50",
  "name": "Hermes Weekly Backup",
  "script": "D:\\hermes-data\\backup\\weekly_backup.bat",
  "no_agent": true,
  "schedule": { "kind": "cron", "expr": "0 20 * * 0" },
  "enabled": true,
  "state": "scheduled",
  "workdir": "D:\\hermes-data\\backup",
  "enabled_toolsets": ["terminal"]
}
```

## Full Backup Content Map

```
D:\hermes-data\backup\
├── backup_hermes.py                    # Backup script (three-tier)
├── weekly_backup.bat                   # Cron batch wrapper
├── backup.log                          # Append-only run log
├── DR_RESTORE_GUIDE.md                 # Printable restore guide
│                                        (path mapping, checklist)
│
├── installers/                         # TIER 3: one-time
│   └── Hermes.Studio-0.6.26-x64.exe    (161 MB)
│
├── scheduled_tasks/                    # TIER 3: one-time
│   ├── task_HermesEmailReceiver.xml
│   ├── task_HermesForkMonitor.xml
│   ├── task_HermesGatewayTunnel.xml
│   └── task_Hermes_Obsidian_RAG_AutoIndex.xml
│
├── startup_files/                      # TIER 3: one-time
│   ├── code-server.bat
│   ├── coding_local_server.bat
│   ├── Hermes_Hindsight_Daemon.bat
│   ├── Hermes_Obsidian_RAG.bat
│   └── plugin_server.bat
│
├── coding-programs/                    # TIER 3: one-time
│   ├── server.js  (port 5000)
│   ├── 27c4217bd2358ad6.html
│   └── input[...].txt
│
├── plugin-server/                      # TIER 3: one-time
│   ├── server.js  (port 5001)
│   ├── index.html
│   ├── .coze
│   └── start.bat
│
└── YYYY-MM-DD_HHmmss/                 # TIER 1+2: weekly timestamped
    ├── hermes-config/          # config.yaml, .env, SOUL.md, auth.json, ...
    ├── memories/               # memory provider data files
    ├── skills/                 # all custom skills (25+)
    ├── scripts/                # Hermes agent scripts
    ├── profiles/               # multi-role profiles (5 directors)
    ├── cron/                   # jobs.json
    ├── gateway/                # gateway config
    ├── database/               # state.db (~98 MB) + .db-wal + .db-shm
    ├── email/                  # fork_state.json, email_receiver_state.json
    ├── global-config/          # ~/.hermes/config.yaml, .env
    ├── global-profiles/        # ~/.hermes/profiles/
    ├── hermes-data/            # D:\hermes-data\ key scripts
    ├── relate-program/         # D:\Program\Hermes Studio\ scripts
    ├── hindsight/              # Hindsight daemon config
    ├── hermes-web-ui-db/       # Web UI database (27 MB) + WAL + SHM
    │                             config.json, .token, device-identity.json
    ├── rag-obsidian/           # FAISS vector index (114 MB)
    ├── edge-debug/             # Edge browser profile (553 MB)
    │                             (all login sessions: 巨量百应, etc.)
    ├── workspace/              # Hermes workspace files
    ├── weixin/                 # WeChat platform config
    └── manifest.json           # backup metadata
```

## Restore Procedure (New Machine)

See `DR_RESTORE_GUIDE.md` for the full step-by-step. Summary:

1. **Install toolchain**: Node.js, uv, mermaid-cli on new machine
2. **Install Hermes Desktop**: Download from nousresearch.com (runtime ~3.4 GB, not in backup)
3. **Install Hermes Studio**: Run backup's `installers/Hermes.Studio-*` (161 MB)
4. **Restore files**: Copy each backup subdirectory to the correct path
5. **Import scheduled tasks**: `schtasks /create /xml ...` for each XML
6. **Restore startup items**: Copy `.bat` files to `%APPDATA%\Start Menu\Startup\`
7. **Verify**: Check sessions, memories, skills, cron, profiles, RAG, email, browser automation

### Path Migration (When Username Differs)

If the new machine has a different username (not `Admin`):

1. Do a global text replace in `config.yaml` and `.env` files:
   - `C:\Users\Admin\` → `C:\Users\<new_username>\`
2. Skills may need dependency reinstall:
   ```bash
   cd %LOCALAPPDATA%\hermes\skills\
   for /d %d in (*) do if exist "%d\requirements.txt" uv pip install -r "%d\requirements.txt"
   ```
3. XML task files need `UserId` and path tags updated

## What Is NOT in the Backup

These require re-download or re-configuration on a new machine:

| Item | Reason | Workaround |
|------|--------|------------|
| Hermes Desktop Runtime (~3.4 GB) | Too large (125K files), downloadable | Download from nousresearch.com |
| Third-party CLIs (uv, node, npm, mmdc) | System-level installs | Re-install via winget/npm |
| Edge browser login cookies | Some may expire | Re-login to 巨量百应 etc. |
| Feishu OAuth tokens | Timed tokens (lark-cli) | Re-run OAuth device flow |
| Edge browser profile cookies | Some may expire | Re-login to 巨量百应 etc. |

## Known Bugs Fixed

- **Windows reserved filename `nul`**: The workspace directory contained a file named `nul` (Windows reserved name). `shutil.copytree()` without `ignore` param crashes with `[WinError 87]`. Fixed by adding `ignore_reserved()` function that filters out `nul`, `con`, `prn`, `aux` from directory copies.

## Key Paths (Windows)

| What | Path |
|------|------|
| Hermes data (primary) | `C:\Users\Admin\AppData\Local\hermes\` |
| Hermes global config | `C:\Users\Admin\.hermes\` |
| Hermes Web UI runtime | `C:\Users\Admin\.hermes-web-ui\` |
| Working directory | `D:\hermes-data\` |
| Backup root | `D:\hermes-data\backup\` |
| Cron jobs file | `C:\Users\Admin\AppData\Local\hermes\cron\jobs.json` |
| Hermes bundled Python | `C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.2\win-x64\python\python.exe` |
| Startup items | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` |
| Hermes Studio installer | `%USERPROFILE%\Downloads\Hermes.Studio-*.exe` |
