# 飞书白board API 实测笔记（2026-07-09，已验证通过）

## lark-cli 命令路径
```
node C:\Users\Admin\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js
```

## 创建画板（验证通过 ✅）
```bash
lark-cli docs +create \
  --title "标题" \
  --markdown '<whiteboard type="blank"></whiteboard>'
```
返回：`doc_id`, `board_tokens` (数组，取第一个), `doc_url`

⚠️ **注意**：`docs +create` 用的是 v1 API（已 deprecated），但仍可用。

## Mermaid 解析 API（验证通过 ✅）
```
POST /open-apis/board/v1/whiteboards/{board_token}/nodes/plantuml
Body: {"plant_uml_code": "<mermaid代码>", "syntax_type": 2, "diagram_type": 1}
```

### 权限要求（必须）
1. App 权限：`board:whiteboard:node:create`（飞书开放平台手动开通）
2. 鉴权方式：`user_access_token`（通过 lark-cli auth login 获取）

### 参数确认（实测通过）
| 参数 | 值 | 说明 |
|------|-----|------|
| `syntax_type` | 2 | Mermaid 语法 ✅ |
| `diagram_type` | 1 | 思维导图 ✅ |

### 完整流程（实测通过，code:0）
```bash
# Step 1: 创建文档+画板
lark-cli docs +create \
  --title "标题" \
  --markdown '<whiteboard type="blank"></whiteboard>' \
  --format json

# Step 2: 等待画板初始化（10-15秒）

# Step 3: 写入思维导图（用户身份！）
lark-cli api POST "/open-apis/board/v1/whiteboards/{board_token}/nodes/plantuml" \
  --data '{"plant_uml_code": "mindmap\n  root((主题))...", "syntax_type": 2, "diagram_type": 1}' \
  --as user --format json
```

### 错误码
| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `code=0` | 成功 | - |
| `2891001` | 未检测到图表类型 | 检查 mermaid 语法 |
| `99991672` | 缺少权限 | 开通 `board:whiteboard:node:create` |
| `99991679` | OAuth scope 不足 | 重新扫码授权 |
| `99991661` | token 缺失或过期 | 重新登录 |

## OAuth 鉴权（实测通过 ✅）

### 正确的 OAuth 流程（2步）

**Step 1: 获取 device_code + verification_url**
```bash
lark-cli auth login --recommend --no-wait --json
```
返回：`device_code`, `verification_url`, `user_code`

**Step 2: 打开 verification_url（不是 device_code 拼接的 URL！）**
```bash
# 后台等待扫码
lark-cli auth login --recommend --device-code <device_code>
```

### ⚠️ 关键发现
- ❌ 错误：`https://www.feishu.cn/suite/passport/oauth/verify?device_code=...`（404）
- ✅ 正确：使用 `data.verification_url`（包含 `accounts.feishu.cn/oauth/v1/device/verify`）
- Token 有效期 600 秒（10分钟）

## Mermaid 外部渲染服务（全部不可用）

| 服务 | 状态 | 问题 |
|------|------|------|
| Kroki.io | ❌ 404 | `https://kroki.io/mermaid/png/<b64>` 全部 404 |
| img.vim-cn.com | ❌ SSL | Windows Python 环境证书验证失败 |
| mermaid.ink | ❌ 404 | Not Found |

## 飞书 docx API Code Block 问题
`block_type=13` + `style.language` (任何值) → **始终 400 Bad Request**

### 替代方案
使用 `lark-cli docs +update --mode append --markdown` 写入：
- 普通文本（type=2）✅
- 标题（type=3/4/5）✅
- 列表（type=14/15）✅
- 图片（type=27，但 Drive URL 嵌入后可能 IMAGE_DOWNLOAD_FAILED）

## 图片上传到飞书（已验证 ✅）

### lark-cli drive +upload（推荐）
```bash
# 必须用相对路径（在 cwd 内）！绝对路径报错
lark-cli drive +upload --file <相对路径> --format json
```
返回：`file_name`, `file_token`, `url`

### lark-cli api POST /open-apis/im/v1/images
```bash
# 需要权限：im:resource:upload, im:resource
lark-cli api POST "/open-apis/im/v1/images" \
  --file "image=<相对路径>" \
  --as user --format json
```

### 图片嵌入文档问题
- Drive URL 嵌入 docx 时提示 `IMAGE_DOWNLOAD_FAILED`
- 原因：Drive 文件不在文档内
- 暂时无完美解决方案

## Coze 工作流输出解析（已验证 ✅）

### 关键坑
- 无 Interrupt 节点
- 逐字稿在 **Message 事件**（不是 Done）
- Done 事件只有 `debug_url`，不含 content

### 正确提取方式
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
        elif current_event == "Done":
            break  # Done 不含逐字稿，直接结束

full_content = "".join(all_content)
parsed = json.loads(full_content)
transcript = parsed.get("output", parsed.get("text", str(parsed))).strip()
```