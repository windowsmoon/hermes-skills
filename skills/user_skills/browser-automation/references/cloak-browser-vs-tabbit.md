# CloakBrowser vs Tabbit Browser: Anti-Detection Comparison

**Researched**: 2026-07-22 | **Source**: CloakBrowser GitHub (19.6k⭐), juejin.cn analysis, cloakhq official site

## Core Difference: Architecture

| Dimension | CloakBrowser | Tabbit Browser |
|-----------|-------------|---------------|
| Approach | **C++ source-level patches** (71 patches compiled into Chromium binary) | **JS runtime injection** (Playwright-based anti-detect script injection) |
| How it works | Pre-built custom Chromium binary with modified source code | MCP server + Playwright that injects anti-detection JS at page load |
| Detectability | Transparent - fingerprints match real Chrome exactly | Observable - JS patch descriptors differ from native Chrome |
| Installation | `pip install cloakbrowser` (~200MB binary auto-download) | Hermes MCP server + Tabbit Browser app |

## Head-to-Head: Anti-Detection Capabilities

| Detection Vector | CloakBrowser | Tabbit Browser |
|-----------------|-------------|---------------|
| `navigator.webdriver` | ✅ C++ attribute descriptor modification (undetectable) | ⚠️ JS injection (descriptor mismatch) |
| Canvas 2D fingerprint | ✅ Skia renderer noise injection (source-level) | ❌ Cannot modify |
| WebGL renderer/vendor | ✅ C++ compiled patch | ❌ Cannot modify |
| AudioContext fingerprint | ✅ Source-level noise injection | ❌ Cannot modify |
| Font enumeration | ✅ Returns real desktop font list (C++) | ❌ Returns server font list |
| Screen resolution/color depth | ✅ Reports real system values | ⚠️ JS override (detectable) |
| Hardware concurrency | ✅ Reports real CPU count | ⚠️ JS override |
| Device memory | ✅ Returns true RAM value (C++) | ⚠️ JS override |
| `window.chrome` object | ✅ Present with real sub-objects | ⚠️ JS stub (detectable) |
| `navigator.plugins` | ✅ Returns 5+ real plugins | ⚠️ JS override |
| TLS fingerprint (JA3/JA4) | ✅ Identical to real Chrome | ❌ Cannot modify |
| CDP automation signal | ✅ `isAutomatedWithCDP: false` (source-level) | ⚠️ Uses CDP inherently |
| User-Agent | ✅ Real Chrome UA (no "Headless" leak) | ⚠️ May leak "Headless" marker |

## Detection Test Results (Official)

| Test | Stock Playwright | CloakBrowser |
|------|----------------|-------------|
| reCAPTCHA v3 | 0.1 (bot) | **0.9 (human)** |
| Cloudflare Turnstile (non-interactive) | FAIL | **PASS** |
| Cloudflare Turnstile (managed) | FAIL | **PASS** (single click) |
| ShieldSquare | BLOCKED | **PASS** |
| FingerprintJS | DETECTED | **PASS** |
| BrowserScan | DETECTED | **NORMAL (4/4)** |
| bot.incolumitas.com | 13 fails | **PASS** |
| deviceandbrowserinfo.com | 6 true flags | **0 true flags** |

## 🚨 CloakBrowser Has NO MCP/Plugin/API (Python Library Only)

**Confirmed on this system (2026-07-22):** After searching GitHub, npm, PyPI, and cloakhq official site — CloakBrowser is a Python/JS library. It has no MCP server, no Hermes plugin, no REST API.

| Integration | Status |
|-------------|--------|
| Python library (`pip install cloakbrowser`) | ✅ Yes |
| JS library (`npm install cloakbrowser`) | ✅ Yes |
| NuGet (.NET) package | ✅ Yes |
| Docker image (`cloakhq/cloakbrowser`) | ✅ Yes |
| **CLI manager** (`cloakbrowser install/info/doctor/update/clear-cache`) | ✅ Yes — binary management only |
| **MCP Server** | ❌ Does not exist |
| **Hermes Plugin** | ❌ Does not exist |
| **Hermes Skill** | ❌ Can be created (wraps Python calls via execute_code) |
| **REST API** | ❌ No HTTP endpoints |

