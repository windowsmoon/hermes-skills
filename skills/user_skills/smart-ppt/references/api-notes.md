# Smart PPT 实现笔记

## 文多多 API 要点

### 认证
- API Key 有效期: 长期
- Token 有效期: 2 小时（`POST /api/user/createApiToken`）
- UID 参数用于数据隔离，同一个 UID 创建新 token 后旧 token 10 秒内失效

### SSE 流式解析
```python
# 文多多的大纲/内容生成使用 SSE（Server-Sent Events），非标准 JSON 响应
# 正确解析方式：
resp = urllib.request.urlopen(req, timeout=180)
text = ""
while True:
    line = resp.readline()
    if not line: break
    ln = line.decode("utf-8", errors="replace").strip()
    if ln.startswith("data:"):
        d = json.loads(ln[5:])
        if "text" in d: text += d["text"]
```
- 错误信号：`{"status": -1, "error": "..."}`
- 内容信号：`{"text": "..."}`

### API 端点（BASE = https://docmee.cn）
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/user/createApiToken` | POST | 创建 token，header 用 `Api-Key` |
| `/api/ppt/generateOutline` | POST | SSE 流式，header 用 `token` |
| `/api/ppt/generateContent` | POST | SSE 流式，header 用 `token` |
| `/api/ppt/randomTemplateId` | GET | header 用 `token` |
| `/api/ppt/generatePptx` | POST | header 用 `token` |
| `/api/ppt/downloadPptx?id={id}` | GET | header 用 `token` |

## ChatPPT CLI 要点

### 模板列表
```bash
chatppt ppt template --limit 50 -o json
```
返回结构：`{"code":200,"data":{"count":79,"data":[{"show_id":"6BC5rT","title":"...","style":"..."}]}}`

### 生成参数
| 参数 | 说明 |
|------|------|
| `--custom-template-id` | 模板 ID（79 个可选） |
| `--custom-page-count` | 页数（默认 10） |
| `--language zh-CN` | 中文 |
| `--ai-picture true` | AI 配图 |
| `--font-name` | 字体 |
| `--image-style` | 图片风格 |
| `--poll` | 启用轮询等待完成（推荐） |

### 模板风格示例
- 卡通风、现代风、商务风、科技风、简约风
- 可通过 `--style "商务风"` 参数筛选
