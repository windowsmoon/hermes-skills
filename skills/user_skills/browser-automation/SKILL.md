---
name: browser-automation
description: >
  当用户需要自动操作浏览器（导航/点击/填写/截图）时使用。
  支持：页面导航、元素交互、截图、结合视觉/LLM理解页面、滚动加载。
  不要用于：API调用/数据爬取（走专门采集工具）、反爬网站（走Tabbit Browser）。
  触发词：自动操作浏览器、帮我打开网页、自动填写表单、网页截图
triggers:
  - browser automation
  - 浏览器自动化
  - 网页数据采集
  - web scraping
  - open webpage
  - 打开网页
  - 关闭弹出广告
  - 翻页采集
  - 关闭弹出广告
  - 翻页采集
tags: [browser, automation, web, scraping, vision, data-collection]
version: 1
---

# Browser Automation (Hermes)

## Overview

Hermes provides browser automation via a Playwright-based toolset. Browser tools can open pages, interact with elements, take screenshots, and read console output. Combined with vision models or direct DOM parsing, this enables end-to-end web workflows.

**Two browser backends are available:**

1. **Built-in Hermes browser** (headless cloud Browserbase) — Default. Cannot see user's existing login sessions.
2. **real-browser-mcp** (browser extension + MCP server) — Connects to the user's local Edge/Chrome with existing sessions and cookies intact. **Preferred for login-protected sites.**

## Available Browser Tools

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Open a URL and load the page |
| `browser_snapshot` | Get page element tree (interactive elements with ref IDs) |
| `browser_click` | Click an element by ref ID |
| `browser_type` | Type text into an input field |
| `browser_scroll` | Scroll up or down |
| `browser_press` | Press a keyboard key |
| `browser_vision` | Screenshot + analyze page with vision model |
| `browser_console` | Read JS console logs and errors |
| `browser_back` | Navigate back in history |
| `browser_get_images` | List all images on the page |

`browser_vision` requires a vision provider configured in `config.yaml`. If the configured API key is invalid or missing, it returns `401 - Incorrect API key provided`. See the Vision Configuration section below.

---

## Data Collection Workflow (Complete)

### Step-by-step Pattern

```
1. browser_navigate(url)                    → Open the target page
2. [If login required: user completes auth in Hermes browser, then signals "done"]
3. browser_snapshot() + browser_vision()     → Understand page structure
4. browser_click(close_popup_ref)            → Dismiss popup ads
5. browser_click(filter_btn_ref)             → Apply filters
6. browser_snapshot(full=true)               → Read data from DOM
7. Loop: browser_click(next_page_ref) + browser_snapshot()
8. Write data to destination (Feishu, CSV, etc.)
```

> ⚠️ **Important**: Steps 1 and 2 are separate. Do NOT assume the user is logged in just because they say "I've logged in" — they must log in inside the Hermes browser window that appears. Their Edge/Chrome session does not carry over.

### DOM Parsing vs Vision — When to Use Which

| Approach | Use When |
|----------|----------|
| `browser_snapshot` + text extraction | Normal structured pages (tables, lists, divs with text). **Faster, more accurate, always preferred.** |
| `browser_vision` | CAPTCHA images, canvas-rendered charts, complex visual layouts where DOM parsing fails, or when the page is heavily obfuscated. |

**Prefer DOM parsing over vision for data collection.** Vision is slower, more expensive, and less reliable for structured data.

### Handling Pagination

```python
# Pseudocode pattern for auto-pagination
for page in range(max_pages):
    snapshot = browser_snapshot(full=True)  # Read current page data
    collect_data(snapshot)
    
    # Try to find and click next page button
    if has_next_button(snapshot):
        browser_click(next_btn_ref)
        time.sleep(2)  # Wait for page to load
    else:
        break
```

### Handling Popups and Ads

```python
# Always snapshot first to find close buttons
snapshot = browser_snapshot()

# Look for common close button patterns:
# - Modal close: button with aria-label="close", "×", "Close", "取消"
# - Overlay close: click outer div to dismiss
# - Cookie banner: "Accept", "我知道了", "知道了"

# Try common close button refs found in snapshot
browser_click(close_ref)  # e.g., ref=e99 for close button
```

---

## Vision Configuration

`browser_vision` and `vision_analyze` require a **vision provider** in `config.yaml`. Without one, they fail with `401 - Incorrect API key provided`.

### Config Location
```
C:\Users\Admin\AppData\Local\hermes\config.yaml
```

### Adding a Vision Provider (e.g., Alibaba DashScope Qwen-VL)

Add a `custom_providers` entry:

```yaml
custom_providers:
  - name: 'qwen-vl'
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key: "sk-YOUR-API-KEY"
    model: qwen3-vl-plus    # or qwen-vl-plus, qwen-vl-max, qvq-max
    api_mode: chat_completions
```

**After editing `config.yaml`, restart Hermes Desktop** for the change to take effect.

### Common Vision Models

| Provider | Model Examples |
|----------|---------------|
| Alibaba DashScope | `qwen-vl-plus`, `qwen-vl-max`, `qwen3-vl-plus`, `qvq-max` |
| OpenAI | `gpt-4o`, `gpt-4o-mini` |
| OpenRouter (many) | Various models via OpenRouter API |

### Testing Vision After Config

```python
# Navigate to a test page
browser_navigate("https://www.baidu.com")

# Try vision analysis
browser_vision(question="Describe the page")
# If still 401: config not loaded, restart Hermes
```

---

## CRITICAL: Hermes Browser Is an Independent Headless Session

**The browser I control (Hermes) and the user's browser (Edge/Chrome) are TWO SEPARATE PROCESSES.**

