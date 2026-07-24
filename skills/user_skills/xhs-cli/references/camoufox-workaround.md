# Camoufox Firefox Download Workaround — Playwright Chromium QR Login

## Problem

`xhs login --qrcode` depends on camoufox Firefox (~492MB from GitHub releases) which often fails to download on unstable connections:

```
camoufox.exceptions.CamoufoxNotInstalled: official/stable is not installed.
Please run `camoufox fetch` to install.
```

The download (`python -m camoufox fetch`) keeps failing with `IncompleteRead` after downloading 100–200MB of the 492MB file.

## Solution: Playwright Chromium QR Login

Playwright Chromium (~182MB) downloads reliably from `cdn.playwright.dev`. Once installed, run a custom script that opens the login page on the user's desktop, waits for QR scan, and extracts cookies on real login.

### Prerequisites

```bash
# In Hermes bundled Python
uv pip install --python <bundled-python-path> playwright
python -m playwright install chromium
```

Or via standalone Hermes bundled Python:
```bash
"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.2\win-x64\python\python.exe" -m playwright install chromium
```

### Runnable Script

Save as `xhs_qr_login.py` and run. The script opens a Chromium window on the user's desktop.

```python
import asyncio, json, os, subprocess
from playwright.async_api import async_playwright

async def main():
    print("[LOGIN] Starting xiaohongshu QR code login...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        page = await ctx.new_page()
        await page.goto("https://www.xiaohongshu.com/login",
                        wait_until="domcontentloaded")
        await asyncio.sleep(3)

        ss_path = os.path.expanduser("~/Desktop/xhs_qr.png")
        await page.screenshot(path=ss_path)
        print(f"[LOGIN] QR code saved to {ss_path}")
        print("请用小红书 App 扫描二维码，等待浏览器跳转...")

        # Poll: check URL change + cookie indicators every 3s, max 3 min
        for i in range(60):
            await asyncio.sleep(3)
            current_url = page.url
            cookies = await ctx.cookies()
            names = [c["name"] for c in cookies]
            has_session = any(s in names for s in ["session", "sid", "token", "id_token"])
            url_changed = "/login" not in current_url and "/explore" in current_url

            if url_changed or (has_session and len(cookies) > 15):
                print(f"[LOGIN] Detected! URL: {current_url}, cookies: {len(cookies)}")
                await asyncio.sleep(2)  # let cookies settle

                cookies = await ctx.cookies()
                # Save full cookie dump
                with open(os.path.expanduser("~/.xhs_cookies.json"), "w") as f:
                    json.dump(cookies, f, indent=2)

                # Import to xhs CLI via its internal API
                from xhs_cli.cookies import save_cookies
                d = {}
                for c in cookies:
                    if c["name"] in ("a1", "web_session", "webId", "sid", "session", "token", "id_token"):
                        d[c["name"]] = c["value"]
                save_cookies(d)

                # Verify
                xhs = r"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.2\win-x64\python\Scripts\xhs.exe"
                r = subprocess.run([xhs, "status"], capture_output=True, text=True, timeout=10)
                w = subprocess.run([xhs, "whoami"], capture_output=True, text=True, timeout=10)
                print(f"[LOGIN] status: {r.stdout[:150]}")
                print(f"[LOGIN] whoami: {w.stdout[:150]}")
                print("[LOGIN] ✅ 登录成功！")
                await browser.close()
                return

            if i % 5 == 0:
                print(f"[LOGIN] waiting... ({i*3}s) URL: {current_url[:60]}")

        print("[LOGIN] Timed out after 3 min")
        await browser.close()

asyncio.run(main())
```

### How It Works

1. Opens a Chromium browser window on the user's desktop
2. Navigates to `https://www.xiaohongshu.com/login`
3. Saves a screenshot to `~/Desktop/xhs_qr.png`
4. Polls every 3 seconds for the URL to change from `/login` to `/explore` OR for session cookies to appear
5. After login, imports the `a1` + session cookies into xhs CLI via `xhs_cli.cookies.save_cookies()`
6. Verifies with `xhs status` and `xhs whoami`

### Key Differences from `xhs login --qrcode`

| Aspect | `xhs login --qrcode` | Playwright script |
|--------|---------------------|-------------------|
| Browser engine | camoufox Firefox (492MB) | Chromium (182MB) |
| Download reliability | Unstable (GitHub) | Reliable (Playwright CDN) |
| Cookie detection | Automatic | Polling + URL check |
| Cookie import | Automatic | Via `xhs_cli.cookies.save_cookies()` |
| User visibility | Browser window | Browser window |

### Troubleshooting

- **Screenshot not created**: Check if playwright chromium is installed (`python -m playwright install chromium`). The script exits within seconds if Chromium is missing.
- **Not detecting login**: The script checks for URL change to `/explore` OR session cookies (`session`, `sid`, `token`, `id_token`). If the login page redirects differently, adjust the detection criteria.
- **`guest: true` in xhs status**: The a1 cookie from the login page before QR scan is a guest/anonymous session. The user must scan the QR code and let the page redirect before the script captures cookies.
- **Script exits too fast**: Ensure `headless=False` so the browser window stays visible. The background terminal process may not show output properly; run via `execute_code` with sufficient timeout.
