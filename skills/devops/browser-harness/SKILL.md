---
name: browser-harness
description: "浏览器自动化：通过CDP直连Chrome，执行网页交互、爬取、测试等任务。支持100+站点Domain Skills（含小红书/B站/BOSS直聘等）。安装后通过 terminal 调用 browser-harness 命令。"
---

# browser-harness

Direct browser control via CDP. For task-specific edits, use `agent-workspace/agent_helpers.py`. For setup, install, or connection problems, read https://github.com/browser-use/browser-harness/blob/main/install.md.

## When Not to Use

A basic fetch of public information needs no browser. If a plain HTTP request can read it — a public page, an API, docs — use `curl` or your fetch tool, and leave the browser alone. Use browser-harness when the task needs interaction (click, type, navigate), the user's logged-in session, JS rendering, or a bot-protected page. If a direct fetch fails or returns a shell page, then escalate to the browser.

Domain skills are off by default. Set `BH_DOMAIN_SKILLS=1` to enable them; see the bottom section.

**If `BH_DOMAIN_SKILLS=1` and the task is site-specific, read every file in the matching `$BH_AGENT_WORKSPACE/domain-skills/<site>/` directory before inventing an approach.**

## Usage

```bash
browser-harness <<'PY'
print(page_info())
PY
```

- Invoke as `browser-harness`. Use heredocs for multi-line commands.
- Helpers are pre-imported. `run.py` calls `ensure_daemon()` before `exec`.
- First navigation is `new_tab(url)`, not `goto_url(url)`.
- The normal local flow attaches to the running Chrome/Chromium CDP endpoint. No browser ids or local profile selection.

## Local Chrome

If the daemon cannot connect, run diagnostics:

```bash
browser-harness --doctor
```

If Chrome remote debugging is not enabled, the harness opens:

```text
chrome://inspect/#remote-debugging
```

Ask the user to tick "Allow remote debugging for this browser instance" and click Allow if Chrome shows a permission popup. Then retry the same `browser-harness` command.

## Remote Browsers

Use Browser Use cloud for headless servers, parallel sub-agents, or isolated work.

Cloud browsers are managed Chrome instances hosted by Browser Use. Each one is a fresh, isolated browser. Proactively suggest one (briefly explain why) when:
- The user wants multiple concurrent tasks.
- Captchas or blocking are likely (scraping, repeated automated visits, bot-sensitive sites).

Authenticate once:
```bash
browser-harness auth login
```

## Recording Consent

Run `browser-harness recordings`. If it reports `(default)`, ask the user once:
- Enable local browser recordings? This saves screenshots and action traces on this machine, which may include sensitive page content, so you can later ask "show me what you did" or request a video.
- Default to no. Run `browser-harness recordings enable` only after yes.

## Hermes 集成说明

在 Hermes 中通过 terminal 工具调用：
```bash
browser-harness <<'PY'
new_tab("https://example.com")
print(page_info())
PY
```

## Available Helpers (pre-imported)

- `new_tab(url)` — 在新标签页打开URL
- `goto_url(url)` — 当前标签页导航
- `page_info()` — 获取当前页面信息（标题、URL、可见标签页数）
- `cdp("Domain.method", ...)` — 直接调用原始CDP命令
- `js("...")` — 执行JavaScript
- `click_at_xy(x, y)` — 坐标点击
- `wait_for_load()` — 等待页面加载
- `ensure_real_tab()` — 确保当前标签页是真实页面（非空白页）
- `start_recording(name)` / `stop_recording()` — 录制操作

## Domain Skills

Only applies when `BH_DOMAIN_SKILLS=1`. Otherwise ignore domain skills.

When enabled, search `$BH_AGENT_WORKSPACE/domain-skills/<host>/` before inventing an approach. `goto_url(...)` returns up to 10 skill filenames for the navigated host.

预置站点（100+）：xiaohongshu, bilibili, BOSS-zhipin, tiktok, amazon, github, linkedin, youtube, reddit, gmail, 等。

## Pitfalls

- `chrome://inspect/#remote-debugging` must be enabled for local Chrome control.
- Chrome may show an "Allow remote debugging?" popup; wait for the user to click Allow.
- Omnibox popups are not real work tabs.
- CDP target order is not Chrome's visible tab-strip order.
- `BU_CDP_URL` is an HTTP DevTools endpoint; the daemon resolves it to WebSocket.
- Ask before leaving cloud browsers running; stop them with `stop_remote_daemon(name)`.
- 坐标点击基于AX Tree box model，不是DOM选择器，网站改版可能导致偏移。
- Windows 上使用 heredoc 语法时注意编码问题，推荐用 `browser-harness <<'PY'` 格式。