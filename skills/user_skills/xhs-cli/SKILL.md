---
name: xhs-cli
description: >
  当用户需要操作小红书时使用。
  支持：搜索笔记、阅读帖子、浏览主页、点赞评论关注收藏发布。
  不要用于：抖音/B站/微博等其他社交平台、内容深度分析。
  触发词：小红书、xhs、搜小红书、发小红书、小红书笔记
author: jackwener
version: "1.0.0"
tags:
  - xhs
  - xiaohongshu
  - 小红书
  - rednote
  - social-media
  - cli
triggers:
  - 小红书
  - xhs
  - 搜小红书
  - 发小红书
  - 小红书笔记

---

# Xhs Cli

> [!NOTE]
> An alternative package [xiaohongshu-cli](https://github.com/jackwener/xiaohongshu-cli) is available, which uses a reverse-engineered API and runs faster.
> This package (`xhs-cli`) uses a headless browser (camoufox) approach — slower but more resilient against risk-control detection.
> Choose whichever best fits your needs.

# xhs-cli Skill

A CLI tool for interacting with Xiaohongshu (小红书). Use it to search notes, read details, browse user profiles, and perform interactions like liking, favoriting, and commenting.

## Prerequisites

```bash
# Install (requires Python 3.8+)
uv tool install xhs-cli
# Or: pipx install xhs-cli
```

## Hermes Environment (Bundled Python)

In Hermes Studio, install into the **bundled Python** (not system Python):

```bash
# Find the bundled python
# Typically: ~/.hermes-web-ui/desktop-runtime/hermes/<version>/win-x64/python/python.exe

# Install xhs-cli (also pulls xiaohongshu-cli v0.6.4, upgrades xhs.exe to API-based)
uv pip install --python <bundled-python-path> xhs-cli
```

The bundled Python's `Scripts/` directory is NOT on PATH. Call xhs via full path in `execute_code`:

```python
import subprocess, os
script_dir = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/python/Scripts")
xhs = os.path.join(script_dir, "xhs.exe")
result = subprocess.run([xhs, "status"], capture_output=True, text=True, timeout=30)
print(result.stdout)
```

See `references/installation-notes.md` for full details.

## Authentication

All commands require valid cookies to function.

```bash
xhs status                     # Check saved login session (no browser extraction)
xhs login                      # Auto-extract Chrome cookies
xhs login --cookie "a1=..."    # Or provide cookies manually
```

Authentication first uses saved local cookies. If unavailable, it auto-detects local Chrome cookies via browser-cookie3. If extraction fails, QR code login is available.

### QR Code Login

```bash
xhs login --qrcode              # Browser-assisted QR login (requires camoufox Firefox)
xhs login --cookie "a1=..."    # Import cookies directly from a known a1 value
```

#### Camoufox Firefox Binary Issue

`xhs login --qrcode` requires camoufox Firefox (~492MB from GitHub releases). Download often fails with `IncompleteRead` on unstable connections, showing:
```
camoufox.exceptions.CamoufoxNotInstalled: official/stable is not installed
```

**Workaround** — Use Playwright Chromium for QR login (Chromium ~182MB, downloads reliably):

1. Install Playwright Chromium into the same bundled Python:
   ```bash
   python -m playwright install chromium
   ```
2. Run a custom Playwright script that opens xiaohongshu login page, captures the QR code on the desktop, and waits for the user to scan with their phone.
3. After scanning, extract the `a1` cookie and import to xhs:
   ```bash
   xhs login --cookie "a1=<value>"
   ```

See `references/camoufox-workaround.md` for a complete runnable Playwright-based QR login script.

#### Browser Cookie Extraction

`browser-cookie3` can extract cookies from Edge, Chrome, Firefox, etc. If the user has logged into 小红书 in their browser, cookies are auto-detected. If no cookies found across all browsers, fall back to the Playwright QR code approach.

## Command Reference

### Search

```bash
xhs search "咖啡"              # Search notes (rich table output)
xhs search "咖啡" --json       # Raw JSON output
```

### Read Note

```bash
# View note (xsec_token auto-resolved from search cache)
xhs read <note_id>
xhs read <note_id> --comments  # Include comments
xhs read <note_id> --xsec-token <token>  # Manual token
xhs read <note_id> --json
```

### User

```bash
xhs user <user_id>
xhs user <user_id> --json
xhs user-posts <user_id>
xhs user-posts <user_id> --json
xhs followers <user_id>
xhs following <user_id>
```

### Discovery

```bash
xhs feed                       # Explore page recommended feed
xhs topics "旅行"               # Search topics/hashtags
```

### Interactions (require login)

```bash
xhs like <note_id>
xhs like <note_id> --undo
xhs favorite <note_id>
xhs favorite <note_id> --undo
xhs comment <note_id> "好棒！"
xhs delete <note_id>
```

### Favorites

```bash
xhs favorites                  # List your favorites
xhs favorites --max 10
```

### Post

```bash
xhs post "标题" --image photo1.jpg --image photo2.jpg --content "正文"
```

### Account

```bash
xhs status
xhs whoami
xhs whoami --json
xhs login
xhs logout
```

## JSON Output

Major query commands support `--json` for machine-readable output.

**Response envelope** (v0.6.4):
```json
{ "ok": true, "data": { ... }, "schema_version": "1" }
```

**Extracting from Python subprocess:**

```python
import subprocess, json, os

# Path to xhs in Hermes bundled Python
scripts = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/python/Scripts")
xhs = os.path.join(scripts, "xhs.exe")

# Search results: data.items[].id, .note_card.display_title, .user.nickname
result = subprocess.run([xhs, "search", "话题", "--json"], capture_output=True, text=True, timeout=30)
data = json.loads(result.stdout)
if data.get("ok"):
    for item in data["data"]["items"][:3]:
        card = item.get("note_card", {})
        user = card.get("user", {})
        print(f'{item["id"]} - {card.get("display_title","")} - {user.get("nickname","")}')

# User info: data.user.id, .name, .nickname, .red_id
result = subprocess.run([xhs, "whoami", "--json"], capture_output=True, text=True, timeout=10)
who = json.loads(result.stdout)
u = who["data"]["user"]
print(f'{u["name"]} (@{u["red_id"]}) - user_id={u["id"]}')
```

## Agent Integration Tips

```python
# Typical from execute_code:
import subprocess, json, os
scripts = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/python/Scripts")
xhs = os.path.join(scripts, "xhs.exe")

# Search → return note IDs
r = subprocess.run([xhs, "search", "topic", "--json"], capture_output=True, text=True, timeout=30)
notes = json.loads(r.stdout)["data"]["items"]
note_ids = [n["id"] for n in notes[:5]]

# Read a note
r = subprocess.run([xhs, "read", note_ids[0]], capture_output=True, text=True, timeout=30)

# Verify login before actions
r = subprocess.run([xhs, "status"], capture_output=True, text=True, timeout=10)
is_ok = "authenticated: true" in r.stdout
if is_ok:
    r = subprocess.run([xhs, "like", note_ids[0]], capture_output=True, text=True, timeout=15)
```

## Error Handling

- Commands exit with code 0 on success, non-zero on failure
- Error messages are prefixed with ❌
- Login-required commands show clear instruction to run `xhs login`
- `xsec_token` is auto-resolved from cache; manual `--xsec-token` available as fallback

## Pitfalls

- **`guest: true` in `xhs whoami`** means the cookie is an anonymous/guest session, NOT a real login. The user must complete the QR scan + redirect login flow. Do NOT proceed with authenticated actions (search, read) if `guest: true` — the XHS API returns error code `-104` ("账号没有权限访问").
- **Real login detection**: After QR scan, `xhs status` should show `guest: false` (or no `guest` field at all) and `xhs whoami` should show the user's real nickname (e.g. `麦兜`), not `Unknown`.
- **Windows git-bash terminal garbled output**: On this Hermes runtime (git-bash/MSYS), `terminal()` tool produces binary-garbled output for xhs subprocess calls. Always use `execute_code` with Python `subprocess.run(capture_output=True, text=True, timeout=...)` instead.
- **xhs executable path**: Not on system PATH. Full path: `~/.hermes-web-ui/desktop-runtime/hermes/<version>/win-x64/python/Scripts/xhs.exe`. Construct programmatically via `os.path.expanduser(...)`.
- **Login flow requires user at screen**: QR code login opens a browser window on the user's desktop. The agent cannot complete this alone — the user must physically scan with their phone.

## Safety Notes

- Do not ask users to share raw cookie values in chat logs.
- Prefer auto-extraction via `xhs login` over manual cookie input.
- If auth fails, ask the user to re-login via `xhs login`.
- **Verify real login**: `xhs whoami` should show a real nickname, not `guest: true`. If `guest: true`, the cookie is anonymous — user needs to actually scan the QR code and complete the login flow.
- **Call from execute_code, not terminal**: On Windows (git-bash), `terminal` tool may produce binary garbled output for xhs commands. Use `execute_code` with Python `subprocess.run()` instead, which reliably captures UTF-8 output.
