# Exa 搜索集成笔记

## 基本信息

- **端点**: POST https://api.exa.ai/search
- **认证**: Header `x-api-key: 67cc607e-xxx`
- **Content-Type**: `application/json`

## 请求格式

```json
POST https://api.exa.ai/search
x-api-key: 67cc607e-xxx
Content-Type: application/json

{
  "query": "搜索词",
  "numResults": 10,
  "useAutoprompt": true,
  "category": "research paper",
  "contents": {
    "text": true
  }
}
```

## category 参数（2026-07-17 发现）

Exa 支持 `category` 参数来限定搜索范围 —— **添加后结果差异显著**：

| 值 | 范围 | 实测效果 |
|----|------|:--------:|
| `"research paper"` | 学术论文 | ✅ 返回 arxiv 论文，含标题/作者/摘要 |
| `"news"` | 新闻 | ✅ 新闻类结果 |
| `"article"` | 文章 | ✅ 综合文章 |
| `"company"` | 公司/产品信息 | ✅ |
| `"pdf"` | PDF 文档 | ✅ |
| 不传（默认） | 全网 | ⚠️ 中文内容常为空 |

**建议**：中文用户搜索时始终指定 `category`（如 `"research paper"` 或 `"article"`），能显著提升内容返回率。

## contents.text 参数（2026-07-17 发现）

添加 `"contents": {"text": true}` 后，Exa 会返回 `text` 字段（含正文摘要），不再为空：

```json
{
  "results": [{
    "title": "论文标题",
    "url": "https://arxiv.org/...",
    "text": "论文摘要和正文前几段...",   // ← 之前为空，加了 contents.text 后就有内容了
    "score": 0.95
  }]
}
```

**没有 `contents: {"text": true}`** 时，Exa 返回的 `text`/`content` 字段几乎永远为空（尤其是中文搜索）。这是 Exa 的设计，不是 bug。

## 坑点：未指定 category 时 content/text 字段为空

**这是 Exa 的设计行为**——不加 contents.text 时非英文搜索的 content/text 字段常为空。

### 解决方法：URL 内容补全

Exa 至少返回 `title` 和 `url`，即便 content 为空。对每个 Exa 返回的 URL，用以下方法抓取正文摘要：

```python
import re, urllib.request

html = urllib.request.urlopen(url, timeout=10).read().decode('utf-8', errors='replace')
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '', text)
text = re.sub(r'\\s+', ' ', text).strip()
paragraphs = [p.strip() for p in text.split('\\n') if len(p.strip()) > 30]
meaningful = [p for p in paragraphs if len(re.findall(r'[\\u4e00-\\u9fff]', p)) > 10]
preview = meaningful[0][:400] if meaningful else text[:300]
```

或者使用 Hermes 内置的 `web_extract` 工具。

## Exa 擅长领域

- 学术论文检索（返回 papernotes.org 等学术站点）
- 英文技术文章
- CVPR / ECCV / ICLR 等顶会论文

## 不擅长

- 中文长文摘要（content 常为空）
- 普通新闻/博客类内容（不如 Tavily 实用）
