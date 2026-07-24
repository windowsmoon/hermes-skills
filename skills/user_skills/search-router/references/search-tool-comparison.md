# 搜索工具对比（2026-07 调研）

## 已安装的搜索工具

| 工具 | 类型 | 覆盖源 | 费用 | 适合场景 |
|------|------|--------|------|---------|
| **open-webSearch** | MCP + CLI | 百度/Bing/搜狗/CSDN/掘金/DuckDuckGo/Brave/Startpage | ✅ 免费 | 日常通用搜索，中文首选百度 |
| **Tavily** | API | 通用网络搜索 | ⚠️ 有免费额度 | 英文通用搜索 |
| **Exa** | API | 语义搜索 | ⚠️ 有免费额度 | 语义搜索/深度内容发现 |
| **秘塔** | API | 中文搜索 | ⚠️ 剩3次 | 中文搜索备选，快用完 |
| **Firecrawl** | API | 网页抓取 | ⚠️ 有免费额度 | 批量网页内容抓取 |
| **TrendRadar** | Skill | 微博/知乎/抖音/百度/B站/头条/澎湃/贴吧 | ✅ 免费 | 热点监控，8平台聚合 |
| **SenseNova 搜索套件** | Skill (10个) | 学术/代码/金融/社交(中+英)/图片/市场/年报 | ⚠️ 需 SenseNova API | 专业领域搜索 |
| **xhs-cli** | CLI | 小红书站内 | ✅ 已有登录态 | 小红书搜索 |
| **bailian-cli** | CLI | 阿里云 DashScope 搜索 | ✅ 免费额度 | 阿里系搜索 |
| **unified-search** | Skill | Tavily+Exa+秘塔+Firecrawl+open-webSearch | ⚠️ 混合 | 深度研究/竞品分析 |

## 未安装的备选

| 工具 | 特点 | 为什么不装 |
|------|------|-----------|
| **SearXNG** | 自建元搜索引擎，248个引擎，Docker部署 | 需先装Docker Desktop+WSL2，暂未部署 |
| **AnySearch** | 云端聚合搜索API，15个垂直领域 | 未注册API Key，垂直搜索增量大但非必需 |

## 搜索路由规则

| 搜索内容 | 首选工具 |
|---------|---------|
| 通用信息/数据/知识 | open-webSearch --engine baidu（中文）或 --engine bing（英文） |
| 热点/新闻/实时 | TrendRadar（8平台） |
| 深度研究/竞品分析 | unified-search（Tavily+Exa+秘塔+Firecrawl） |
| 学术/论文/百科 | sensenova-sn-search-academic |
| 代码/开源/API | sensenova-sn-search-code |
| 中文UGC（B站/知乎/抖音） | sensenova-sn-search-social-cn |
| 小红书 | xhs-cli |
| 海外社媒（Reddit/Twitter/YouTube） | sensenova-sn-search-social-en |
| 图片 | sensenova-sn-search-image |
| 商业/财经/行业 | sensenova-sn-search-finance + sensenova-sn-search-market-cn + sensenova-sn-search-year-report |
| 爬虫/反爬场景 | Tabbit浏览器 + Firecrawl |