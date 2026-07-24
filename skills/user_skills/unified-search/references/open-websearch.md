# open-webSearch 集成参考

## 项目信息

- GitHub: https://github.com/Aas-ee/open-webSearch (⭐1614)
- 安装方式: `npm install -g open-websearch` 或 `npx -y open-websearch`
- 无需 API Key（直接爬搜索引擎）
- 引擎列表: bing, baidu, csdn, duckduckgo, exa, brave, juejin, startpage, sogou

## Hermes 集成状态

已在 Hermes Studio 注册为 MCP Server `open-websearch`，配置如下：
- command: `npx`
- args: `["-y", "open-websearch"]`
- transport: stdio

## 环境变量

- `OWS_ENGINE` — 默认引擎（如 `baidu`、`bing`），unified_search.py 自动读取

## CLI 用法

```bash
open-websearch search "<查询词>" --engine bing --limit 10 --json
open-websearch fetch-web <url> --readability --json
open-websearch fetch-csdn <url> --json
open-websearch fetch-juejin <url> --json
```

## MCP 工具名映射

| CLI 命令 | MCP 工具名 |
|----------|-----------|
| search | search |
| fetch-web | fetchWebContent |
| fetch-csdn | fetchCsdn |
| fetch-github-readme | fetchGithubReadme |
| fetch-juejin | fetchJuejin |

## 返回格式

```json
{
  "status": "ok",
  "data": {
    "results": [
      {"title": "...", "url": "...", "description": "...", "source": "...", "engine": "bing"}
    ]
  }
}
```

注意：结果在 `data.results` 中，摘要字段为 `description` 而非 `content`。
