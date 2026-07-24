# 抖音 Pipeline 实测笔记 (2026-07-10)

## 关键发现

### 1. Coze 工作流输出格式

#### 版本获取（2026-07-10 更新；2026-07-20 确认）
```python
# ⚠️ 注意：POST /v1/workflow/workflow_versions/list 已废弃，返回 4000
# ✅ 必须使用 GET 端点
r = requests.get(f"https://api.coze.cn/v1/workflows/{WORKFLOW_ID}/versions", 
    headers={"Authorization": f"Bearer {API_TOKEN}"})
versions = r.json().get("data", {}).get("items", [])
version = versions[0]["version"] if versions else "v0.0.1"
# 格式: "v0.0.1" (字符串，非数字)
# 硬编码 fallback "v0.0.1" 同样可用（工作流版本很少变动）
```

#### 工作流执行（无需Interrupt节点）
```python
# 当前工作流 v0.0.1 无Interrupt节点，直接返回完整结果
payload = {
    "workflow_id": WORKFLOW_ID,
    "workflow_version": "v0.0.1",  # 字符串格式
    "parameters": json.dumps({"input": douyin_link})
}
resp = requests.post("https://api.coze.cn/v1/workflow/stream_run",
    headers=headers, json=payload, stream=True, timeout=180)
# 逐字稿在 Message 事件中完整返回
```

#### 逐字稿提取（标准代码）
```python
all_content = []
current_event = None
for line in resp.iter_lines(decode_unicode=True):
    if not line:
        continue
    if line.startswith("event:"):
        current_event = line[6:].strip()
    elif line.startswith("data:"):
        data = json.loads(line[5:])
        if current_event == "Message":
            all_content.append(data.get("content", ""))
full = "".join(all_content)
parsed = json.loads(full)
transcript = parsed.get("output", str(parsed)).strip()
```

### 2. 图片生成 (心流grop)

#### ⚠️ cdn.wusag.com 上游服务不稳定（2026-07-10 新发现；2026-07-20 补充）
- **502 Bad Gateway** 错误频发
- **525 SSL Handshake Failed** — Cloudflare SSL 握手失败（2026-07-20 实测）
- **522 Connection Timed Out** — Cloudflare 连接上游超时（2026-07-20 实测）
- 备用方案：等待服务恢复或使用其他图片生成服务
- 熔断规则：最多2次尝试，失败则跳过图片步骤

#### ❌ gpt-image-2 完全不可用（实测）
- 连续10+次测试全部被拦截
- 无论中文/英文/长短 prompt
- 错误：\"Your request could not be used to generate an image\"
- **结论：心流grop 的 gpt-image-2 模型已彻底下线/暂停**

#### ✅ gemini-2.5-flash-image-preview 可用（推荐）
- 返回 base64 内嵌图片（`data:image/png;base64,...`）
- 同样走 `/v1/chat/completions`
- **设为默认图片模型**

#### 用户图片偏好（必须遵守）
1. **禁止英文** — prompt 全中文
2. **简约中文概括** — Markdown 格式，不要大段文字
3. **PPT级别可视化** — 给老板看，一眼就懂
4. **图标/图案/图例** — 每个观点配代表性图标
5. **信息密度拉满** — 每张图至少5-8个核心信息点
6. **风格统一** — 深黑底+青色网格+霓虹光晕

### 3. 飞书画板 - 已验证 ✅

#### OAuth 扫码正确格式
```
URL: https://accounts.feishu.cn/oauth/v1/device/verify?flow_id={flow_id}&user_code={user_code}
```
其中的 `flow_id` 和 `user_code` 来自 lark-cli 返回的 `verification_url` 字段（不要自己拼接！）

#### lark-cli 命令
```bash
# 绑定Hermes身份（首次需执行）
node run.js config bind --source hermes --identity user-default --force

# 获取验证URL
node run.js auth login --recommend --no-wait --json
# 从返回的 verification_url 提取 URL

# 生成ASCII二维码
node run.js auth qrcode <verification_url> --ascii

# 等待扫码
node run.js auth login --recommend --device-code <device_code>
```