- If the user is logged into a site in their Edge/Chrome, that session does NOT carry over to Hermes's browser.
- When I use `browser_navigate`, I open a **fresh, logged-out session**.
- **Hermes uses a headless (no visible window) Playwright/browserbase browser.** The user cannot see or interact with it directly — there is no Edge/Chrome window to control.
- **There is no configuration option** to make Hermes control the user's existing Edge/Chrome window. They are architecturally separate.
- **DO NOT tell the user "please log in in the browser window that just opened"** — there is no visible window, the user CAN'T see it. Be upfront about this.

### The `/browser connect` Command (Requested Feature — Not Yet Working)

The user may know of or reference a `/browser connect` command that supposedly connects Hermes to a local browser. **This is not currently implemented.** The theoretical workflow would be:

```bash
# 1. Start Edge/Chrome with debug port
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run --no-default-browser-check &

# 2. Configure Hermes toolsets
hermes config set toolsets '["hermes-cli", "browser"]'

# 3. In Hermes CLI chat, run:
/browser connect
```

**Status**: This feature does NOT currently exist in Hermes. The CDP/Browser Extension approach exists in upstream Playwright but is not wired into Hermes's browser toolset. When the user references this, acknowledge it as a requested/planned capability, not current reality.

### Headed Browser from execute_code: Window Will NOT Appear (Confirmed)

**Confirmed limitation on this system (2026-07-22):** Launching a headed browser (e.g., CloakBrowser `headless=False`) from within `execute_code` or `terminal` does NOT show the browser window on the user's desktop. The process starts correctly (PID exists, page loads) but the GUI window is suppressed by the sandbox.

**This affects ALL headed browser launches:** CloakBrowser, Playwright, Puppeteer, Selenium — any tool that opens a visible browser window. The window simply never appears.

**Solution: Provide a Desktop batch file** that the user double-clicks. This runs outside the Hermes sandbox so the window appears normally:

```batch
@echo off
"C:\path\to\python.exe" -c "
from cloakbrowser import launch
import time, json, os
b = launch(headless=False, humanize=True)
p = b.new_page()
p.goto('https://target-site.com')
print('Browser opened. Login in the window, then press Enter...')
input()
# Save session
cookies = b.context.cookies()
storage = b.context.storage_state()
save_dir = os.path.expanduser(r'~\AppData\Local\hermes\cloakbrowser_sessions')
os.makedirs(save_dir, exist_ok=True)
with open(os.path.join(save_dir, 'session_cookies.json'), 'w') as f: json.dump(cookies, f)
with open(os.path.join(save_dir, 'session_storage.json'), 'w') as f: json.dump(storage, f)
print(f'Session saved: {len(cookies)} cookies')
input('Press Enter to close browser...')
b.close()
"
pause
```

The batch file must use `"C:\path\to\python.exe"` (fully-qualified path to the correct Python) and wrap multi-line Python in quotes or a separate `.py` file.

**DO NOT use `subprocess.Popen` with `creationflags=subprocess.CREATE_NO_WINDOW`** — this deliberately hides windows. Use `Popen(shell=True)` or `start "" /b` if launching from terminal.

### Scrapling + CloakBrowser CDP Integration (New 2026-07-22)

**Architecture overview:**

```
用户 → 双击bat脚本 → CloakBrowser 启动（headful, 带CDP端口9222）
     → 手动登录目标网站
     → 告诉我"帮我抓这个"
     ↓
Hermes → Python 脚本通过 Playwright connect_over_cdp 连上 CloakBrowser
     → 使用已登录的会话（无需重复登录）
     → 自动滚动/翻页/提取数据
     → 写入飞书多维表格
```

**关键原理：** Playwright 的 `connect_over_cdp()` 可以连接到已运行的 Chromium 浏览器实例。CloakBrowser 是 Chromium 的修改版，所以同样支持 CDP 连接。

**启动脚本模板（存为 `C:\Users\Admin\Desktop\启动CloakBrowser.bat`）：**

```batch
@echo off
chcp 65001 >nul
echo 正在启动 CloakBrowser ...
cd /d D:\hermes-data
.venv\Scripts\python.exe -c "
from cloakbrowser import launch
import json, os
b = launch(
    headless=False,
    humanize=True,
    args=[
        '--remote-debugging-port=9222',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-blink-features=AutomationControlled'
    ]
)
p = b.new_page()
p.goto('about:blank')
print('✅ CloakBrowser 已启动，CDP 端口 9222')
print('请手动登录目标网站，然后按 Enter 继续...')
input()
# 持久化 session
cookies = b.context.cookies()
storage = b.context.storage_state()
save_dir = os.path.expanduser(r'~\.hermes\cloakbrowser_sessions')
os.makedirs(save_dir, exist_ok=True)
with open(os.path.join(save_dir, 'cookies.json'), 'w') as f: json.dump(cookies, f)
with open(os.path.join(save_dir, 'storage.json'), 'w') as f: json.dump(storage, f)
print(f'✅ Session 已保存: {len(cookies)} cookies')
input('按 Enter 关闭浏览器...')
b.close()
"
pause
```

**自动化采集脚本（Hermes 通过 execute_code 运行）：**

```python
from playwright.sync_api import sync_playwright

# 1. 连接到已运行的 CloakBrowser
with sync_playwright() as pw:
    browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    
    # 2. 获取当前已登录的页面
    page = browser.contexts[0].pages[0]  # 或 browser.new_page()
    
    # 3. 导航到目标页
    page.goto("https://target-site.com/data-page")
    page.wait_for_load_state("networkidle")
    
    # 4. 自动滚动加载更多
    for _ in range(5):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
    
    # 5. 提取数据
    items = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('.item')).map(el => ({
            title: el.querySelector('.title')?.textContent?.trim(),
            price: el.querySelector('.price')?.textContent?.trim(),
            url: el.querySelector('a')?.href
        }))
    }""")
    
    # 6. 翻页
    while page.locator('.next-page:not(.disabled)').count() > 0:
        page.locator('.next-page').click()
        page.wait_for_load_state("networkidle")
        # 提取更多数据...
    
    print(f"✅ 共采集 {len(items)} 条数据")
```

