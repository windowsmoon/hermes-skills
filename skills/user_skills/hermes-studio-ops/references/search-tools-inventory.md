# 搜索工具清单 & API Key 配置

## 已配置的 Key（`~/.hermes/.env`）

| Key | 值 | 用途 |
|-----|-----|------|
| `TAVILY_API_KEY` | `tvly-dev-2Ht23B-...hbFaRl6YW` | 网络搜索（1000次/月） |
| `EXA_API_KEY` | `67cc607e-cf49-47da-bec8-087c05488bb5` | 语义搜索 |
| `FIRECRAWL_API_KEY` | `fc-b2fe461...` | 网页抓取 |
| `MITA_API_KEY` | (有额度) | 秘塔中文搜索 |

## 搜索工具索引

### API / CLI 类

| 工具 | 类型 | 配置位置 | 状态 |
|------|------|---------|------|
| **Tavily** | Web Search API | `~/.hermes/.env`（`TAVILY_API_KEY`） | ✅ 已配 |
| **Exa** | Semantic Search API | `~/.hermes/.env`（`EXA_API_KEY`） | ✅ 已配 |
| **Firecrawl** | Web Scraping API | `~/.hermes/.env`（`FIRECRAWL_API_KEY`） | ✅ 已配 |
| **秘塔/Mita** | 中文搜索 API | `~/.hermes/.env`（`MITA_API_KEY`） | ✅ 已配（剩3次） |
| **open-websearch MCP** | 聚合搜索 MCP | 内置，无需 Key | ✅ 已装 |
| **bailian-cli search** | 阿里云搜索 | DashScope API Key | ✅ 已装 |
| **xhs-cli** | 小红书搜索 | CLI | ✅ 已装 |
| **SenseNova 搜索套件** | 10个专业搜索 skill | 需 SenseNova API Key | ⚠️ 未配 Key |

### MCP 工具

| 工具 | 引擎 | 是否需 Key |
|------|------|-----------|
| `mcp__open_websearch__search` | Bing/百度/CSDN/搜狗等 | ❌ 免费 |
| `mcp__open_websearch__fetchWebContent` | 网页抓取 | ❌ 免费 |
| `mcp__open_websearch__fetchCsdnArticle` | CSDN | ❌ 免费 |
| `mcp__open_websearch__fetchGithubReadme` | GitHub | ❌ 免费 |
| `mcp__open_websearch__fetchJuejinArticle` | 掘金 | ❌ 免费 |

### Skills

| Skill | 用途 |
|------|------|
| **unified-search** | 统一搜索入口，同时调多个搜索源 |
| **sensenova-sn-search-academic** | 学术搜索 |
| **sensenova-sn-search-code** | 代码搜索 |
| **sensenova-sn-search-finance** | 金融搜索 |
| **sensenova-sn-search-image** | 图片搜索（Serper.dev） |
| **sensenova-sn-search-market-cn** | 中国市场搜索 |
| **sensenova-sn-search-social-cn** | 中文社交搜索 |
| **sensenova-sn-search-social-en** | 英文社交搜索 |
| **sensenova-sn-search-social-media** | 社交媒体搜索 |
| **sensenova-sn-search-year-report** | 年报搜索 |
| **xhs-cli** | 小红书搜索 |

## 配置文件检查顺序

当需要确认某个服务是否已配置 API Key 时，**不要只看 config.yaml 或 skills 目录**，按以下顺序检查：

1. `~/.hermes/.env` — 环境变量（Tavily/Exa/Mita 的 Key 存在这里）
2. `~/.hermes/config.yaml` — 系统配置（memory provider, toolset 等）
3. Web UI Config API — `GET /api/hermes/config`
4. `~/AppData/Local/hermes/config.yaml` — Hermes Agent 配置
5. `~/.hermes-web-ui/config.json` — Web UI 状态

**`.env` 是最容易被忽略的 API Key 存放位置。**
