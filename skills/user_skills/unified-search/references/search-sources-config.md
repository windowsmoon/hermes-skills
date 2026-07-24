# 搜索源配置手册

本文档记录了 unified-search 各搜索源的 API 端点、参数、凭证位置和注意事项。

## Tavily
- 端点: POST https://api.tavily.com/search
- 认证: JSON body `api_key` 字段
- Key 位置: ~/.hermes/.env → TAVILY_API_KEY
- 上限: 10条/次（免费版硬上限）
- 参数: query, max_results(≤10), include_answer=true

## Exa
- 端点: POST https://api.exa.ai/search
- 认证: Header `x-api-key`
- Key 位置: ~/.hermes/.env → EXA_API_KEY
- 参数: query, numResults, category(research paper/news/article/company/pdf)
- **必须加** `contents: {text: true}` 否则 content 为空

## 秘塔
- 端点: POST https://metaso.cn/api/v1/search
- 认证: Header `Authorization: Bearer <key>`
- 参数: q, scope(web/news/academic/wiki/video), count, page
- 分页: page翻页，每页10条

## Firecrawl
- 端点: POST https://api.firecrawl.dev/v0/search（用v0非v1）
- 认证: Header `Authorization: Bearer <key>`

## open-webSearch
- 安装: npm install -g open-websearch
- CLI: npx -y open-websearch search <q> --engine <e> --limit N --json
- 支持引擎: bing/baidu/csdn/duckduckgo/exa/brave/juejin/sogou

## 今日热榜
- 端点: GET https://api.tophubdata.com/search
- 认证: Header `Authorization: <key>`（直接传key）
- 实际参数: keyword（文档写q但q常超时）
- 返回: title, description(常空), url, extra(热度), time