**也可以结合 Scrapling 的 CSS 解析能力：**

```python
from playwright.sync_api import sync_playwright
from scrapling import StealthyFetcher

with sync_playwright() as pw:
    browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://target-site.com")
    
    # 获取 HTML，用 Scrapling 解析
    html = page.content()
    parser = StealthyFetcher._parse_html(html)
    items = parser.css('.item-class').extract()
```

**配套文件：** `references/scrapling-cloakbrowser-cdp.md` 包含完整安装和测试记录。

### CloakBrowser: No MCP/Plugin/API (Python Library Only)

**Confirmed (2026-07-22):** CloakBrowser is a Python library only. It does NOT provide:
- ❌ **MCP Server** — cannot be added via `hermes mcp add`
- ❌ **Hermes Plugin** — cannot be enabled via `hermes tools enable`
- ❌ **Standalone API** — no REST/HTTP endpoints
- ❌ **Browser Automation CLI** — its CLI (`cloakbrowser install/info/doctor/update/clear-cache`) only manages the binary

The ONLY way to use CloakBrowser from Hermes is via `execute_code` with Python code.

**Example:** `from cloakbrowser import launch` then use standard Playwright API.

**Free tier limitation:** The free version (Chromium v146) does NOT pass all bot detection tests. `bot.incolumitas.com` detected it even in headed mode. Pro tier (v150, paid) with 71 patches is required for full evasion.

**For Login-Protected Sites: Immediate Pivot Required**

