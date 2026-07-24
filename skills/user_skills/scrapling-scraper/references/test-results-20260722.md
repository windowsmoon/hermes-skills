# Scrapling 测试记录（2026-07-22）

## 环境
- Python 3.12.12（uv venv at D:/hermes-data/.venv）
- Scrapling 0.4.11
- patchright 1.61.2（Playwright 1.61.0）
- Chromium Headless Shell 149.0.7827.55

## 安装依赖
```bash
uv pip install scrapling
uv pip install curl_cffi httpx browserforge patchright fake-useragent msgspec
uv run playwright install chromium
```

## 测试结果

| 测试项 | URL | 结果 |
|--------|-----|------|
| 隐身模式伪装 | httpbin.org/headers | ✅ Chrome 149，UA、Sec-* 头、Referer 伪装成 Google 搜索 |
| 百度搜索 | baidu.com/s?wd=AI | ✅ 成功获取 1.4MB 页面，CSS 解析出 5 个搜索结果 |
| 自动滚动 | baidu.com/s?wd=AI | ✅ page_action 滚动 3 次，内容从 1.41MB 增长到 1.48MB |
| CSS 解析 | baidu.com/s?wd=AI | ✅ `.result` 找到 5 个元素，`h3` 找到 13 个 |
| JD.com 搜索 | search.jd.com | ⚠️ 被重定向到登录页 |
| 翻页采集 | 未测试 | 通过构建 URL page 参数实现 |

## 关键发现

1. **Response 对象属性**：使用 `.html_content` 获取完整 HTML，`.body` 获取原始 bytes，`.text` 获取解析文本
2. **StealthyFetcher.fetch() 是类方法**，不是实例方法
3. **page_action 参数**接收一个函数，函数接收 page 对象，可以执行 evaluate/click/wait 等操作
4. **JD.com 重定向到 passport.jd.com/login** → 说明 Scrapling 无法绕过京东的反爬
5. **百度搜索成功** → 说明百度级别的反爬可以绕过