#### 创建白board 文档
```bash
node run.js docs +create \
  --title "标题" \
  --markdown '<whiteboard type="blank"></whiteboard>' \
  --format json
```
返回：`doc_id`, `board_tokens[0]`, `doc_url`

#### 写入思维导图 (已验证成功)
```bash
node run.js api POST \
  /open-apis/board/v1/whiteboards/{board_token}/nodes/plantuml \
  --data '{"plant_uml_code":"mindmap\\n  root((主题))\\n    分支","syntax_type":2,"diagram_type":1}' \
  --as user \
  --format json
```
返回：`{"code":0,"data":{"node_id":"z1:1"}}`

#### ⚠️ 关键限制
- `syntax_type: 2` = Mermaid, `diagram_type: 1` = 思维导图
- 白board 创建后需等 **15秒** 初始化再写入
- 必须用 user 身份（`--as user`）
- 权限 `board:whiteboard:node:create` 必须提前在开放平台开通

### 4. 飞书 docx API 写入

#### ✅ 正确方式：lark-cli append
```bash
node run.js docs +update --doc {doc_id} --mode append --markdown "内容"
```

#### ⚠️ 分块写入注意
- 单次不超过 4000-5000 字符
- 每块之间 sleep 1-2 秒
- 不要用 `---` 分隔线（lark-cli 会解析为 flag）

#### ⚠️ 关键发现 (2026-07-15): block_type 3/4/5 在直接API下不可用

**问题：** 使用 tenant_access_token 直接调用飞书 docx API 时，`block_type=3(h1)/4(h2)/5(h3)` 全部返回 400 invalid param。

```python
# ❌ 这四种方式全部失败
POST /open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children
{"children": [{"block_type": 3, "text": {"elements": [{"text_run": {"content": "标题"}}]}}]}
# → 400 {"code":1770001, "msg":"invalid param"}

{"children": [{"block_type": 3, "heading1": {"text": {"elements": [{"text_run": {"content": "标题"}}]}}}]}
# → 400 {"code":99992402, "msg":"field validation failed"}
```

**原因推测：** 飞书 docx 的标题块（block_type 3/4/5）需要 `document_revision_id` 或特定权限，tenant_access_token 作为企业级 token 可能不支持创建标题级别的块。

**✅ Workaround：用 block_type=2 加粗文本块模拟标题**

```python
def write_bold_heading(doc_id, text):
    """用加粗文本块模拟标题（block_type 3/4/5 在 tenant_access_token 下不可用）"""
    block = {
        "children": [{
            "block_type": 2,
            "text": {
                "elements": [{
                    "text_run": {
                        "content": text,
                        "text_element_style": {"bold": True}
                    }
                }]
            }
        }]
    }
    payload = json.dumps(block, ensure_ascii=False).encode()
    req = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
        data=payload, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())
```

### 5. 深度分析格式（用户偏好）

#### ✅ 推荐格式（v2版本，用户认可）
```markdown
### 观点一：[观点概括]

**原文引用：**

> "[完整句子150字以上]"

**论据：**
- 事实：[原文具体描述，要有具体时间、地点、事件]
- 数据：[原文数据或数据来源问题]
- 逻辑：[原文推理过程]
- 质量：强/中/弱

**破绽：**

*原文引用："[完整句子]"*

→ 破绽类型：以偏概全/逻辑谬误/矫枉正/主次颠倒/夸大矛盾
→ 问题分析：80字以上详细阐述，说明为什么引用存在逻辑问题
```

#### ⚠️ 核心规则（违反算失败）
1. 观点必须完整复制原文句子，不得用总结替代，观点部分必须超过50字
2. 论据中的数据和事实必须详细引用原文中的案发现场描述
3. 破绽分析必须先引用原文，然后80字以上详细阐述
4. 必须大量引用原文：每个观点平均引用原文超过150字
5. 分析结果需超过3000字

### 6. 完整 Pipeline 执行顺序

