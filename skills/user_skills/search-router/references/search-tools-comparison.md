# 搜索工具对比参考

> 2026-07-20 调研结论

## open-webSearch vs SearXNG vs AnySearch

| 维度 | open-webSearch | SearXNG | AnySearch |
|------|---------------|---------|-----------|
| ⭐ Stars | 1,619 | 34,122 | Skill 4,554 / MCP 1,553 |
| 部署 | npm install -g | Docker 自建 | API 接入 |
| 免 Key | ✅ 是 | ✅ 是 | 匿名可用，注册 API Key 提速 |
| MCP | ✅ 原生 MCP | ❌ 需自建 | ✅ 原生 MCP |
| 引擎数 | 10 | **248** | 通用 + 15 垂直领域 |
| 中文源 | Baidu/Sogou/CSDN/掘金 | Baidu/Sogou/360/B站/AcFun/ChinaSo | ❌ 无 |
| 垂直搜索 | ❌ | ❌ | ✅ 股票/CVE/论文/专利/航班等 |

## open-webSearch 10 个引擎

Baidu、Bing、Sogou、DuckDuckGo、Brave、Startpage、CSDN、掘金、Exa（需 Key）

## SearXNG 248 个引擎（按类别）

| 类别 | 引擎 |
|------|------|
| 通用网页 | Google、Bing、DuckDuckGo、Brave、Yahoo、Yandex、Qwant、Startpage、Kagi、**Baidu**、**Sogou**、**360Search**、**ChinaSo** |
| 新闻 | Bing News、Google News、Reuters |
| 图片 | Google Images、Bing Images、500px、DeviantArt、Flickr、Pexels、Pixabay、Unsplash |
| 视频 | YouTube、Bing Videos、**Bilibili**、Dailymotion、Vimeo、PeerTube |
| 学术 | ArXiv、PubMed、Google Scholar、Semantic Scholar、CrossRef |
| 代码 | GitHub、GitLab、NPM、PyPI、Docker Hub、HuggingFace、StackExchange |
| 音乐 | Bandcamp、SoundCloud、Spotify、Deezer |
| 购物 | eBay |
| 社交 | Reddit、HackerNews、Mastodon |
| 中文专用 | **Baidu、Bilibili、Sogou、360Search、AcFun、IQIYI、ChinaSo** |
| 种子 | 1337x、PirateBay、BTDigg |

## AnySearch 15 个垂直领域

finance(股票/市场/新闻)、academic(论文/作者/期刊)、security(CVE/威胁)、legal(案例/法规)、code(仓库/Issue/包)、travel(航班/酒店)、health(药品/临床)、gaming(游戏/成就)、film(电影/TV/名人)、business(企业/专利)、social_media、ip(专利/商标)、energy、environment、agriculture

## 决策树

```
日常中文搜索 → open-webSearch --engine baidu
日常英文搜索 → open-webSearch --engine bing
隐私搜索 → open-webSearch --engine duckduckgo 或 --engine startpage
垂直领域搜索 → AnySearch（需注册）
全量搜索/自部署 → SearXNG（需 Docker）
```