The CLI (`cloakbrowser.exe`) is only for managing the embedded Chromium binary:
```bash
cloakbrowser install        # Download Chromium binary
cloakbrowser doctor         # Check installation status
cloakbrowser info           # Show env + binary diagnostics
cloakbrowser update         # Check for newer binary
cloakbrowser clear-cache    # Remove cached binaries
```

It CANNOT be added to Hermes as an MCP server:
```bash
hermes mcp add cloakbrowser --command cloakbrowser --args doctor
# This would NOT work as an MCP server — cloakbrowser CLI is not MCP-compatible
```

## Free Tier (v146) vs Pro Tier (v150)

**Tested on this system (2026-07-22):** Free tier (Chromium v146, limited patches).

| Test | Free Tier (v146) | Pro Tier (v150) |
|------|-----------------|-----------------|
| bot.incolumitas.com | ❌ FAIL | ✅ PASS (official claim) |
| Binary download size | ~200MB | Latest binary |
| Number of patches | Limited | **71 patches** |
| Headless mode | ❌ Detected | ✅ Works |
| Headed mode | ⚠️ Partial | ✅ Full evasion |

**Lesson**: Free tier is good for basic anti-detection but NOT sufficient for strong bot-detection sites like Cloudflare Turnstile or 巨量百应. Pro subscription ($) required for production use.

## Which Tool for Which Scenario?

| Scenario | Recommended Tool | Reason |
|----------|----------------|--------|
| Generic web scraping (no login) | Hermes built-in browser | Fastest, no extra setup |
| Public e-commerce (no login) | Hermes built-in + Tabbit | Acceptable anti-detection |
| **Login-required platform (巨量百应/抖音/淘宝)** | **CloakBrowser** (but needs re-login) | Anti-detection is better but cannot reuse existing session |
| **Login-required + existing session** | Real Browser MCP (extension route) | Only tool that reuses existing browser session |
| Strong anti-bot e-commerce | CloakBrowser + proxy | Source-level evasion beats JS injection |

## Key Limitation

**Neither CloakBrowser, Tabbit, nor any browser-based tool can use the user's existing Edge/Chrome login session.** All launch a NEW browser instance. For login-protected platforms, you must either:
1. Use **Real Browser MCP** (browser extension → connects to existing browser with all sessions)
2. Log in again in the new browser instance
3. Ask the user to export data from their logged-in browser

## CloakBrowser Quick Install

```python
pip install cloakbrowser

from cloakbrowser import launch
browser = launch(humanize=True)  # Auto-downloads ~200MB binary on first run
page = browser.new_page()
page.goto("https://target-site.com")
```

- Free tier: Chromium v146 (limited patches)
- Pro tier: Chromium v150 (71 patches, latest anti-bot fixes, paid)

**Note**: The `headless=True` mode on free tier still gets detected at some sites. Use `headless=False` (headed mode) for best results.

## Using CloakBrowser from Hermes (The Only Way)

Since CloakBrowser has no MCP/server, you MUST use it via Python in execute_code:

```python
from cloakbrowser import launch
browser = launch(headless=True)  # or headless=False for visible window
page = browser.new_page()
page.goto("https://target-site.com")
# ... standard Playwright API ...
browser.close()
```

**⚠️ execute_code CANNOT show headed browser windows** — the sandbox suppresses GUI. See "Headed Browser from execute_code" section in the main SKILL.md.

## Practical Login Workflow (Verified 2026-07-22)

For login-protected platforms like 巨量百应, the recommended workflow is:

1. **Create a desktop batch file** that the user double-clicks to launch CloakBrowser (headed mode)
2. The batch file runs outside the Hermes sandbox, so the browser window appears visibly
3. User logs in (SMS/QR code) in the visible browser
4. Session cookies are saved to `~/AppData/Local/hermes/cloakbrowser_sessions/`
5. Subsequent data collection can use the saved session

```python
# Save session after login
from cloakbrowser import launch
browser = launch(headless=False, humanize=True)
page = browser.new_page()
page.goto("https://target-site.com")
# ... user logs in manually ...
input()  # Wait for user to press Enter after login

# Save cookies and storage
cookies = browser.context.cookies()
storage = browser.context.storage_state()
with open("session_cookies.json", "w") as f:
    json.dump(cookies, f)
with open("session_storage.json", "w") as f:
    json.dump(storage, f)
```

**Key lesson from this system (2026-07-22):** Launching a headed browser from inside `execute_code` (Hermes sandbox) does NOT show the window. Always use a batch file on the Desktop that the user double-clicks.
