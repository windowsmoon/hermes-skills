# 图片生成实测笔记（2026-07-09）

## 心流grop 供应商实测

### ❌ gpt-image-2 完全不可用

**连续10+次测试全部被拦截**，无论：
- 中文/英文 prompt
- 长/短 prompt（50-500字符）
- 有无敏感词（包括"hello"和"一只猫"）

错误信息：
```
"Your request could not be used to generate an image. It may be blocked by safety policies."
```

**结论**：心流grop 的 gpt-image-2 模型已暂停/下线，非 prompt 问题。

### ✅ gemini-2.5-flash-image-preview 可用

- 模型 key：`gemini-2.5-flash-image-preview`
- 返回格式：base64 内嵌图片
- 成功生成 774KB 中文信息图
- 全中文 prompt 正常响应

### ⚠️ agnes-image-2.0-flash 不可用

错误：模型无可用渠道（distributor），503 错误。

## 图片 Prompt 规则（用户明确要求）

### 用户原话
> "你的提示词一定不能够有英文；用MD格式把作者的观点和事实或者事物发展过程用简约的中文概括描述，不要一大段的文字给过去；用最能表达整个概括描述的逻辑编排构图，用最有代表性的图标或者图案/图例表达每个观点文字意思，用给老板看的标准（一眼就懂）的PPT级别的可视化方式做图片每个框里的图来呈现内容"

### 规则总结
1. **禁止英文** — prompt 全中文，不出现一个英文字母
2. **简约中文概括** — 用 Markdown 格式（列表/标题），不要大段文字
3. **PPT级别可视化** — 给老板看，一眼就懂
4. **图标/图案/图例** — 每个观点配代表性图标
5. **逻辑编排构图** — 按描述逻辑排布（时间线/流程图/对比图）
6. **信息密度拉满** — 每张图至少5-8个核心信息点

### 正确的 Prompt 模板
```
创建一张赛博朋克风格知识信息图。

标题：饭圈文化演变与互联网极化

内容：
- 1990-2004：追星1.0 私人情感 收集海报 抄歌词
- 2005：超级女声短信投票 粉丝权力感启蒙
- 2005-2017：微博贴吧QQ群 组织化
- 2014：EXO归国 韩式方法论输入
- 2018：偶像练习生 消费=投票权
- 2020+：饭圈逻辑向地缘政治扩散
- 现在：全面渗透 二极管思维

风格：深黑底+青色网格+霓虹光晕+中文+信息密度拉满
```

## API 调用代码

```python
import requests, json, base64

API_KEY = "sk-jDRslt0kupSc7zgHGPkbTuqG2FPnFyznmqpgntGLzq2N9z2L"
BASE_URL = "https://cdn.wusag.com/v1"

payload = {
    "model": "gemini-2.5-flash-image-preview",
    "messages": [{"role": "user", "content": prompt}],
    "n": 1,
    "size": "1344x768"
}
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=180)

if resp.status_code == 200:
    content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    if "base64," in content:
        start = content.find("base64,") + 7
        end = content.find(")", start)
        b64 = content[start:end].strip()
        img_bytes = base64.b64decode(b64)
        with open("output.png", 'wb') as f:
            f.write(img_bytes)
```

## 熔断规则（用户明确要求）

> "不能重复请求，最多一次任务请求生成两次图片，如果一次生成成功就上传，如果两次都失败就熔断不上传"

**执行流程：**
1. 第1次请求 → 成功则上传，结束
2. 第1次失败 → 第2次请求 → 成功则上传，结束
3. 第2次也失败 → **熔断，不再重试**，跳过图片步骤，先把其他内容整理到飞书文档

---

## 豹剪 API 图片生成（2026-07-20 实测，✅ 推荐）

### 凭证
| 项目 | 值 |
|------|-----|
| API Key | `sk-naweFNcH8H7sGyDcNYhOf86GbHSrs23Lb1cFDiwjDyPYb265` |
| Base URL | `https://api.bjzy.nfai.top/v1` |
| Model | `gpt-image-2-4k` |
| 端点 | `/v1/chat/completions`（非 `/v1/images/generations`） |

### ⚠️ SSL 问题（关键）
- `requests.post()` 报 `SSLError: record layer failure`
- `requests.post(verify=False)` 同样报 SSL 错误
- **必须用 `urllib.request.urlopen(context=ctx)`**，其中 `ctx` 为禁用证书验证的 SSL context
- 原因：该域名使用非标准 SSL 证书

### 调用代码
```python
import urllib.request, json, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

payload = json.dumps({
    "model": "gpt-image-2-4k",
    "messages": [{"role": "user", "content": prompt}]
}).encode()
req = urllib.request.Request(
    "https://api.bjzy.nfai.top/v1/chat/completions",
    data=payload,
    headers={
        "Authorization": "Bearer sk-naweFNcH8H7sGyDcNYhOf86GbHSrs23Lb1cFDiwjDyPYb265",
        "Content-Type": "application/json"
    },
    method="POST"
)
with urllib.request.urlopen(req, timeout=180, context=ctx) as r:
    result = json.loads(r.read())
    content = result["choices"][0]["message"]["content"]
    # 返回 Markdown 格式: ![title](https://pro.filesystem.site/cdn/.../xxx.png)
    urls = re.findall(r'https?://[^\s")<>]+\.(?:png|jpg|jpeg|webp)', content)
    if urls:
        # 下载图片
        with urllib.request.urlopen(urls[0], timeout=30, context=ctx) as img_r:
            img_bytes = img_r.read()
```

### 返回格式
- 返回 Markdown 文本，包含图片 URL（指向 `pro.filesystem.site` CDN）
- 非 base64 内嵌
- 图片 URL 有时效性（CDN 缓存），建议下载到本地后使用

### 在飞书 docx API 中的使用限制
- 豹剪生成的图片可下载到本地后通过 `drive/v1/medias/upload_all` 上传到飞书
- 但 `docx/v1/documents/{id}/blocks/{id}/children` 插入 `block_type=17` 图片块时返回 `1770001 invalid param`
- **workaround**：使用 `lark-cli docs +media-insert --as bot` 代替直接 REST API（见 `feishu-image-block-notes.md`）
- 或：在飞书文档中以文字链接形式插入 CDN URL（兜底方案）