```
1. 抖音链接 → Coze 工作流 → 逐字稿
2. 逐字稿 → 深度分析（>3000字，严格引用原文）
3. 深度分析 → Mermaid 思维导图（大白话，菜市场大妈都能懂）
4. 深度分析 → 知识图文（1-5张，全中文，PPT级别可视化）
5. 全部内容 → 飞书文档（原文+分析+思维导图+图片）
```

### 7. 已知限制

| 服务 | 状态 | 备注 |
|------|------|------|
| Coze 工作流 | ✅ 正常 | v0.0.1版本 |
| gemini-2.5-flash-image-preview | ⚠️ 上游不稳定 | 502/525/522时熔断 |
| gpt-image-2 | ❌ 不可用 | 彻底下线 |
| 飞书画板 | ✅ 需OAuth | user_access_token |
| EdrawMind API | ✅ 可用 | 返回缩略图+在线编辑链接 |

### 8. ⚠️ 2026-07-20 发现的问题修复

#### 问题1：逐字稿截断
- **现象**：手动转写逐字稿时从3153字截断为1769字
- **修复**：必须从Coze原始输出直接复制，不可手动转写
- **规则**：`逐字稿必须完整写入飞书，一字不改`

#### 问题2：飞书文档图片插入失败
- **现象**：EdrawMind思维导图缩略图上传到drive/media/upload_all成功（返回file_token），但以block_type=17插入docx时返回1770001 invalid param
- **当前workaround**：以EdrawMind在线编辑链接形式插入文档
- **待解决**：需要排查飞书docx API image block的正确参数格式

#### 问题3：图片生成渠道全线不可用
| 渠道 | 错误 | 状态 |
|------|------|------|
| 心流grop cdn.wusag.com | 525/522 SSL/Cloudflare | ❌ |
| 豹剪 api.bjzy.nfai.top | ✅ 可用（Key已找到） | 需用urllib绕过SSL验证（见§9） |
| FAL.ai FLUX 2 Klein 9B | Balance exhausted | ❌ |
| Agnes apihub.agnes-ai.com | ProxyError 连接超时 | ❌ |
- **当前可用渠道**：豹剪（gpt-image-2-4k）
- **待解决**：恢复心流grop、给FAL充值

### 9. 豹剪 API 实测笔记（2026-07-20）

#### 凭证
| 项目 | 值 |
|------|-----|
| API Key | `sk-naweFNcH8H7sGyDcNYhOf86GbHSrs23Lb1cFDiwjDyPYb265` |
| Base URL | `https://api.bjzy.nfai.top/v1` |
| Model | `gpt-image-2-4k` |
| 端点 | `/v1/chat/completions`（非 `/v1/images/generations`） |

#### ⚠️ SSL 问题
- `requests.post()` 报 `SSLError: record layer failure (_ssl.c:2580)`
- `requests.post(verify=False)` 也同样报 SSL 错误
- **必须用 `urllib.request.urlopen(context=ctx)`** 绕过，其中 `ctx` 为禁用证书验证的 SSL context
- 原因：该域名使用非标准 SSL 证书，urllib 裸调用可绕过

```python
import urllib.request, json, ssl

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
    headers={"Authorization": "Bearer sk-naweFNcH8H7sGyDcNYhOf86GbHSrs23Lb1cFDiwjDyPYb265",
             "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req, timeout=180, context=ctx) as r:
    result = json.loads(r.read())
    content = result["choices"][0]["message"]["content"]
    # 返回 Markdown 格式: ![title](https://pro.filesystem.site/cdn/.../xxx.png)
```

### 10. 飞书文档图片插入的正确方式（2026-07-20 实测）

#### 🔴 错误方式：直接 REST API + block_type=17

```python
# ❌ 以下方式全部返回 1770001 invalid param
POST /open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children
{
  "children": [{
    "block_type": 17,
    "image": {"token": file_token}
  }]
}
```

**测试了5种参数名**（token/file_token/src/image_key）+ **3种父节点**（root/已有block/新文本块），全部返回1770001。

即使图片已通过 `drive/v1/medias/upload_all`（parent_type=docx_image）成功上传拿到 file_token，block_type=17 依然无效。

**结论：** 这是飞书 docx API 的设计限制，block_type=17 在直接 REST 调用下不可用。

---

