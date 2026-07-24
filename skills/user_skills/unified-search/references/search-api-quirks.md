# 搜索 API 集成笔记

## Tavily

- **端点**: POST https://api.tavily.com/search
- **认证**: JSON body 内传递 `api_key` 字段
- **参数**: `query`, `max_results` (默认5, 免费版上限10), `include_answer` (AI摘要), `include_raw_content`
- **返回**: `results[]` 含 `title`, `url`, `content`(约200字摘要), `score`(0-1)
- **限频**: 免费 1000 次/月
- **注意**: content 是 AI 生成的摘要，非原文。需要原文摘要需额外抓取。

## 秘塔搜索 (Metaso)

- **端点**: POST https://metaso.cn/api/v1/search
- **认证**: Header `Authorization: Bearer mk-xxx`
- **参数**: `q`(查询词), `scope`(web/academic/news/wiki/video), `count`(每页最多10), `page`(翻页)
- **选项**: `conciseSnippet: true`, `includeSummary: true`（获取内容摘要）
- **返回**: `webpages[]` 含 `title`, `link`, `snippet`(摘要), `score`(high/medium), `date`, `position`
- **分页**: count 单独无效（硬上限10），用 `page` 翻页。实测翻7页不扣 credits
- **额度**: credits 在返回中体现，每次请求不递减
- **MCP 支持**: 页面显示"已支持MCP协议"
- **注意**: scope='video' 可能无索引返回0条

## Exa（更新）

- **端点**: POST https://api.exa.ai/search
- **认证**: Header `x-api-key`
- **参数**: `query`, `numResults`, `useAutoprompt`(自动优化query), `category`(搜索类别), `contents: {text: true}`(获取正文)
- **category 支持**: `research paper`, `news`, `article`, `company`, `pdf`
- **正文获取**: 加上 `{"contents": {"text": true}}` 返回正文。不加则 text 为空
- **返回**: `results[]` 含 `title`, `url`, `text`(需 contents.text), `score`
- **坑点**: text 字段仍可能为空（免费版限制），需配合 Exa Content endpoint 或自行爬取
- **擅长**: 学术论文、英文技术文章

## open-webSearch

已注册为 Hermes MCP Server。详见 `references/open-websearch.md`。
CLI 集成：`scripts/unified_search.py` 通过 `OWS_ENGINE` 环境变量切换引擎。

## Firecrawl

- **端点 (v0)**: POST https://api.firecrawl.dev/v0/search ← 用户当前Key是v0
- **端点 (v1)**: POST https://api.firecrawl.dev/v1/search ← v1参数不同
- **认证**: Header `Authorization: Bearer fc-xxx`
- **v0 参数**: `query`, `maxResults`
- **v1 参数**: 使用 `limit` 而非 `maxResults`
- **v0 返回**: `data[]` 含 `content`(含原始HTML/Markdown)，**无**独立的 `title` 和 `url` 字段(需从 content 正则解析)
- **坑点**: v1 不认识 `maxResults` 参数会报 400。v0 返回的 title/url 为空字符串，
          URL 可能嵌在 content 的 Markdown 链接中，需用 `re.findall(r'https?://[^\s)]+', content)` 提取

## 环境变量

四个 Key 存储在 `~/.hermes/.env`：
- `TAVILY_API_KEY`
- `EXA_API_KEY`  
- `FIRECRAWL_API_KEY`
- `MITA_API_KEY`（秘塔）

以及搜索范围环境变量（通过 --scope 参数自动设置）：
- `MITA_SCOPE` — 秘塔搜索范围（web/academic/news/wiki/video）
- `EXA_CATEGORY` — Exa 搜索类别（news/article/research paper/company/pdf）
- `OWS_ENGINE` — open-webSearch 引擎（bing/baidu/csdn/sogou...）

调用子进程时必须显式传递 `env` 参数加载这些变量，subprocess 不会自动读取 .env 文件。

## 摘要快照

- 对每条返回的文章，用 `web_extract` 或 `urllib` GET 抓取 HTML
- 用 regex 去标签：`re.sub(r'<[^>]+>', '', html)`（先去掉 script/style 块）
- 提取含中文的段落：`re.findall(r'[^\n]{30,}', text)` 然后过滤 `len(re.findall(r'[\u4e00-\u9fff]', p)) > 10`
- 取第一个段落的前 200-400 字作为快照
- 抓取失败时注明原因（反爬/超时/403），不返回空
