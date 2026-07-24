# Obsidian RAG Setup — Production Implementation

Used for a real user setup on 2026-07-07.

## User Configuration

- **Vault**: `D:\Obsidian\Note`
- **Index directory**: `C:\Users\Admin\AppData\Local\hermes\rag_obsidian`
- **Python**: Hermes bundled Python at `C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe`

## Pre-installed Packages

Verified available in Hermes Python:
- `faiss-cpu` ✓
- `numpy` ✓  
- `scipy` ✓
- `sklearn` ✓ (need to install via pip)
- `torch` ✓ (slow import, avoid)
- `yaml` ✓

## Installation Commands

```bash
# Install sklearn (not pre-bundled)
"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe" -m pip install sklearn -q

# Install faiss if missing
"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe" -m pip install faiss-cpu -q
```

## Cron Job Created

```
Job ID: 6910d41d4dab
Name: Obsidian RAG Indexer
Schedule: 0 9 * * * (daily at 9 AM)
Script: "C:\Users\Admin\AppData\Local\hermes\rag_obsidian\index_on_startup.bat"
no_agent: true
```

## Files in rag_obsidian/

| File | Size | Purpose |
|------|------|---------|
| `index_obsidian.py` | 7516 | Main indexing script |
| `query_obsidian.py` | 3403 | Query/search script |
| `index.faiss` | 9873 | FAISS vector index |
| `index_vectorizer.pkl` | 8609 | sklearn TF-IDF vectorizer |
| `index_chunks.pkl` | 9913 | Chunk metadata + sources |
| `metadata.json` | 459 | File hash tracking |
| `index_on_startup.bat` | 519 | Batch for startup |
| `setup_and_run.bat` | 1370 | Initial setup + task creation |
| `README.md` | - | User documentation |

## Key Code Patterns

### Hermes Python path (hardcoded, works)
```
C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe
```

### Reading hermes config for API credentials
```python
import yaml
config = yaml.safe_load(open(r"C:\Users\Admin\AppData\Local\hermes\config.yaml"))
custom_provider = config.get('custom_providers', [{}])[0]
api_key = custom_provider.get('api_key', '')
base_url = custom_provider.get('base_url', '')
```

### Initial test results
- Vault had 2 markdown files
- Generated 13 chunks after processing
- TF-IDF created (13, 189) embedding matrix
- Index built successfully with L2 distance

### Query test with "欢迎"
- Returned 3 relevant passages
- Sources correctly attributed to filenames
- Ranking based on L2 distance (converted to similarity)

## Windows Scheduled Tasks

### Existing (orphaned)
- `C:\Windows\System32\Tasks\ObsidianHybridWatcher` — references missing script `obsidian_hybrid_watchdog.py` at `hermes-agent\venv\pythonw.exe`. Task exists but script file is gone. Should be deleted to avoid confusion/conflict.

### Created
- Task name: `Hermes_Obsidian_RAG_AutoIndex`
- Path: `C:\Windows\System32\Tasks\Hermes_Obsidian_RAG_AutoIndex`
- Trigger: LogonTrigger with 30-second delay (`<Delay>PT0M30S</Delay>`)
- Action: `cmd /c "C:\Users\Admin\AppData\Local\hermes\rag_obsidian\index_on_startup.bat"`
- RunLevel: HighestAvailable

### Startup folder backup
- `C:\Users\Admin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Hermes_Obsidian_RAG.bat`
- This runs as a background min window — doesn't block user login

### Inspecting tasks
```python
import os
task_path = r"C:\Windows\System32\Tasks\TaskName"
with open(task_path, 'rb') as f:
    print(f.read().decode('utf-16-le'))  # tasks are UTF-16 LE XML
```

### Deleting an orphaned task
```python
import subprocess
subprocess.run(f'schtasks /delete /tn "ObsidianHybridWatcher" /f', shell=True)
```

## Vault File Distribution

By design, only `.md` files are indexed. Sample vault had:

| Ext | Count | Indexed? | Reason |
|-----|-------|----------|--------|
| `.md` | 2 | ✅ | Obsidian native format |
| `.txt` | 8 | ❌ | Typically temp/config |
| `.json` | 2 | ❌ | Config files |
| `.xlsx` | 2 | ❌ | Binary |
| `.csv` | 1 | ❌ | Binary |
| `.jpg` | 1 | ❌ | Binary |

To extend indexing to `.txt`, change the file filter to include `f.endswith(('.md', '.txt'))`.