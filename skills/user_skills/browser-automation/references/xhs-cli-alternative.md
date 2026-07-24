# xhs-cli — Browserless Xiaohongshu Content Ingestion

Discovered 2026-07-09. Alternative to browser-based scraping for Xiaohongshu (小红书/RedNote) content.

## Overview

**Repository**: https://github.com/jackwener/xhs-cli  
**Stars**: 598 ⭐  
**Tech**: Python + camoufox (anti-fingerprint Firefox, headless)  
**Author**: jackwener (also maintains twitter-cli, bilibili-cli)

## Key Capabilities

| Feature | Command | Notes |
|---------|---------|-------|
| Search notes | `xhs search "query"` | Rich table or `--json` output |
| Read note | `xhs read <note_id>` | Supports `--comments` flag |
| User profile | `xhs user <user_id>` | Uses internal hex user_id |
| User posts | `xhs user-posts <user_id>` | List published notes |
| Feed | `xhs feed` | Explore page recommendations |
| Like/Favorite/Comment | `xhs like / favorite / comment` | Requires login |
| Post | `xhs post "title" --image path` | Publish image notes |

## Installation (Hermes Bundled Python)

On Hermes Studio (Windows), install into bundled Python — `uv tool install` doesn't add to system PATH:

```bash
uv pip install --python <bundled-python-path> xhs-cli
```

Where `<bundled-python-path>` is typically:
```
C:\Users\<user>\.hermes-web-ui\desktop-runtime\hermes\<version>\win-x64\python\python.exe
```

The `xhs.exe` appears at `<bundled-python-dir>/Scripts/xhs.exe` and must be called via full path from `execute_code`. See the `xhs-cli` skill for details.

System-wide install (alternative):
```bash
uv tool install xhs-cli
# or: pipx install xhs-cli
```

Requires Python 3.8+.

## Authentication

```bash
xhs login              # Auto-extract Chrome cookies (recommended)
xhs login --qrcode     # QR code login (fallback)
xhs status             # Quick saved-session check (no browser needed)
```

Cookies stored at `~/.xhs-cli/cookies.json` (0600 permissions). Re-login every few months.

## Hermes Integration

The repo ships with a `SKILL.md` — register it as a Hermes skill:

```bash
# Option A: Copy the SKILL.md
mkdir -p ~/.hermes/skills/xhs-cli
curl -o ~/.hermes/skills/xhs-cli/SKILL.md \
  https://raw.githubusercontent.com/jackwener/xhs-cli/main/SKILL.md

# Option B: /learn command (Hermes 0.17+)
# Send /learn with the SKILL.md URL
```

## When to Use vs Browser Automation

| Factor | real-browser-mcp | xhs-cli |
|--------|-----------------|---------|
| Platform | Any website | XiaoHongShu only |
| Speed | Slow (full browser) | Fast (headless firefox) |
| Detection risk | Higher | Lower (camoufox) |
| Login persistence | Browser cookies | Dedicated cookie file |
| Complexity | High (MCP crashes) | Low (CLI tool) |
| Hermes skill | Custom setup | Built-in SKILL.md |

## Faster Alternative (API-based)

https://github.com/jackwener/xiaohongshu-cli — reverse-engineered API version. Faster but more likely to be blocked by Xiaohongshu risk control.

## Related Tools (same author)

- https://github.com/jackwener/twitter-cli — X/Twitter CLI
- https://github.com/jackwener/bilibili-cli — Bilibili CLI
