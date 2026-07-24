---
name: scrapling-scraper
description: >-
  当用户需要使用 Scrapling 进行隐身网页采集（StealthyFetcher）时使用。
  支持：隐身模式采集（绕过反爬）、自动滚动加载、CSS 解析、翻页采集。
  不要用于：需要登录的平台（走 real-browser-mcp）、API调用（走 Apify）。
  触发词：Scrapling、隐身采集、反爬采集、StealthyFetcher、自动翻页采集
triggers:
  - Scrapling
  - 隐身采集
  - 反爬采集
  - StealthyFetcher
  - 自动翻页
  - 网页采集工具
tags: [scraping, web, stealth, anti-bot, python]
version: 1
---

# Scrapling 隐身网页采集工具

## 概述

Scrapling 是一个 Python 库，通过启动隐身 Chromium 浏览器（带真实指纹伪装）来绕过反爬检测。比 Hermes 内置的 Headless 浏览器更隐蔽，比 real-browser-mcp 更轻量（无需扩展）。

**安装位置**：`D:/hermes-data/.venv/`（通过 `uv pip install scrapling` 安装）

## 核心能力

| 能力 | 说明 |
|------|------|
| 隐身模式 | 模拟真实 Chrome 149 浏览器，Referer 伪装成 Google 搜索流量 |
| 自动滚动 | 通过 `page_action` 参数，传入自定义函数实现 |
| CSS 解析 | 内置 `.css()` 选择器，可直接提取元素 |
| 页面交互 | 支持截图、等待元素、执行 JS |
| 反爬绕过 | 通过 `patchright` 驱动的真实 Chromium 浏览器，通过大部分反爬检测 |

## 安装

```bash
uv pip install scrapling
uv pip install patchright    # 隐身浏览器引擎
uv run playwright install chromium  # 浏览器内核
```

## 基础用法

### 1. 简单抓取

```python
from scrapling import StealthyFetcher

resp = StealthyFetcher.fetch("https://example.com", headless=True)
# headless=True 无头模式，False 可见浏览器窗口

print(f"状态码: {resp.status}")
print(f"HTML内容: {resp.html_content[:1000]}")
print(f"纯文本: {resp.body[:1000]}")
print(f"JSON: {resp.json()}")  # 如果是JSON接口
```

### 2. CSS 解析提取数据

```python
resp = StealthyFetcher.fetch("https://www.baidu.com/s?wd=手机", headless=True)

# CSS 选择器提取
results = resp.css('.result')  # 找到所有 class="result" 的元素
titles = resp.css('h3')       # 找到所有 h3 标题

for result in results:
    text = result.text          # 纯文本
    link = result.css('a')      # 找到子元素 a
    href = link[0].attrib.get('href') if link else None
```

### 3. 自动滚动（模拟翻页/懒加载）

```python
def auto_scroll(page):
    """自动滚动 3 次，每次间隔 1 秒"""
    import time
    for i in range(3):
        # 滚动到页面高度的 1/3, 2/3, 3/3
        page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {i+1}/3)")
        time.sleep(1)

resp = StealthyFetcher.fetch(
    "https://www.baidu.com/s?wd=AI",
    headless=True,
    timeout=30000,
    page_action=auto_scroll
)
# 对比滚动前的内容长度，确认新内容加载
print(f"滚动后内容长度: {len(resp.html_content)}")
```

### 4. 等待元素加载

```python
resp = StealthyFetcher.fetch(
    "https://example.com",
    headless=True,
    wait_selector="div.content",  # 等待 CSS 选择器出现
    wait_selector_state="visible"
)
```

### 5. 配置 Cookie/UserAgent

```python
resp = StealthyFetcher.fetch(
    "https://example.com",
    headless=True,
    useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    cookies={"session_id": "abc123"},
    locale="zh-CN"
)
```

## 完整翻页采集流程

```python
from scrapling import StealthyFetcher

all_data = []

for page_num in range(1, 6):  # 采集 5 页
    # 构建翻页 URL
    url = f"https://search.jd.com/Search?keyword=手机&page={page_num}"
    
    resp = StealthyFetcher.fetch(url, headless=True, timeout=30000)
    
    # 提取本页数据
    items = resp.css('.gl-item')  # JD 商品卡片
    for item in items:
        title = item.css('.p-name em')[0].text if item.css('.p-name em') else ''
        price = item.css('.p-price i')[0].text if item.css('.p-price i') else ''
        all_data.append({'title': title, 'price': price})

print(f"共采集 {len(all_data)} 条商品")
```

## Response 对象属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `status` | int | HTTP 状态码 |
| `html_content` | str | 完整 HTML（含滚动后加载的内容） |
| `body` | bytes | 原始响应体（可用于 decode） |
| `text` | str | CSS 解析后的文本 |
| `json()` | dict | 如果是 JSON 接口 |
| `css(selector)` | list | CSS 选择器提取元素 |
| `url` | str | 最终 URL |
| `headers` | dict | 响应头 |
| `cookies` | dict | Cookie |
| `.attrib` | dict | 元素属性 |
| `find_by_text(text)` | list | 按文本查找元素 |
| `xpath(path)` | list | XPath 查询 |

## 已知限制

1. **JD.com 等强反爬站**：会被重定向到登录页（需要 cookie 或 real-browser-mcp）
2. **首次启动慢**：需要启动 Chromium 浏览器（约 3-5 秒）
3. **内存消耗**：每个 `fetch()` 启动一个浏览器实例（约 150MB）
4. **不支持多页面并发**：同一时间只能处理一个页面
5. **不支持登录态保持**：每次 `fetch()` 都是新会话（除非用 `page_setup` 注入 cookie）

## 与 Hermes 内置浏览器的对比

| 对比项 | Hermes 内置浏览器 | Scrapling StealthyFetcher |
|--------|-------------------|--------------------------|
| 浏览器类型 | 云端无头 Browserbase | 本地 Chromium |
| 隐身程度 | 低（有 Stealth 警告） | 高（真实 Chrome 指纹） |
| 反爬绕过 | 弱 | 强（通过大部分检测） |
| 自动滚动 | 独立 scroll 工具 | 内嵌 page_action 函数 |
| CSS 解析 | 需用 vision/截图 | 内置 `.css()` 选择器 |
| 翻页 | 手动 click 下一页 | 编程式 URL 构建 |
| 依赖 | 无需安装 | 需安装 + 下载 Chromium |
| 速度 | 快（云端） | 慢（本地启动浏览器） |

## Pitfalls

1. 0.4.11 版本 API 有变化：`stealth` 参数已废弃，用 `StealthyFetcher.fetch()` 类方法
2. 第一个请求较慢（约 5-8 秒），后续约 2-3 秒
3. 临时目录残留：每次 `fetch()` 在 `~/.cache/scrapling/` 留下缓存文件
4. 不要在 `page_action` 中做耗时操作（超过 30 秒 timeout 会超时）
5. 出现 `ModuleNotFoundError: No module named 'patchright'` → 需要手动安装（不是默认依赖）