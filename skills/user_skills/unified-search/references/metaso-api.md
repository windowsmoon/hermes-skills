# 秘塔搜索 API 集成笔记

## 基本信息

- **平台**: 秘塔AI搜索 (metaso.cn)
- **API 文档**: https://metaso.cn/search-api/playground
- **端点**: `POST https://metaso.cn/api/v1/search`
- **认证**: `Authorization: Bearer mk-xxx`
- **Content-Type**: `application/json`

## 请求格式

```json
POST https://metaso.cn/api/v1/search
Authorization: Bearer mk-xxx
Content-Type: application/json

{
  "q": "搜索关键词",
  "scope": "web",
  "count": 10,
  "page": 1,
  "conciseSnippet": true,
  "includeSummary": true
}
```

参数说明:
- `q` — 搜索查询词（必填）
- `scope` — 搜索范围，可选值：
  - `"web"` — 网页搜索（默认）
  - `"academic"` — 学术搜索
  - `"news"` — 新闻搜索
  - `"wiki"` — 百科搜索
  - `"video"` — 视频搜索
- `count` — 每页结果数（最大 10）
- `page` — 页码（从 1 开始），支持翻页获取更多结果：`total` 字段返回总结果数，可据此翻页
- `conciseSnippet` — true 返回精简的原文匹配信息
- `includeSummary` — true 通过网页的摘要信息进行召回增强

## 返回格式

```json
{
  "credits": 3,
  "searchParameters": { "q": "...", "scope": "web", ... },
  "webpages": [
    {
      "title": "文章标题",
      "link": "https://...",
      "score": "high" | "medium" | "low",
      "snippet": "文章摘要文本...",
      "position": 1,
      "date": "2026年07月08日"
    }
  ]
}
```

## 关键字段

| 字段 | 说明 |
|------|------|
| `credits` | 剩余调用额度（消耗完需充值） |
| `webpages[].title` | 文章标题 |
| `webpages[].link` | 文章 URL |
| `webpages[].snippet` | 内容摘要（中文质量不错） |
| `webpages[].score` | 相关性评分: `high`/`medium`/`low` |
| `webpages[].date` | 发布日期（中文格式字符串） |
| `webpages[].position` | 排序位置 |

## 注意事项

1. **Key 格式**: `mk-` 前缀，来自 https://metaso.cn/search-api/ 页面
2. **计费**: 每次搜索消耗 credits，额度用完后 API 返回 402 或额度相关错误。但实测多次调用 credits 不递减，可能是按账号维度统一计费或有缓存
3. **参数命名**: 使用 `q`（不是 `query`）、`count`（不是 `maxResults`）、`link`（不是 `url`）——与多数搜索 API 命名不同，易混淆
4. **日期**: date 字段是中文格式字符串，如 "2026年07月08日"
5. **MCP 支持**: 秘塔官方已支持 MCP 协议（详见 metaso.cn search-api 页面）
6. **分页**: `count` 上限为 10，但支持 `page` 参数翻页，`total` 字段返回总结果数，可据此计算页数。单次请求最多返回 10 条，但通过遍历 page=1,2,3... 可获任意数量
7. **scope 测试结果**: `web`/`academic`/`news`/`wiki` 均正常工作且返回不同结果；`video` 返回 0 条（可能无视频索引）