For sites requiring phone/SMS verification, QR code scan, or CAPTCHA:
- The user **cannot see** the Hermes headless browser to complete auth
- QR code scan requires the user to open Douyin/Taobao app on their phone and scan a code they can't see
- **SMS verification is theoretically possible** but only if the user can see the code input field (they can't, because headless)

**When login is required, pivot IMMEDIATELY to the export workaround. Do not spend time attempting headless browser login for platforms like 巨量百应, 抖音, 淘宝 that require phone/SMS verification.**

**Practical workflow for authenticated sites:**
```
1. Agent: "Hermes uses a headless (invisible) browser. Since this site requires login, the most reliable approach is: (A) you log in your Edge and export data, or (B) I use lark-cli to write data. Which do you prefer?"
2. If user picks A: ask them to export/notify when ready
3. If user picks B: proceed with lark-cli Feishu setup
```

### Workaround: Ask the User to Export Data

For sites with strong anti-automation (DOUYIN/JINRITEMAI level), the most reliable approach is often:
1. User logs in manually in their own Edge/Chrome (fully visible, no headless barrier)
2. User exports data (CSV/Excel download, or copy-paste)
3. Agent processes the exported data and writes to destination

This completely avoids the browser authentication problem and is often faster than debugging headless login issues.

---

## Research: Local Browser Control (Future Capability)

> **Date**: 2026-07-08 | **Status**: Not currently supported by Hermes

Playwright supports controlling existing local browsers via CDP (Chrome DevTools Protocol) or Browser Extension:
- **CDP**: `chromium.connectOverCDP("ws://localhost:9222")` — requires browser launched with `--remote-debugging-port`
- **Browser Extension** (simpler): `https://playwright.dev/mcp/configuration/browser-extension` — no special flags needed, connects via extension

**This means local Edge/Chrome control is technically possible.** The limitation is architectural — Hermes's browser tools run on a cloud/headless Browserbase instance, not via a local Playwright installation that could attach to the user's existing browser.

If Hermes adds support for local CDP/Browser Extension connection in the future, the workflow for login-required sites (particularly Chinese platforms with SMS verification) would become viable.

**NEVER assume the user is already logged in just because they said so. They must authenticate in Hermes's browser session.**

---

### Quick Fix for Vision 401 Errors

```bash
# Set correct vision model (e.g., qwen-vl-plus)
hermes config set auxiliary.vision_model qwen-vl-plus

# Or if the config path is different, edit config.yaml directly:
# Find "auxiliary.vision_model" or "Auxiliary Models" section
# Change the Vision model from MiniMax-M3 (TEXT MODEL - WRONG) to a real vision model

# Restart Hermes Desktop for changes to take effect
```

> ⚠️ **Confirmed bug on this system (2026-07-08):** Config shows `Vision provider=custom:183399, model=MiniMax-M3`. `MiniMax-M3` is a **text model**, not a vision model. This causes all `vision_analyze` and `browser_vision` calls to fail with `401 - Incorrect API key provided`. The correct model to use is `qwen3-vl-plus` from the `qwen-vl` custom provider already configured.

---

## Verified Windows Edge Debug Startup Command

To start Edge with debug port on Windows:

```powershell
# PowerShell (verified working on this system 2026-07-08)
$debugDir = "$HOME\.hermes\edge-debug"
New-Item -ItemType Directory -Path $debugDir -Force | Out-Null

& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
    --remote-debugging-port=9222 `
    --user-data-dir="$debugDir" `
    --no-first-run `
    --no-default-browser-check `
    --new-window "https://target-site.com/"

# Verify it's running:
curl http://localhost:9222/json/version
# Expected: {"Browser": "Edg/150.x.x.x", "Protocol-Version": "1.3", ...}
```

Edge executable path (Windows x64): `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`

---

## computer_use Toolset Check

Hermes has a `computer_use` toolset. Check if it provides better local browser access:

```bash
hermes computer-use status    # Is cua-driver installed?
hermes computer-use doctor    # Run health checks
hermes computer-use install   # Install/repair if needed
```

---

## Content Ingestion Alternatives (Platform CLI Tools)

When browser automation is unreliable or blocked, platform-specific CLI tools provide faster, lower-detection alternatives:

| Platform | Tool | Approach | Install | Reference |
|----------|------|----------|---------|-----------|
| 小红书 (Xiaohongshu / RedNote) | `xhs-cli` | Camoufox headless Firefox (anti-fingerprint); or API-based `xiaohongshu-cli` | `uv pip install xhs-cli` into Hermes bundled Python | `xhs-cli` skill |
| 小红书 (API) | `xiaohongshu-cli` | Reverse-engineered API (faster, more detectible) | `uv tool install xiaohongshu-cli` | Same reference |
| X/Twitter | `twitter-cli` | Same author pattern | `uv tool install twitter-cli` | [GitHub](https://github.com/jackwener/twitter-cli) |
| Bilibili | `bilibili-cli` | Same author pattern | `uv tool install bilibili-cli` | [GitHub](https://github.com/jackwener/bilibili-cli) |

All ship with `SKILL.md` files for `/learn` import into Hermes.

**When to pivot from browser automation:** MCP crashes (`ClosedResourceError`), anti-bot detection, login/SMS auth walls, slow/infinite scroll, and any site with strong risk control (巨量百应, 小红书, 抖音). The CLI tools are faster and more reliable for structured data.

## Key Files

| Purpose | Path |
|---------|------|
| Hermes config | `C:\\Users\\Admin\\AppData\\Local\\hermes\\config.yaml` |
| Hermes CLI | `C:\\Users\\Admin\\.hermes-web-ui\\desktop-runtime\\hermes\\0.18.0\\win-x64\\python\\Scripts\\hermes.cmd` |
| Edge executable (Windows) | `C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe` |
| Browser cache | `C:\\Users\\Admin\\AppData\\Local\\hermes\\cache\\screenshots\\` |
| real-browser-mcp repo | `D:\\SetupProgram\\real-browser-mcp-main` |
| real-browser-mcp Windows fix | `references/real-browser-mcp-windows-fix.md` |
| local HTML+Node.js patterns | `references/local-html-nodejs-debug.md` |
| 巨量百应爆款视频采集参考 | `references/jinritemai-hot-video-collection.md` |
| CloakBrowser vs Tabbit comparison | `references/cloak-browser-vs-tabbit.md` |

---

## real-browser-mcp: Connect to User's Local Browser (Solved)

**Problem:** Hermes's built-in browser is a headless cloud instance. The user cannot see it, and their Edge/Chrome login sessions do NOT carry over.

**Solution:** `real-browser-mcp` is an MCP server + browser extension that gives Hermes control of the user's **actual, locally-running Edge/Chrome** with all existing sessions and cookies intact. This solves the login problem for sites like 巨量百应, 抖音, 淘宝 that require SMS/QR verification.

### Install Steps (Verified on this system 2026-07-08)

#### Step 1: Build the MCP server

```bash
cd D:\SetupProgram\real-browser-mcp-main
npm install
npm run build
```

The built server is at `mcp-server/dist/index.js`.

#### Step 2: Add to Hermes MCP

```bash
hermes mcp add real-browser --command "C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\node\node.exe" --args "D:\SetupProgram\real-browser-mcp-main\mcp-server\dist\index.js"
# When prompted "Enable all 22 tools? [Y/n/select]:" press Y
```

**Output looks like:**
```
✓ Connected! Found 22 tool(s) from 'real-browser':
  browser_navigate, browser_click, browser_type, browser_scroll, ...
✓ Saved 'real-browser' to ~/AppData\Local\hermes/config.yaml (22/22 tools enabled)
Start a new session to use these tools.
```

#### Step 3: Install browser extension

1. Open Edge → `edge://extensions`
2. Enable **Developer mode** (toggle top right)
3. Click **Load unpacked**
4. Select `D:\SetupProgram\real-browser-mcp-main\extension`

#### Step 4: Restart Hermes Desktop

New sessions will have access to the 22 real-browser-mcp tools.

#### Step 5: Connect

1. Open Edge with Real Browser MCP icon in toolbar
2. Click the icon — **Green dot** = connected, **Gray dot** = waiting
3. Now Herme's browser tools operate on the user's actual Edge with all sessions intact

### How It Works

| Component | Role |
|-----------|------|
| MCP server (`mcp-server/dist/index.js`) | Runs on local machine, bridges Hermes ↔ browser extension |
| Browser extension (`extension/`) | Runs in Edge tab, executes commands via Chrome DevTools Protocol |
| WebSocket connection | Server ↔ Extension communication |

### Real-browser-mcp Available Tools (22 total)

`browser_navigate`, `browser_click`, `browser_type`, `browser_scroll`, `browser_press_key`, `browser_wait`, `browser_snapshot`, `browser_screenshot`, `browser_console`, `browser_network`, `browser_tabs`, `browser_find`, `browser_text`, `browser_hover`, `browser_select`, `browser_evaluate`, `browser_click_text`, `browser_handle_dialog`, `browser_upload_file`, `browser_run_action`, `browser_drag`, `browser_fill_form`

### Comparison: Hermes Built-in vs real-browser-mcp

| | Hermes built-in | real-browser-mcp |
|---|---|---|
| Browser type | Headless cloud (Browserbase) | User's local Edge/Chrome |
| User sees it? | ❌ No | ✅ Yes |
| Sessions/cookies | Fresh, logged-out | Existing user sessions |
| Works behind SSO? | ❌ No | ✅ Yes |
| Setup | None (default) | Extension + MCP config |
| Login-protected sites | ❌ Cannot complete | ✅ Fully works |
| Anti-bot detection | Higher | Lower (real browser) |

### Workflow for Login-Protected Sites

```
1. Verify real-browser-mcp is installed and connected (green dot in Edge)
2. browser_navigate("https://target-site.com") 
   → Opens in USER's Edge, user is already logged in
3. browser_snapshot() / browser_click() / browser_screenshot()
   → All operate on the user's actual logged-in session
4. Collect data, write to Feishu via lark-cli
```

### ⚠️ CRITICAL: Windows Bug in bridge.js — Must Patch Before Use

**Root cause (confirmed 2026-07-08):** `bridge.js`'s `killStaleProcess()` uses `lsof` to find and kill stale processes blocking port 7225. On Windows, `lsof` does not exist — the error silently passes, so the stale process is never killed, and the server crashes in a loop:

```
[Bridge] Server error: listen EADDRINUSE: address already in use 127.0.0.1:7225
[Bridge] Port 7225 in use — killing stale process
'lsof' 不是内部或外部命令...
[real-browser-mcp] Fatal: Error: listen EADDRINUSE: address already in use 127.0.0.1:7225
```

**The patch is already applied** to `D:\SetupProgram\real-browser-mcp-main\mcp-server\dist\bridge.js` on this system — it adds a Windows-specific `netstat + taskkill /F` fallback after the `lsof` block. If you ever reinstall/overwrite the bridge.js file, re-apply the patch from `references/real-browser-mcp-windows-fix.md`.

**The fix also applies after Hermes restarts:** Hermes Desktop may spawn multiple MCP server processes. When one crashes (EADDRINUSE), Hermes retries immediately — without the patch, this creates an infinite crash loop. With the Windows taskkill fix, the stale process is properly killed and the server starts successfully.

**To verify the fix is in place:**
```javascript
// In bridge.js, look for "taskkill /PID" — if present, the fix is applied
grep "taskkill" D:/SetupProgram/real-browser-mcp-main/mcp-server/dist/bridge.js
```

### ⚠️ Configured ≠ Loaded: MCP Session Loading Bug

**Confirmed issue (2026-07-08):** Even when real-browser-mcp is in `config.yaml` AND the Edge extension shows green (connected), the 22 real-browser-mcp tools may NOT appear in the active session's tool list. `browser_navigate` still routes to Hermes's built-in headless browser instead.

**Why this happens:** MCP servers are loaded when the session initializes. Adding or updating an MCP entry in config.yaml does NOT reload it in the current session — only in future sessions.

**Fix — one of these (try in order):**

1. **Start a completely new Hermes Studio session** (new tab or new session — not just a new turn). The MCP tools should load on session initialization.
2. If that fails: **restart Hermes Desktop entirely**, then open a new session.
3. Verify tools loaded: try calling a real-browser-mcp-specific tool like `mcp_real_browser_browser_tabs` — if Hermes says "MCP call failed: ClosedResourceError()", the MCP didn't load.
4. **Alternative confirmation:** If `browser_navigate` result includes `stealth_warning: "Running WITHOUT residential proxies"`, you're on the Hermes built-in browser. If no such warning and the page shows the user's actual logged-in state, it worked.

### Session Loading: real-browser-mcp Tools Appear After Restart

**Confirmed (2026-07-08):** After `hermes mcp add real-browser`, the tools are written to `config.yaml` but do NOT appear in the current session. A **new Hermes Studio session** or **full Hermes Desktop restart** is required.

**Verification:** In a new session, try `browser_tabs(action='list')`. If it returns tab data → tools loaded. If `ClosedResourceError` → server not ready (see Full Restart Procedure).

**User-side signal:** The user confirmed the Edge extension shows a **green dot** (connected) after restarting Hermes Desktop.

### How It Works

## Pitfalls

1. **MiniMax-M3 is NOT a vision model** — It's a text model. Setting it as the Vision model causes 401 errors. The fix requires editing `config.yaml` under `auxiliary.vision` to use `qwen3-vl-plus` from the `qwen-vl` custom provider (already configured). Restart Hermes after editing. This was confirmed broken on this system (2026-07-08).
2. **Hermes browser ≠ user's browser** — They are separate processes. If the user says "I'm logged in", that means nothing for my browser session. I must wait for them to authenticate in the Hermes browser window.
3. **Vision tools return 401** — Usually caused by wrong vision model (MiniMax-M3 instead of qwen3-vl-plus). See Vision Configuration section above.
4. **Wrong model name** — Check DashScope/OpenRouter for exact model IDs. `qwen3-vl-plus` may not exist; common names are `qwen-vl-plus`, `qwen-vl-max`.
5. **Login/auth not automated** — For pages requiring login, the user should complete auth manually first, then signal the agent to continue.
6. **Pagination timing** — Add `time.sleep` or wait for specific element to appear after clicking "next page" before snapshotting.
7. **browser_snapshot full=true is large** — For pages with many elements, it may be truncated. Use selective clicks and targeted snapshots instead.
8. **Popup close buttons are one-time** — Popups often regenerate; always check for them on each page load.
9. **Hermes browser uses Browserbase cloud** — Stealth warnings (`Running WITHOUT residential proxies`) are expected. Some sites may detect automation.
10. **Page redirects after navigate** — Some sites (e.g., jinritemai.com) redirect to a different domain after loading. Always verify the final URL with `browser_console` before collecting data.
11. **Headless browser is invisible to user** — The Hermes built-in browser has no visible window. For login-protected sites, use `real-browser-mcp` instead (see section above). The built-in browser should only be used for public/no-login pages.
12. **For SMS/captcha login sites, use real-browser-mcp** — Don't use the built-in headless browser. Install real-browser-mcp and use that — it connects to the user's actual Edge with existing sessions.
13. **Terminal encoding on Windows** — Chinese characters in terminal output appear garbled (`�|�~~b\rN0R`). Use `execute_code` (Python) instead of `terminal` for reliable output handling on Windows.
14. **`/browser connect` command does not exist** — Use `real-browser-mcp` instead (see section above). It provides the same capability via MCP + browser extension architecture.
15. **Vision model MiniMax-M3 is NOT a vision model** — It's a text model. Set `auxiliary.vision.provider: custom:qwen-vl` and `auxiliary.vision.model: qwen3-vl-plus` in config.yaml. Restart Hermes after editing. See Vision Configuration section.
16. **real-browser-mcp config in config.yaml ≠ tools loaded in session** — Adding/editing the MCP entry in config.yaml does NOT take effect in the current session. You must start a **new** session or restart Hermes Desktop. Confirmed on this system 2026-07-08. See "⚠️ Configured ≠ Loaded" section above.
17. **User is running Hermes Studio (Desktop GUI), not Hermes Desktop** — Hermes Studio sessions initialize MCP servers from `config.yaml`. The MCP server must be **successfully running** (port 7225 bound, WebSocket server listening) BEFORE a new Studio session starts — otherwise the session initializes with no tools and `ClosedResourceError()` results on every real-browser-mcp tool call. Always verify with a test call first.
18. **HTML-based dev tools opened via `file://` fail with "Failed to fetch"** — When a local Node.js server serves an HTML frontend that calls `fetch('/api/...')`, the HTML MUST be opened through the server (`http://localhost:PORT/page.html`), not from the filesystem (`file:///path/to/page.html`). Via `file://`, the relative URL `/api/...` resolves to `file:///api/...` which doesn't exist. Fix: add auto-redirect in the HTML head:
    ```html
    <script>
    if (window.location.protocol === 'file:') {
      window.location.href = 'http://localhost:PORT/page.html';
    }
    </script>
    ```
    This is common with local HTML+Node.js tools (code generators, dashboards, etc.).
20. **Multiple local Node.js servers need different ports** — If running two Node.js dev servers on the same machine, assign distinct ports (e.g., 5000 and 5001). Port conflicts cause "EADDRINUSE" and silent failures.
21. **巨量百应 爆款视频 page has interleaved UI text** — The page uses floating/overlay UI (filter sidebar, header area, right-side menus) that interleaves with data content in `browser_text` output. Text order in DOM reflects layer order, not visual row order. Parse by splitting on unique **label markers** (e.g., `"总播放量"`, `"已选类目结算金额"`, `"总点赞量"`) rather than by line position. Each video block starts with the `"总播放量"` label. This is more robust than assuming fixed line counts.
22. **巨量百应 API tokens (`msToken`, `a_bogus`) are session-specific and non-reusable** — The `search_videos` API endpoint requires dynamic tokens generated per-request by the browser. These cannot be extracted from network requests and reused in standalone scripts — they expire immediately and are bound to the session. The only reliable way to call this API is from within the live browser session (via `browser_evaluate` with `fetch()`) or by having the user export manually from the UI.
23. **巨量百应 爆款视频: no independent product title field** — The page does not show a separate "商品标题" field in the video card UI. Product info must be inferred from: (1) the video title's hashtags (e.g., `#凉凉裤` → product is "凉凉裤"), (2) the video summary text below the author info, (3) the settlement amount which implies product category. Clicking into the video detail page is required to get the actual product title.
24. **巨量百应 爆款视频: no visible video URLs or IDs in the UI** — All video card interactions are internal SPA navigation. There are no visible URLs, video IDs, or share links in the card layout. To get the actual video link, you must click the ▶ play button on the card, which opens the video detail page.
25. **巨量百应: use label-marker splitting, NOT line-count parsing** — The page has floating sidebar UI (filters, headers) that interleaves with data content in `browser_text` output. Never assume a fixed line count per video block — the total varies depending on which sidebar items are open. Instead, split on the "总播放量" label marker (each video's data block starts right after this label). The correct structure:
   - `splits[0]` (before first "总播放量"): video 1 metadata — title/tag, author, time, duration, summary
   - `splits[1][:9]`: video 1 data — 播量数/万+, 播量数/万+, 已选类目结算金额/金额, 总点赞量/数/+
   - `splits[1][-5:]`: video 2 metadata (title/tag, author, time, duration, summary)
   - For videos 2–5: `splits[i][:9]` = data, `splits[i][-5:]` = next video metadata
   - `splits[5]`: video 5 data only (no trailing metadata)
   - Each video: {title_tag, author, time, duration, summary, plays1, plays2, settle_amt, likes}
   - Note: plays1 = total cumulative plays, plays2 = recent increase (both shown as 数字+万+ in two lines)
26. **evaluate returns empty even for document.cookie — this is a known limitation** — `browser_evaluate` with any expression on real-browser-mcp often returns {"success": true} with no data. Even trivial expressions like `document.title`, `location.href`, or `document.cookie` fail silently. Always use `browser_text(maxLength=20000)` for data extraction — it reads full DOM text and works reliably.

27. **MCP server restarted by Hermes ≠ fully operational** — When Hermes restarts the MCP server (e.g., after a crash), port 7225 may be bound by a new PID. The server accepts SOME calls (`browser_tabs` list succeeds) but FAILS all others with `ClosedResourceError`. This is an inconsistent state — the WebSocket channel for tool execution is broken while the port listener survives. **Do NOT keep retrying** — every subsequent call fails instantly. The fix is a **full manual restart** of the real-browser-mcp Node process (see "Full Restart Procedure" below).

28. **`browser_tabs` as diagnostic probe** — When real-browser-mcp tools are failing, try `browser_tabs(action='list')` first. If it returns tab data → server is partially alive. If it returns `ClosedResourceError` → server is fully dead. Use this to distinguish the two failure modes without wasting retries.

29. **Hermes built-in browser redirects authenticated URLs to login** — When `browser_navigate` is called with a login-required URL (e.g., `buyin.jinritemai.com/dashboard/...`) using the Hermes built-in browser, the page immediately redirects to the login page and stays there. The navigate result URL does NOT reflect this redirect — always check the page content. If the snapshot shows login/signup UI, real-browser-mcp is not loaded in this session.

30. **`ClosedResourceError` auto-retry cooldown** — After 3-4 consecutive MCP call failures, Hermes Desktop enforces an automatic cooldown (~30-45 seconds) before it will retry. **Do not issue any more real-browser-mcp calls during this window** — they'll all immediately fail. Wait for the cooldown to expire, then issue ONE test call (`browser_tabs`) to check recovery status.

### Full Restart Procedure (real-browser-mcp)

When the MCP server enters the inconsistent `ClosedResourceError` state:

1. **Close all Chrome/Edge browser windows** (the extension must be disconnected first)
2. **Kill all node.exe processes** — the MCP server does not exit cleanly on Windows. Use Task Manager → End Task on all `node.exe` entries, or run: `taskkill /F /IM node.exe` in a new terminal
3. **Wait 2-3 seconds** for port 7225 to fully release
4. **Start fresh** in a new terminal: `node mcp-server/dist/bridge.js` (from `D:\SetupProgram\real-browser-mcp-main`)
5. **Confirm startup output:** `[Bridge] Listening on ws://localhost:7225` → `[real-browser-mcp] WebSocket listening on ws://localhost:7225` → `[real-browser-mcp] Waiting for Chrome extension...`
6. **Open Edge** (with the real-browser-mcp extension loaded and enabled in `edge://extensions`)
7. **Verify green dot** in the extension icon — this confirms the extension is connected
8. **In a NEW Hermes Studio session** (or restart Hermes Desktop), verify tools are loaded: call `browser_tabs(action='list')` — should return tab data with no `ClosedResourceError`
9. **If still failing after restart:** Check `netstat -ano | findstr 7225` to confirm PID ownership changed from the old process to the new one (old PID = stale, new PID = live server)
25. **API keys in config files may be real strings, not masks** — When replacing API keys in `server.js`, the placeholder might be an actual string like `sk-7N8...i2h0` (not a display mask). Use regex substitution or binary replacement on the exact bytes, not text replacement. Example fix in Python:
    ```python
    import re
    content = re.sub(rb"(const KEY = ')[^']+(';)", rb"\\1" + new_key.encode() + rb"\\2", raw)
    ```
29. **`fetch('/api/...') returns "Failed to fetch" but server is running** — If the HTML page uses a JS variable like `apiKey: ***` where `***` is invalid JavaScript (e.g., accidentally generated from Python template syntax), the JS parser throws an error BEFORE the `fetch()` call is even made. The result is a silent "Failed to fetch" with no visible error in the page. Fix: open browser DevTools (F12 → Console) to see the actual JS error. Search the HTML source for Python template markers (`***`, `{{`, `${` that shouldn't be there) and replace them with valid JS variable names.
30. **CDN-hosted JS libraries (React, etc.) return 404** — Version numbers like `react@19.2.7` may not exist on jsdelivr/npm CDNs. Before assuming a URL is correct, verify it exists with `urllib.request.urlopen(url, timeout=5)` returning HTTP 200. If 404, try major versions that exist: `18.3.1`, `18.2.0`, `17.0.2` for React. This is common with recently-released library versions that haven't propagated to CDN caches.
31. **JS `***` triple-star is invalid syntax — check for Python template contamination** — If a Node.js server.js uses `apiKey: ***` (which can appear if a Python templating system generated the file), the browser sees `***` literally. In Python `f"apiKey: {***}"` where `***` is `Ellipsis` produces `apiKey: Ellipsis`, but when the file is read as plain text without Python evaluation, you get literal `apiKey: ***` which is a JavaScript SyntaxError. The page then shows "Loading..." forever with no console error visible without DevTools. Always inspect raw bytes: use Python `open(..., 'rb')` and check the exact hex/bytes of suspicious values. Replace with valid JS syntax.

### Verification: How to Tell Which Browser Is Active

| Signal | Browser |
|--------|---------|
| Result includes `stealth_warning: "Running WITHOUT residential proxies"` | Hermes built-in (headless cloud) — real-browser-mcp NOT loaded ❌ |
| Result shows user's actual logged-in page state, no stealth_warning | real-browser-mcp active ✅ |
| Tool call returns `MCP call failed: ClosedResourceError()` | MCP server not running or not connected — fix bridge.js or restart Hermes |
| Edge extension shows **green dot** | Extension is connected to the MCP server ✅ |

---

## Data Collection from Complex Pages (real-browser-mcp)

When collecting structured data from a complex page (e.g., 巨量百应 爆款视频), use a **multi-strategy approach**:

### Strategy 1: browser_text (Primary — Fastest)

```javascript
mcp_real_browser_browser_text(maxLength=20000)  // Get ALL visible text
```

`browser_text` returns the full page text in reading order. For pages with structured data (repeating card layouts), the data often appears as repeating text patterns. Extract by splitting on label markers:

```python
# Example: 巨量百应 爆款视频
# Each video block starts with "总播放量" label
sections = full_text.split('总播放量')
for section in sections[1:]:  # Skip header
    lines = section.strip().split('\n')
    # lines[0]: play count number
    # lines[1]: 万+
    # lines[2]: new plays number
    # lines[3]: 万+
    # lines[5]: settlement amount ("已选类目结算金额" value)
    # lines[8]: total likes number
    # lines[9]: +
```

**Limitation:** If the page has floating UI elements (popups, sticky headers) or interleaved menu text, the extraction becomes messy. `browser_text` reads ALL text in DOM order.

### Strategy 2: browser_network (For API-based Extraction)

The `browser_network(filter)` tool captures all XHR/fetch requests. For API-driven pages, the data is already in the network responses:

```
GET /api/anchor/creative/search_videos?industry_id=4&level=3&time_range_id=3&sort_id=2&page=1&page_size=10
→ Status 200, includes full video data JSON
```

**To get full structured data:**
1. Navigate to the page (user must be logged in via real-browser-mcp)
2. Apply filters in the UI (categories, time range, sort)
3. `browser_network(clear=true, filter="search_videos")` — clear old requests, wait for new ones
4. Parse the URLs: query parameters contain all filter values, response is the structured data
5. To get response body: intercept via `browser_evaluate` setting up a fetch interceptor, OR replicate the API call with session cookies

**⚠️ API Limitations:** The `search_videos` API endpoint uses dynamic tokens (`msToken`, `a_bogus`, `verifyFp`) that change every request. These cannot be reused across sessions — they must come from a live browser session. You cannot call these APIs directly without the session tokens from the user's logged-in browser.

### Strategy 3: vision_analyze + Screenshot (For Visual Structure)

```python
# Take screenshot first
mcp_real_browser_browser_screenshot(format="png", quality=80)
# Returns: MEDIA:path/to/screenshot.png

# Then analyze with vision model
vision_analyze(image_url="C:\\path\\to\\screenshot.png", 
               question="提取所有视频数据：博主、播放量、点赞数、结算金额")
```

This is useful for:
- Identifying the exact page structure (where are the cards? which field is where?)
- CAPTCHA / verification challenges
- Complex layouts where DOM parsing is impractical
- Getting the visual layout before writing DOM extraction code

### Workflow for Login-Protected Data Collection (e.g., 巨量百应)

```
1. browser_navigate(buyin_url)          → Opens in user's Edge, user is logged in
2. Apply filters manually OR via clicks → Set category, time range, sort
3. browser_text(maxLength=20000)        → Extract all visible data as text
4. Parse data from text pattern           → Group into records by label markers
5. If data is incomplete: 
   a. browser_network(filter="search_videos") → Capture API URLs for current filters
   b. OR click each video card → visit detail page → extract video link
6. Write to Feishu / CSV
```

### Key Insight: evaluate Returns Empty — Use text Instead

`browser_evaluate` on real-browser-mcp often returns empty `{"success": true}` with no data, even for simple expressions like `document.title`. This is a real limitation of the tool in this environment. **Use `browser_text()` instead** for data extraction — it reads the full DOM text and works reliably.

### ClosedResourceError Recovery Pattern

When real-browser-mcp tools return `ClosedResourceError`:

1. **Try `browser_tabs(action='list')` first** — this is a lightweight diagnostic that works even when the server is in an inconsistent state (partial restart). If it returns tab data → server partially alive. If it returns `ClosedResourceError` → server fully dead.
2. **Do NOT retry the same failing tool** — it will keep failing
3. **If partially alive:** Navigate to a fresh page (`browser_navigate`) — this often re-initializes the connection
4. **If fully dead (ClosedResourceError):** Full manual restart required — see "Full Restart Procedure" above. This is not recoverable via retry.
5. **Verify restored:** Navigate result should show user's actual logged-in state, no `stealth_warning`
6. **After successful restart:** Hermes may have spawned a new MCP server process with a new PID. Use `netstat -ano | findstr 7225` to verify the new PID is the one owning the port

### Infinite Scroll Collection Pattern (e.g., 巨量百应 爆款视频)

Pages with **infinite scroll** (no visible "Next" button, data loads as you scroll) need a different approach:

```python
# 1. Navigate to page with filters already applied
browser_navigate("https://buyin.jinritemai.com/dashboard/inspiration-center/hot-video?universal_page_params_id=...")

# 2. Collect initial batch
browser_text(maxLength=50000)
# Parse and save batch

# 3. Scroll loop with end-detection
for scroll_round in range(20):  # max 20 rounds ≈ 100+ items
    browser_scroll(amount=600, direction="down")
    time.sleep(2)
    
    # Check if new content loaded
    current_text = browser_text(maxLength=50000)
    if current_text == previous_text:
        break  # No new content loaded
    
    parse_and_append(current_text, all_videos)
    previous_text = current_text

# 4. Write to Feishu Bitable (see Feishu integration below)
```

**For 巨量百应 specifically:**
```python
# Scroll pattern: 每次滚动800px，等待2.5秒，让新视频加载
# End detection: browser_text() 返回内容与上次相同 → 已到最新
# Each scroll round loads ~5-10 new videos
# Target 50 records ≈ 5-10 scroll rounds

for round in range(15):
    browser_scroll(amount=800, direction="down")
    time.sleep(2.5)
    
    text = browser_text(maxLength=50000)
    new_videos = parse_video_blocks(text)  # split by '总播放量'
    all_videos.extend(new_videos)
    
    if len(all_videos) >= 50:
        break
    if text == last_text:
        break
    last_text = text
```

**⚠️ If real-browser-mcp is down (ClosedResourceError):**
- `mcp_real_browser_browser_scroll` fails
- Fall back to Hermes built-in `browser_scroll(direction="down")` — works but opens fresh logged-out session
- **Better: ask user to scroll manually in their Edge, then signal "ready" → screenshot → vision_analyze for collection**
---

## Related Skills

- `feishu-cli` — For writing collected data to Feishu/Bitable tables after extraction