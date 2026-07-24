"""Playwright-based QR code login for xhs-cli (camoufox fallback).

When `xhs login --qrcode` fails because camoufox Firefox binary (~492MB)
can't be downloaded, use Playwright Chromium (~182MB, downloads reliably)
as a replacement to show the QR code and capture the a1 cookie after scan.

Usage:
    python qr_login.py

Prerequisites:
    pip install playwright
    python -m playwright install chromium

Flow:
    1. Opens headless=False Chromium browser at xiaohongshu/login
    2. Takes a screenshot of the QR code → ~/Desktop/xhs_qr.png
    3. Polls cookies every 3s for up to 3 minutes
    4. After user scans QR and completes login, extracts a1 cookie
    5. Imports cookie to xhs CLI via `xhs login --cookie "a1=..."`

Detection logic (real login vs guest):
    - Guest: xhs whoami shows guest: true, name: Unknown
    - Real: xhs whoami shows real nickname (e.g. 麦兜), guest field absent/false
"""

import asyncio, json, os, subprocess, time

async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await ctx.new_page()

        await page.goto("https://www.xiaohongshu.com/login", wait_until="domcontentloaded")
        await asyncio.sleep(3)

        ss_path = os.path.expanduser("~/Desktop/xhs_qr.png")
        await page.screenshot(path=ss_path)
        print(f"QR code saved to {ss_path}")
        print("请用小红书 App 扫描桌面上的二维码，扫码后等待跳转...")

        # Poll for real login: URL changes to /explore OR cookies grow with session
        for i in range(60):
            await asyncio.sleep(3)

            # Check URL change
            url = page.url
            if "/login" not in url and "/explore" in url:
                print(f"URL changed to: {url}")

            # Check cookies
            cookies = await ctx.cookies()
            names = [c["name"] for c in cookies]
            has_session = any(s in names for s in ["session", "sid", "token"])
            has_web_session = "web_session" in names

            if ("/login" not in url) or (has_session and len(cookies) > 15):
                print(f"Login detected! Cookies={len(cookies)}")
                await asyncio.sleep(2)
                cookies = await ctx.cookies()

                cookie_file = os.path.expanduser("~/.xhs_cookies.json")
                with open(cookie_file, "w") as f:
                    json.dump(cookies, f)

                xhs = r"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.2\win-x64\python\Scripts\xhs.exe"
                from xhs_cli.cookies import save_cookies
                cookie_dict = {}
                for c in cookies:
                    if c["name"] in ("a1", "web_session", "webId", "sid", "session", "token"):
                        cookie_dict[c["name"]] = c["value"]
                save_cookies(cookie_dict)

                # Verify real login (not guest)
                r = subprocess.run([xhs, "whoami"], capture_output=True, text=True, timeout=10)
                if "guest: true" in r.stdout or "Unknown" in r.stdout:
                    print("WARNING: Logged in as guest only. User needs to actually scan and complete login.")
                else:
                    print("Real login confirmed!")
                print(r.stdout[:300])
                await browser.close()
                return

            if i % 5 == 0:
                print(f"Waiting... URL: {url[:60]} ({i*3}s)")

        print("Timed out (3 min) — no login detected")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