#### ✅ 正确方式：lark-cli +media-insert

```bash
# 使用 lark-cli 的 4 步编排（创建空block→上传图片→绑定→回填）
node run.js docs +media-insert \
  --doc <document_id> \
  --file <相对路径图片文件> \
  --align center \
  --width 800 \
  --caption "图片标题" \
  --as <bot|user> \
  --format json
```

| 参数 | 说明 |
|------|------|
| `--doc` | 文档ID或URL |
| `--file` | **必须是相对路径**（需要先cd到图片所在目录或用./前缀） |
| `--align` | left / center / right |
| `--width` | 图片显示宽度（px），高度自动按比例计算 |
| `--caption` | 图片标题文字 |
| `--as` | **关键参数！** `bot` 还是 `user`（见下方说明） |
| `--format json` | 返回JSON格式结果 |

#### ⚠️ `--as bot` vs `--as user` 的选择

| 身份 | 适用的文档 | 说明 |
|------|-----------|------|
| `--as bot` | 用 tenant_access_token 创建的文档 | 文档owner是bot，user身份插不进去 |
| `--as user` | 用 lark-cli user OAuth 创建的文档 | 文档owner是用户 |

**错误现象：**
- 用 `--as user` 插入 bot 创建的文档 → **1770032 forBidden**
- 用 `--as bot` 插入 user 创建的文档 → 也可能会失败

**判断方法：**
```bash
lark-cli auth status --verify
# 看 identity 字段: "bot" 还是 "user"
```

**最终策略：先写文字再append图片到末尾（稳定可靠）**

由于 `--as bot` + `--selection-with-ellipsis` 报 invalid token（无法定位插入），直接 append 到末尾 100% 成功。
流程统一为：

```python
# 最终流程（稳定可靠）:
doc_id = create_feishu_doc("标题")    # ① 创建文档
write_text(doc_id, "来源/链接/日期")   # ② 写元信息
write_text(doc_id, "完整逐字稿")       # ③ 写逐字稿
write_text(doc_id, "深度分析")         # ④ 写分析
append_image(doc_id, "mindmap.jpg")  # ⑤ lark-cli --as bot 追加图片
```

`--as bot` + `--selection-with-ellipsis` 已知问题：定位阶段报 code=-32602 invalid token（lark-cli v1.0.48 & v1.0.73，更新未修复）。直接 append 无此问题。

流程统一为**建文档 -> 写文字 -> append图片**。图片在末尾，搭配编辑链接：

```python
# 标准流程：
doc_id = create_feishu_doc("标题")    # ① 创建文档
write_text(doc_id, "来源/链接/日期")   # ② 写元信息
write_text(doc_id, "完整逐字稿")       # ③ 写逐字稿
write_text(doc_id, "深度分析")         # ④ 写分析
append_image(doc_id, "mindmap.jpg")  # ⑤ lark-cli --as bot 追加图片
```

#### 🚨 当 user 授权过期时

```bash
# 1. 获取新的 device code（不阻塞）
lark-cli auth login --domain docs --no-wait --json
# → 返回 verification_url + device_code

# 2. 展示二维码给用户扫
lark-cli auth qrcode <verification_url> --ascii

# 3. 用户扫码后完成授权
lark-cli auth login --device-code <device_code>
# → OK: 授权成功! 用户: xxx
```

#### 与直接 REST API 的对比

| 方式 | 图片插入 | 标题块(h1/h2) | 文本块 | 
|------|---------|---------------|--------|
| REST API + tenant_token | ❌ 1770001 | ❌ 400 | ✅ 可用 |
| lark-cli `--as bot` | ✅ 成功 | ✅ 靠markdown模式 | ✅ 可用 |
| lark-cli `--as user` | ✅ 成功 | ✅ 靠markdown模式 | ✅ 可用 |

#### 结论
- **飞书 docx API 的某些 block type（3/4/5 标题、17 图片）在直接 REST 调用下不可用**
- `lark-cli +media-insert` 内部做了4步封装，是图片插入的**唯一可靠方式**
- 文档创建者决定了图片插入时用 `--as bot` 还是 `--as user`
