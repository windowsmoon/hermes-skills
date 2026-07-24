# 搜索源完整矩阵

所有当前已知/可用的搜索工具及其覆盖的搜索引擎。

## 已部署/已配置的搜索工具

## 调研中/待部署的搜索工具

| 工具 | 部署方式 | 搜索引擎/源 | 费用 | 中文友好 |
|------|---------|------------|------|---------|
| **SearXNG** | Docker自部署 | **248个引擎**包括：Google / Bing / Baidu / Sogou / 360搜索 / ChinaSo / Bilibili / Wikipedia / ArXiv / PubMed / GitHub / Reddit / 图片/视频/音乐/学术/代码/购物 等全部类型 | 免费（需服务器） | ✅ 百度/搜狗/360/B站/CSDN |
| **AnySearch** | REST API（Key已配） | 通用Web + **22个垂直领域**：代码/技术/金融/学术/法律/安全/医疗/能源/娱乐等 | 免费1,000次/天 | ✅ 中文工商/合规/专利等本土信息强 |
| **Apify MCP** | API接入 | 电商爬取：1688/淘宝/天猫/闲鱼/抖音（Actor付费） | Actor按次计费 | ✅ 国内电商 |

## SearXNG 完整引擎分类（248个）

| 类别 | 引擎 |
|------|------|
| 🌐 通用网页 | Google / Bing / DuckDuckGo / Brave / Yahoo / Yandex / Qwant / Startpage / Mojeek / Swisscows / Kagi / Presearch / Naver / Sogou（搜狗）/ Baidu（百度）/ 360搜索 / ChinaSo |
| 📰 新闻 | Bing News / Google News / Yahoo News / Reuters / Swisscows News |
| 🖼️ 图片 | Google Images / Bing Images / Sogou Images / 500px / DeviantArt / Flickr / Imgur / Pexels / Pixabay / Unsplash |
| 🎬 视频 | Bing Videos / Google Videos / YouTube / Bilibili / Dailymotion / Vimeo / PeerTube / Rumble / Odysee / Niconico |
| 📚 学术 | ArXiv / PubMed / Google Scholar / Semantic Scholar / CrossRef / OpenAlex / Springer |
| 💻 代码 | GitHub / GitLab / NPM / PyPI / Docker Hub / HuggingFace / StackExchange |
| 🛒 购物 | eBay / Shopify Stock |
| 📱 社交 | Reddit / HackerNews / Mastodon |
| 🎮 游戏/娱乐 | Steam / IMDb / 9GAG / Bandcamp / SoundCloud |
| 🏴‍☠️ 种子 | 1337x / PirateBay / Kickass / Nyaa |
| 🇨🇳 中文专用 | Baidu / Bilibili / Sogou / 360Search / AcFun / IQIYI / ChinaSo |

## AnySearch 垂直领域（22个，部分 tag 名称待确认）

| 领域 | 子领域 | 典型用途 |
|------|--------|---------|
| finance | finance.quote / finance.market / finance.news / finance.company | 股票行情、市场趋势 |
| academic | academic.paper / academic.author / academic.journal / academic.conference | 论文搜索 |
| security | security.cve / security.advisory / security.threat | CVE漏洞、安全公告 |
| legal | legal.case / legal.statute / legal.regulation | 法律案例、法规 |
| code | code.repository / code.issue / code.package | GitHub仓库、Issue |
| travel | travel.flight(IATA) / travel.hotel / travel.destination | 航班、酒店 |
| health | health.drug / health.condition / health.clinical_trial | 药品、疾病 |
| gaming | gaming.game / gaming.achievement / gaming.player | 游戏数据库 |
| film | film.movie / film.tv / film.celebrity / film.review | 电影、影评 |
| business | business.company / business.patent / business.news | 企业信息 |
| social_media | social_media.reddit / social_media.x / social_media.threads | 社媒讨论 |
| ip | ip.patent / ip.trademark | 专利、商标 |
| energy | energy.price / energy.report | 能源价格 |
| environment | environment.weather / environment.pollution | 环境数据 |
| agriculture | agriculture.price / agriculture.report | 农产品价格 |
| resource | resource.commodity / resource.mineral | 大宗商品 |

## 搜索工具选择决策树

```
查询类型？
  │
  ├─ 通用中文网页搜索 → open-webSearch（百度/搜狗）或 秘塔
  ├─ 通用英文网页搜索 → open-webSearch（Bing/Brave）或 Tavily
  ├─ 学术论文 → Exa（category=research paper）或 SenseNova sn-search-academic
  ├─ 代码/GitHub → SenseNova sn-search-code
  ├─ 金融/股票 → SenseNova sn-search-finance
  ├─ 中文社交(B站/知乎/抖音) → SenseNova sn-search-social-cn
  ├─ 热点监控(微博/知乎/头条) → TrendRadar
  ├─ 小红书 → xhs-cli
  ├─ 电商数据 → Apify MCP（需配置）
  ├─ 深度研究 → SenseNova sn-deep-research
  ├─ 垂直领域(代码/金融/法律/学术等) → AnySearch（已配，1,000次/天）
  ├─ 需要自建可控/隐私敏感 → SearXNG Docker（需服务器）
  └─ 本地笔记 → Obsidian RAG
```

## 呈现规则（必须遵守）

1. **枚举source时必须具体到引擎名称**，不能说"通用搜索"或"多个引擎"就完事
2. 中文友好度是必备维度，单独列出来
3. 对比表格必须有详细分类展开，不能只有概括性描述
