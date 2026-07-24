# 搜索工具注册表

本文件记录当前可用的搜索源及其 API 配置状态。
用于 unified-search skill 初始化时检查可用搜索源。

## 可用搜索源

| 源 | 接入方式 | API Key | 免费额度 | 状态 |
|----|---------|---------|---------|:----:|
| Tavily | REST API | ✅ 已配置 | 1000次/月 | ✅ 可用 |
| Exa | REST API | ✅ 已配置 | 有免费额度 | ⚠️ content字段常空，需URL补全 |
| Firecrawl | REST API (v0) | ✅ 已配置 | 有免费额度 | ⚠️ v0 API，title/url需从content解析 |
| 秘塔 | REST API | ✅ 已配置 | 按credits计费 | ✅ 可用 |
| web_search (Hermes) | 内置工具 | 无需 Key | 无限 | ✅ 可用 |
| web_extract (Hermes) | 内置工具 | 无需 Key | 无限 | ✅ 可用 |
| Obsidian RAG | query_obsidian.py | 无需 Key（本地FAISS） | 无限 | ✅ 可用 |
| session_search | Hermes FTS5 | 无需 Key | 无限 | ✅ 可用 |
| Hindsight | 内置 | 硅基流动（已配置） | 免费 | ✅ 可用 |

## 各 API 注册地址

- Tavily: https://tavily.com （GitHub/Google 登录）
- Exa: https://exa.ai
- Firecrawl: https://firecrawl.dev
- 秘塔: https://metaso.cn/search-api/

## 配置方式

API Key 写入 ~/.hermes/.env：

```bash
TAVILY_API_KEY=tvly-xxx
EXA_API_KEY=xxx
FIRECRAWL_API_KEY=fc-xxx
MITA_API_KEY=mk-xxx
```

## 统一搜索入口

优先使用 `scripts/unified_search.py`：

```bash
python scripts/unified_search.py "查询词" --sources all --max 10
```
