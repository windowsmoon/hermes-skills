# 搜索工具引擎对比

## open-webSearch vs SearXNG vs AnySearch

| 维度 | open-webSearch | SearXNG | AnySearch |
|------|---------------|---------|-----------|
| 部署 | `npm install -g` | Docker 自建 | API 注册 |
| 引擎数 | 10 个 | 248 个 | 通用 + 15 垂直领域 |
| MCP | 原生 MCP | 无 | 原生 MCP |
| 免 Key | ✅ | ✅ | 匿名可用 |
| 中文源 | Baidu/Sogou/CSDN/掘金 | Baidu/360/Sogou/Bilibili/AcFun | ❌ 无百度中文源 |

## open-webSearch 引擎列表
baidu, bing, duckduckgo, sogou, csdn, juejin, brave, startpage, exa, linuxdo

## SearXNG 中文引擎
baidu, 360search, sogou, sogou_images, sogou_videos, sogou_wechat, chinaso, bilibili, acfun, iqiyi

## 路由规则（用户确认 2026-07-20）
| 搜索类型 | 首选工具 |
|---------|---------|
| 通用信息/数据/知识 | open-webSearch --engine baidu（中文）或 bing（英文） |
| 热点/新闻/实时 | TrendRadar（8平台） |
| 深度研究/竞品分析 | unified-search（Tavily+Exa+秘塔+Firecrawl） |
| 学术/论文/百科 | sensenova-search-academic |
| 代码/开源/API/Skill | sensenova-search-code |
| 中文UGC自媒体 | sensenova-search-social-cn + xhs-cli |
| 海外自媒体 | sensenova-search-social-en |
| 图片 | sensenova-search-image |
| 商业/财经/公司 | sensenova-finance + market-cn + year-report |
| 爬虫/反爬 | Tabbit浏览器 + Firecrawl |
| 垂直领域（股票/CVE/专利/航班） | AnySearch（需注册） |
