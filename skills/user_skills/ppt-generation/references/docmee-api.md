# 文多多 (docmee.cn) API 参考

## 基本配置

| 项目 | 值 |
|------|-----|
| Base URL | `https://docmee.cn` |
| API Key | `ak_s_Q1m1s3T6Fs5imN4_` |
| 模式 | 两步授权：Api-Key → token(2h) → token 后续请求 |

## 完整流程（6步）

### Step 1: 创建 Token
```
POST /api/user/createApiToken
Headers: Api-Key: <your-key>
Body: {"uid": "用户标识", "limit": null}
→ 返回: {"code":0, "data":{"token":"sk_...","expireTime":7200}}
```

### Step 2: 生成大纲（SSE 流式）
```
POST /api/ppt/generateOutline
Headers: token: <from step 1>
Body: {"subject": "主题", "dataUrl": null, "prompt": null}
→ SSE 流式返回，每行 data: {"text":"..."}
→ 用 resp.readline() 逐行读取，拼接 text 字段
```

### Step 3: 生成内容（SSE 流式）
```
POST /api/ppt/generateContent
Headers: token: <from step 1>
Body: {"subject": "主题", "dataUrl": null, "prompt": null}
→ 同上 SSE 流式
```

### Step 4: 获取模板
```
GET /api/ppt/randomTemplateId
Headers: token: <from step 1>
→ 返回: {"data":{"id":"模板ID"}}
```

### Step 5: 生成 PPTX
```
POST /api/ppt/generatePptx
Headers: token: <from step 1>
Body: {"templateId": "xxx", "markdown": "markdown内容"}
→ 返回: {"data":{"id":"ppt_id"}}
```

### Step 6: 下载
```
GET /api/ppt/downloadPptx?id=<ppt_id>
Headers: token: <from step 1>
→ 返回: {"data":{"fileUrl":"下载链接"}}
```

## SSE 解析要点

```python
# 正确做法：逐行读取，解析 data: 前缀
with urllib.request.urlopen(req, timeout=180) as resp:
    text = ""
    while True:
        line = resp.readline()
        if not line: break
        ln = line.decode("utf-8", errors="replace").strip()
        if ln.startswith("data:"):
            d = json.loads(ln[5:])
            if "text" in d: text += d["text"]
            if d.get("status") == -1:
                raise Exception(d.get("error",""))
```

## 注意

- Token 有效期 2 小时，过期需重新创建
- 同 uid 创建新 token 时，旧 token 会在 10 秒内失效
- 生成大纲的 subject 可包含附件文本（拼接在主题后）
- API 需要 requests 库（如果用纯 urllib 需手动处理 SSE）
