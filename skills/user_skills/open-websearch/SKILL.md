---
name: open-websearch
description: >
  当用户需要免API Key的搜索引擎结果时使用。
  通过MCP Server调用Bing/百度/CSDN/搜狗/掘金/DuckDuckGo等多引擎。
  不要用于：需要深度分析的搜索（走unified-search）、学术搜索（走sn-search-academic）。
  触发词：联网搜索、搜索引擎、Bing搜索、百度搜索、open-webSearch
tags:
  - search
  - web
  - baidu
  - bing
  - mcp
triggers:
  - 联网搜索
  - 搜索引擎
  - Bing搜索
  - 百度搜索
  - open-webSearch

---

# open-webSearch

## 安装

```bash
npm install -g open-websearch
```

已安装，路径：`~AppData/Roaming/npm/node_modules/open-websearch/`

## 可用搜索引擎

| 引擎 | 命令 | 适合 |
|------|------|------|
| **百度** `baidu` | `search "关键词" --engine baidu` | ✅ **中文搜索首选** |
| **Bing** `bing` | `search "keyword" --engine bing` | 英文通用搜索 |
| **搜狗** `sogou` | `search "关键词" --engine sogou` | 中文备选 |
| **CSDN** `csdn` | `search "技术问题" --engine csdn` | 技术社区 |
| **掘金** `juejin` | `search "前端" --engine juejin` | 前端/技术 |
| **DuckDuckGo** `duckduckgo` | `search "keyword" --engine duckduckgo` | 隐私搜索 |
| **Brave** `brave` | `search "keyword" --engine brave` | 英文备选 |
| **Exa** `exa` | 需 API Key，但 `.env` 已有 | 语义搜索 |
| **Startpage** `startpage` | `search "keyword" --engine startpage` | 隐私搜索 |

## 用法（Hermes Bundled Node）

```bash
# 直接用 Heremes Bundled Node 运行 one-shot 搜索
"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.2\win-x64\node\node.exe" "C:\Users\Admin\AppData\Roaming\npm\node_modules\open-websearch\build\index.js" search "关键词" --engine baidu --limit 5 --json
```

### one-shot（推荐，不需要后台服务）

```bash
# 搜索百度中文（免 Key）
node build/index.js search "AI新闻" --limit 5 --engine baidu --json

# 多引擎并行
node build/index.js search "自然语言处理" --limit 3 --engine sogou --json

# 抓取网页内容
node build/index.js fetch-web "https://example.com" --readability --json

# 抓取 CSDN 文章
node build/index.js fetch-csdn "https://blog.csdn.net/xxx" --json
```

### 后台 daemon 模式（可选）

```bash
node build/index.js serve --port 3001
```

## MCP Server

已注册到 Hermes Studio（端口 3001），可通过 MCP 协议调用。
