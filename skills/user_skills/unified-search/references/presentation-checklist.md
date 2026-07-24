# 搜索结果呈现清单

Agent 向用户输出搜索结果时，逐项检查：

## 呈现前 Checklist

- [ ] 每条结果都有 🔗 URL（完整可点击）
- [ ] 每条结果都有 📝 内容快照（200-400字，从原文抓取）
- [ ] 如果快照抓取失败，注明原因（反爬/超时/403）
- [ ] 每个搜索源标注状态（✅ / ⚠️ / ⚪）
- [ ] 空结果的源解释了原因（没写明白，不要只写"无结果"）
- [ ] 标记了推荐优先级（🔥 最推荐 / 📖 其次 / 📎 参考）
- [ ] 学术论文（Exa）和网文（Tavily）分开展示

## 快照抓取方法

```python
import re, urllib.request

html = urllib.request.urlopen(url, timeout=10).read().decode('utf-8', errors='replace')
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '', text)
text = re.sub(r'\s+', ' ', text).strip()
paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 30]
meaningful = [p for p in paragraphs if len(re.findall(r'[\u4e00-\u9fff]', p)) > 10]
preview = meaningful[0][:400] if meaningful else text[:300]
```

## 来源状态标注

- `✅` 正常返回结果
- `⚠️ 部分异常` 返回了但内容不完整（如 Exa 无正文）
- `🔴 失败` API 调用报错，注明错误原因
- `⚪ 未命中` 正常运行但无匹配结果
