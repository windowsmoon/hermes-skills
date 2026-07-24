# Scrapling + CloakBrowser CDP Integration

**Date**: 2026-07-22 | **Scrapling**: 0.4.11 | **CloakBrowser**: 0.4.13 (chromium-146.0.7680.177.5)

## Architecture

```
用户登录 → CloakBrowser (headful, CDP:9222) → Hermes connect_over_cdp → 自动采集 → 飞书多维表格
```

## Scrapling Installation

```bash
cd D:\hermes-data
uv venv .venv
uv pip install scrapling
uv pip install curl_cffi browserforge patchright msgspec playwright
uv run playwright install chromium
```

## Scrapling Test Results (2026-07-22)

| Test | Result | Detail |
|------|--------|--------|
| StealthyFetcher basic | ✅ | Chromium 149, proper UA, Sec-*, Referer=Google |
| httpbin.org/headers | ✅ | 200, full headers returned |
| Baidu search | ✅ | 1.4MB page, CSS parsing `.result`=5 items |
| Auto-scroll via page_action | ✅ | Content grew from 1.41MB to 1.48MB after 3 scrolls |
| JD.com search | ⚠️ | Redirected to login (expected, anti-bot) |
| CSS selector parsing | ✅ | `.css()` works, `.extract_first()` works |

## StealthyFetcher API

```python
from scrapling import StealthyFetcher

# Basic fetch
resp = StealthyFetcher.fetch("https://target-site.com", headless=True)

# With auto-scroll
def auto_scroll(page):
    for i in range(3):
        page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {i+1}/3)")
        import time; time.sleep(1)

resp = StealthyFetcher.fetch(
    "https://target-site.com",
    headless=True,
    page_action=auto_scroll
)

# CSS parsing
resp.css('.item-class')  # Returns list of matched elements
resp.css('h3')  # Returns heading elements
resp.css('.price').extract_first()  # First match text
```

## CloakBrowser CDP Connection

```python
from playwright.sync_api import sync_playwright

# Connect to running CloakBrowser (must be started with --remote-debugging-port=9222)
with sync_playwright() as pw:
    browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    
    # Get existing context/pages (user's login session is here)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    # Navigate and scrape
    page.goto("https://target-site.com/data")
    page.wait_for_load_state("networkidle")
    
    # Auto-scroll loop
    last_height = page.evaluate("document.body.scrollHeight")
    for _ in range(10):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # Extract data
    items = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('.item')).map(el => ({
            title: el.querySelector('.title')?.textContent?.trim(),
            url: el.querySelector('a')?.href
        }))
    }""")
    
    # Pagination loop
    while page.locator('.next-btn:not(.disabled)').count() > 0:
        page.locator('.next-btn').click()
        page.wait_for_load_state("networkidle")
        # extract more data...
```

## CloakBrowser Startup Script Template

Save as `C:\Users\Admin\Desktop\启动CloakBrowser.bat`:

```batch
@echo off
chcp 65001 >nul
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
print('请登录目标网站，然后按 Enter 保存 session...')
input()
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

## Known Issues

1. **Headed browser from execute_code won't show window** — Hermes sandbox suppresses GUI. Must use desktop batch file.
2. **JD.com redirects to login** — Even with stealth, JD detects automation. Real logged-in browser (via CDP) is required.
3. **Scrapling 0.4.11 API changed** — `stealth` parameter is deprecated. Use `configure()` or `StealthyFetcher.fetch()`.
4. **CloakBrowser free tier (v146) limited** — Doesn't pass all bot detection tests. Pro tier (v150, 71 patches, paid) required for full evasion.
5. **connect_over_cdp requires the browser to be running first** — Script must be run AFTER user starts CloakBrowser.