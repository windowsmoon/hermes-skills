---
name: universal-scraper
description: 通用网站信息爬取——先问用户要多少条，按决策树逐层执行。Firecrawl→Tabbit(滚动+翻页+反检测)→Scrapling(隐身采集)→CloakBrowser(源码反爬)→Playwright+Vision(验证码)→computer-control(兜底)
triggers:
  - 帮我爬
  - 采集这个网站
  - 爬取数据
  - scraper
  - 网页采集
  - 帮我采集
version: 8
tags:
  - universal-scraper
  - universal

---

# Universal Scraper — 采集决策树

## 完整层级全景

```
L1: Firecrawl           API直调，公开页面
L2a: Tabbit Browser     有登录态+反检测【默认首选】
L2b: Scrapling          隐身采集，轻量反爬
L2c: CloakBrowser       源码级反检测+humanize
L2d: Playwright MCP     +Vision 处理验证码/滑块
L3:  computer-control   物理操作，最终兜底
```

## 核心流程

### Phase 0: 问用户
```
→ 需要采集多少条数据？
→ 用户回答：N条 / 全部
```

### Phase 1: 判断路径
```
我自行判断是否需要登录：
├─ 不需要 → 走路径B（L1 Firecrawl → L2b Scrapling → ...）
└─ 需要   → 告诉用户"需要登录"
            用户登录后告诉我"好了"
            → 走路径A
```

### Phase 2: 采集
```
路径A（需登录）：
L2a Tabbit → 滚动→翻页→够了停
   ↓ 反爬
L2c CloakBrowser → 用户双击登录后继续
   ↓ 验证码
L2d Playwright+Vision
   ↓ 全崩
L3 computer-control

路径B（无需登录）：
L1 Firecrawl → 够了停 / 不够降级
L2b Scrapling → 隐身采集
L2c → L2d → L3（同上）
```

### Phase 3: 写飞书
```
采集完成后：
→ 问用户："写入哪个飞书多维表格？"
   ├─ 用户回复链接 → 读取表格 → 追加到最后一条记录后面
   └─ 超时未回复（5分钟） → 自动创建新的飞书多维表格 → 写入数据
```

## 各层详细

### L1: Firecrawl
公开页面，API 直调，无需浏览器。

### L2a: Tabbit Browser
```
tabbit_navigate(url)
tabbit_antidetect()
循环: tabbit_input(scroll down) → 提取 → 去重
if 累计 >= N: break
if 滚到底:
    if 有翻页: click → 继续
    else: 降级
```

### L2b: Scrapling
```python
resp = StealthyFetcher.fetch(url, headless=True, page_action=scroll_fn)
items = resp.css('.selector')
```

### L2c: CloakBrowser
```python
browser = launch(headless=True, humanize=True)
context = browser.new_context(storage_state=storage)
```

### L2d: Playwright MCP + Vision
截图 → vision_analyze 识别 → 点击/拖动

### L3: computer-control
键盘 + 鼠标 + OCR，物理操作。

## 反爬检测
```python
signals = ["重定向", "空白页", "验证码", "数据为0", "HTTP异常"]
```

## 输出
JSON lines → 飞书多维表格（追加/自建）
