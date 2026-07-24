---
name: feishu-cli
description: >
  当用户需要操作飞书文档/表格/Base/消息时使用。
  支持：OAuth登录、文档操作、表格操作、多维表格操作、消息推送。
  不要用于：飞书多维表格附件处理（走feishu-workflow）、非飞书平台的操作。
  触发词：飞书CLI、lark-cli、飞书文档、操作飞书、飞书API
triggers:
  - lark-cli
  - feishu-cli
  - 飞书 CLI
  - 飞书登录
  - Feishu API
  - Lark API
tags: [feishu, lark, oauth, cli, windows]
version: 1
---

# Feishu CLI (lark-cli)

## Overview

`lark-cli` (npm package `@larksuite/cli`) is the official Feishu/Lark CLI. It supports **Bot mode** (robot identity, limited scope) and **User mode** (impersonates the user, full access). On this machine both `lark-cli` and `feishu` commands are installed under `C:\Users\Admin\AppData\Roaming\npm\`.

This skill covers: verifying installation, binding to Hermes workspace, User-mode OAuth authentication, and the `.cmd` wrapper workaround on Windows.

---

## Verification & Health Check

```bash
# Via node directly (avoids .cmd wrapper issues — see Windows workaround below)
node C:/Users/Admin/AppData/Roaming/npm/node_modules/@larksuite/cli/scripts/run.js --version

# Or use the .cmd wrapper (may have issues with special characters in args)
lark-cli --version
lark-cli doctor

# Check auth status
node C:/Users/Admin/AppData/Roaming/npm/node_modules/@larksuite/cli/scripts/run.js auth list
```

The `doctor` command checks: CLI version, update availability, and whether the CLI is bound to the current workspace (Hermes).

---

## Windows `.cmd` Wrapper Bug — ALWAYS Use Node Directly

The npm-generated `.cmd` files (`lark-cli.cmd`, `feishu.cmd`) on Windows do NOT properly pass URL arguments containing `&` or `?` characters to the underlying Node.js script. This causes **silent failures** when running commands like `auth qrcode <verification_url>` or any command with OAuth/device-code URLs.

**Always invoke the Node script directly:**

```python
import subprocess, os

npm_dir = r"C:\Users\Admin\AppData\Roaming\npm"
run_js = os.path.join(npm_dir, "node_modules", "@larksuite", "cli", "scripts", "run.js")
env = os.environ.copy()
env["HERMES_HOME"] = r"C:\Users\Admin\AppData\Local\hermes"

# CORRECT — invoke via node directly
result = subprocess.run(
    ['node', run_js, 'auth', 'qrcode', verification_url, '-o', 'feishu_auth.png'],
    cwd=working_dir,
    env=env,
    capture_output=True,
    text=True,
    timeout=15
)
```

Set `HERMES_HOME=C:\Users\Admin\AppData\Local\hermes` in the subprocess env so lark-cli can find Hermes credentials.

---

## User-Mode OAuth Authentication Flow

User mode allows full impersonation of the user — the AI can read/write their personal Feishu data (messages, calendar, docs, contacts, etc.).

### Step 1 — Bind to Hermes Workspace (One-time)

```bash
lark-cli config bind --source hermes --identity user-default
```

⚠️ Only run this after **explicit user confirmation** — it enables the AI to act as the user.

**Note:** The `--workspace` flag does NOT exist on `config bind`. Workspace binding is implicit based on `HERMES_HOME` env var. The CLI automatically uses `~/.lark-cli/{workspace_name}/config.json`.

After binding, verify with `lark-cli doctor` — you should see:
```json
{"ok": true, "checks": [...{"name": "identity_ready", "status": "pass", "message": "at least one identity is available"}]}
```

The CLI reports the app ID after binding (e.g. `cli_aa92b1fa06395cb0`). The auth config is stored at `C:\Users\Admin\.lark-cli\hermes\config.json`.

### Step 2 — Initiate Device Authorization (non-blocking)

```python
import subprocess, os, json

run_js = r"C:\Users\Admin\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js"
env = os.environ.copy()
env["HERMES_HOME"] = r"C:\Users\Admin\AppData\Local\hermes"

result = subprocess.run(
    ['node', run_js, 'auth', 'login', '--recommend', '--no-wait', '--json'],
    env=env, capture_output=True, text=True, timeout=15
)
data = json.loads(result.stdout)
# Save for later:
#   data['verification_url']   — to generate QR code
#   data['device_code']        — to complete after user authorizes
```

### Step 3 — Generate QR Code (PNG) for the User to Scan

```python
result = subprocess.run(
    ['node', run_js, 'auth', 'qrcode', verification_url, '-o', 'feishu_auth.png'],
    cwd=output_dir,  # Must be the SAME directory the output file will be written to (relative path)
    env=env, capture_output=True, text=True, timeout=15
)
# Output: {"file_path": "...", "ok": true}
```

**Display the QR code to the user:**

```markdown
![飞书授权二维码](<C:/Users/Admin/AppData/Local/hermes/feishu_auth.png>)
```

Include instructions: open Feishu → + → 扫一扫 → scan → confirm on phone.

**If QR code fails** (file not generated), fall back to displaying the `verification_url` as a clickable link, and ask the user to visit and enter the user code manually.

### Step 4 — Complete After User Authorizes

```python
result = subprocess.run(
    ['node', run_js, 'auth', 'login', '--recommend', '--device-code', device_code],
    env=env, capture_output=True, text=True, timeout=60
)
# Blocks ~10-20s waiting for user to complete on their phone
# On success: stdout shows user info and available scopes
```

---

## Bot-Mode (Quick Alternative)

If User mode is not needed (e.g. only sending messages as a bot), bind as bot-only instead:

```bash
lark-cli config bind --source hermes --identity bot-only
# Then:
lark-cli auth login --recommend --no-wait --json
# (follow same QR flow as above)
```

---

## Common API Operations

```bash
# Calendar — list events
lark-cli calendar events instance_view \
  --params '{"calendar_id":"primary","start_time":"1700000000","end_time":"1700086400"}'

# Contacts — search users
lark-cli contact +search-user --query "John"

# Generic API call
lark-cli api GET /open-apis/calendar/v4/calendars

# View API schema
lark-cli schema calendar.events.instance_view --format pretty
```

### Bitable（多维表格）操作

飞书多维表格（Bitable）的命令使用 `base` 子命令，与通用 API 调用不同，参数全部通过 flags 传递。

#### 读取记录（`+record-list`）

```python
import subprocess, os, json

run_js = r"C:\Users\Admin\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js"
env = os.environ.copy()
env["HERMES_HOME"] = r"C:\Users\Admin\AppData\Local\hermes"

# 用 --base-token 和 --table-id 传参，不接受位置参数
result = subprocess.run(
    ['node', run_js, 'base', '+record-list',
     '--base-token', app_token,     # 多维表格的 app_token（如 HeYWbu1Ppa2MEWs9AjJc09WJnce）
     '--table-id', table_id,         # 表格 ID（以 tbl 开头，如 tblEsoWpihj5JwM3）
     '--limit', '10',
     '--format', 'json'],
    cwd=r'D:\hermes-data', env=env, capture_output=True, text=True, timeout=30
)
data = json.loads(result.stdout)
# 字段顺序按 fields 数组返回，无 keys；用 field_id_list / fields 配合定位
```

#### 下载附件（`+record-download-attachment`）

这是**唯一能下载多维表格附件**的 lark-cli 命令，其他 drive 下载命令会返回 403。

```python
# 下载单个附件
result = subprocess.run(
    ['node', run_js, 'base', '+record-download-attachment',
     '--base-token', app_token,
     '--table-id', table_id,
     '--record-id', record_id,       # 从 +record-list 获取
     '--file-token', file_token,      # 附件的 file_token（从记录字段获取）
     '--output', 'attachments/filename.jpg',  # 必须是从 cwd 出发的相对路径
     '--format', 'json'],
    cwd=r'D:\hermes-data', env=env, capture_output=True, text=True, timeout=60
)

# 下载记录所有附件（省略 --file-token）
result = subprocess.run(
    ['node', run_js, 'base', '+record-download-attachment',
     '--base-token', app_token, '--table-id', table_id,
     '--record-id', record_id, '--output', 'attachments/',
     '--format', 'json'],
    cwd=r'D:\hermes-data', env=env, capture_output=True, text=True, timeout=120
)
```

#### 创建分享链接（`+record-share-link-create`）

当需要生成可分享的临时链接时使用（附件 API 本身不返回 tmp_url）。

```python
result = subprocess.run(
    ['node', run_js, 'base', '+record-share-link-create',
     '--base-token', app_token, '--table-id', table_id,
     '--record-id', record_id, '--format', 'json'],
    cwd=r'D:\hermes-data', env=env, capture_output=True, text=True, timeout=15
)
```

---

## 关键发现：附件下载与 URL 边界

| 需求 | 结论 | 说明 |
|------|------|------|
| 通过 file_token 获取 tmp_url | ✅ `tenant_access_token` + GET `/batch_get_tmp_download_url` | 见 `references/bitable-attachment-urls.md` |
| `lark-cli drive +download` 下载 bitable 附件 | ❌ 403 | Bot 权限无法访问多维表格附件文件 |
| `api GET /im/v1/files/{token}` | ❌ user token 不支持 | 该接口仅接受 Bot token |
| **`+record-download-attachment`** | ✅ 成功 | User 身份可完整下载附件到本地（`D:\hermes-data\attachments\`） |
| 飞书内置「创建分享链接」 | ✅ 可用 | 生成应用内可访问的临时链接 |

**两种可用方案：**
1. **直接 URL 方案**（推荐）：用 `scripts/get_bitable_urls.py` 通过 `tenant_access_token` 批量获取 tmp_download_url，输出 JSON 格式（`{"图片":[],"音频":[],"视频":[], "_all_urls":{}}`），URL 直接传给下游工具
2. **本地下载方案**：`lark-cli +record-download-attachment` 下载到 `D:\hermes-data\attachments\`，再把本地路径提供给 libtv 等工具

---

## Key Files & Paths

| Purpose | Path |
|---------|------|
| lark-cli entry | `C:\Users\Admin\AppData\Roaming\npm\lark-cli.cmd` |
| run.js (use directly on Windows) | `C:\Users\Admin\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js` |
| Hermes workspace home | `C:\Users\Admin\AppData\Local\hermes` |
| Auth config (per workspace) | `C:\Users\Admin\.lark-cli\hermes\config.json` |

---

### Direct HTTP API (Simpler than lark-cli for Bitable)

For programmatic bitable operations, **direct Feishu Open API via `tenant_access_token`** is simpler and more reliable than lark-cli — especially for automation scripts. The user's app (`cli_a851f4d520a8900b`) already has the `bitable:app` scope.

```python
import urllib.request, json

APP_ID     = "cli_a851f4d520a8900b"
APP_SECRET = "***"

# Step 1: Get tenant_access_token
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req, timeout=15) as resp:
    token = json.loads(resp.read())["tenant_access_token"]

# Step 2: Create a new bitable
req2 = urllib.request.Request(
    "https://open.feishu.cn/open-apis/bitable/v1/apps",
    data=json.dumps({"name": "巨量百应爆款视频 2026-07-08"}).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST"
)
with urllib.request.urlopen(req2, timeout=15) as resp:
    result = json.loads(resp.read())
# result["data"]["app"]["app_token"]  → new app token
# result["data"]["app"]["default_table_id"]  → first table ID

# Step 3: Add fields (type=1 for text, type=3 for single-select, type=17 for attachment, etc.)
for field_name, field_type in [("博主名称", 1), ("视频时长", 1)]:
    req3 = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
        data=json.dumps({"field_name": field_name, "type": field_type}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST"
    )
    with urllib.request.urlopen(req3, timeout=15) as resp:
        json.loads(resp.read())

# Step 4: Batch insert records — fields value is just the field_name→string mapping
records = [{"fields": {"博主名称": "笑笑麻麻", "视频时长": "1分24秒"}}]
req4 = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
    data=json.dumps({"records": records}).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST"
)
with urllib.request.urlopen(req4, timeout=15) as resp:
    result = json.loads(resp.read())  # code=0 means success

# Step 5: Delete records (batch_delete)
req5 = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
    headers={"Authorization": f"Bearer {token}"},
    method="DELETE"
)
with urllib.request.urlopen(req5, timeout=10) as resp:
    json.loads(resp.read())  # code=0 means success
```

**Key rules for text fields:**
- **Do NOT** wrap values as `{"type": "text", "text": "..."}` — this causes `TextFieldConvFail` (code 1254060)
- **Just pass strings directly**: `{"fields": {"博主名称": "笑笑麻麻", ...}}`
- Date fields (type=5) require epoch milliseconds
- For URL fields (type=15): `{"link": "https://...", "text": "显示文字"}`
- For multi-line text, just pass the string — no special wrapping needed

### Key Feishu Bitable Field Types

| type | Field | Python value |
|------|-------|-------------|
| 1 | 文本 | `"string"` 直接字符串 |
| 2 | 数字 | `{"value": 12345, "operator": "+"}` |
| 3 | 单选 | `"选项名"` |
| 4 | 多选 | `["选项1", "选项2"]` |
| 5 | 日期 | `1700000000000` (epoch ms) |
| 7 | 复选框 | `true` / `false` |
| 11 | 创建人 | 自动，无需填 |
| 13 | 更新时间 | 自动，无需填 |
| 15 | URL | `{"link": "url", "text": "显示名"}` |
| 17 | 附件 | 需通过 get_bitable_urls.py 获取 file_token |
| 18 | 关联 | `{"record_ids": [...]}` |
| 19 | 公式 | 自动计算，无需填 |

## Pitfalls

1. **`.cmd` wrapper strips `&` in URLs** — always invoke via `node run.js` on Windows.
2. **`lark-cli auth login` blocks** without `--no-wait` — use `--no-wait --json` for programmatic flows.
3. **`--no-wait` creates a fresh device code** — do NOT reuse codes from previous calls; each invocation is independent.
4. **QR code `-o` requires relative path** from `cwd` — absolute paths are rejected, output appears in `cwd`.
5. **User-mode is irreversible without re-bind** — switching from bot-only to user-default requires `--force` flag or re-bind.
6. **`+record-list` positional args rejected** — `--base-token` and `--table-id` are required flags, no positional app_token.
7. **All `--output` paths must be relative to `cwd`** — absolute paths are rejected; set `cwd=` to the base dir and use `'attachments/filename.jpg'`.
8. **Text field values must be plain strings** — `{"type":"text","text":"..."}` wrapper causes `TextFieldConvFail` (code 1254060). Pass `{"field_name": "value"}` directly as strings. Date fields need epoch ms, URL fields need `{"link": "...", "text": "..."}`.
9. **batch_create with `fields` key in each record** — JSON body is `{"records": [{"fields": {...}}, {"fields": {...}}]}`. Each record needs its own `fields` dict — the outer record key must be `"fields"`, not something else.
10. **Use app token from creation response, not hardcoded** — each newly created bitable has a unique `app_token`. After creation, read it from `result["data"]["app"]["app_token"]` and `result["data"]["app"]["default_table_id"]`.
11. **`lark-cli docs +update` 和 `+fetch` 强制使用 user identity** — 即使是读取操作也返回 `need_user_authorization`。token 过期后整个命令失败（exit code 3）。**建议：文档读写改用直接 Feishu Open API + tenant_access_token**，无需 OAuth 扫码，更加稳定可靠。
12. **lark-cli 没有 `docs export` 子命令** — 可用命令只有 `+create`, `+fetch`, `+media-download`, `+media-insert`, `+media-preview`, `+media-upload`, `+search`, `+update`, `+whiteboard-update`。导出 Word 文档需用 python-docx 直接生成。
13. **飞书白board API 必须用 user_access_token** — 文档/docx 是企业资源可用 tenant token，但 board/白板是用户个人资源，必须 OAuth 扫码获取 user token。
14. **飞书文档插入图片的正确流程（tenant token 可用）** — 见 `references/feishu-doc-image-insertion.md` 含完整 Python 代码示例和常见错误排查。注意：tenant token 可上传文件但操作用户文档的图片 block 可能受限，此时**让用户手动复制粘贴图片到文档是最快方案**
15. **lark-cli `+media-upload` vs `+media-insert` 的参数差异** —
    - `+media-upload`: 用 `--doc-id`（不是 `--doc`），需要同时传 `--parent-node` 和 `--parent-type`
    - `+media-insert`: 用 `--doc`（不是 `--doc-id`），只需指定文档和文件路径
16. **飞书文档创建建议用 tenant token** — 用 lark-cli 创建文档时 owner 是 user，后续无法用 tenant token 写入内容。**正确做法：用 Feishu Open API `POST /docx/v1/documents` 创建（tenant token），然后用同一 API 写入 blocks**。
17. **mermaid.ink vs kroki.io** — kroki.io 全部 404，**mermaid.ink 在线渲染可用**，URL 格式 `https://mermaid.ink/img/{base64(mermaid_code)}`。本地渲染推荐 npm install -g @mermaid-js/mermaid-cli，入口是 `C:\\Users\\Admin\\AppData\\Roaming\\npm\\mmdc.cmd`。
18. **`--as bot` + `--selection-with-ellipsis` = invalid token（lark-cli v1.0.48 & v1.0.73 均已测试，更新未修复）** — 用 bot 身份 + 文本定位插入图片时，在"Locating block matching selection"阶段返回 `code=-32602, message="invalid token"`。去掉 `--selection-with-ellipsis` 直接 append 到末尾则 100% 成功。
    - **根因：** bot 身份做文本定位时走了不同的内部认证通道，append 模式不走定位通道所以成功。
    - **解法：** 统一用 append 模式。图片放末尾，搭配编辑链接用。
    - **如果必须定位：** 先用 REST API 插入唯一标记文本（如 `ZZ_IMAGE_MARKER_ZZ`），再 `--as bot` append 图片（不带selection），然后手动删除标记。或者用 `--as user` + selection-with-ellipsis（但 user 插 bot 创建的文档会 1770032 forBidden）。
    - **完整工作流：** 参考 `content/douyin-video-pipeline` 技能的 `references/feishu-image-insert-workflow.md`
18. **Mermaid CLI 本地调用**（Windows）：
    ```python
    mmdc_path = r"C:\Users\Admin\AppData\Roaming\npm\mmdc.cmd"
    result = subprocess.run(
        [mmdc_path, "-i", "input.mmd", "-o", "output.png", "-b", "white", "-w", "1920", "-H", "1080"],
        capture_output=True, timeout=60
    )
    ```

---

## References

- Official docs: https://open.feishu.cn/document/
- GitHub: https://github.com/larksuite/cli
- Available skills for AI agents: `npx skills add larksuite/cli -g -y`
- `references/bitable-attachment-urls.md` — 多维表格附件批量获取 tmp_download_url 的完整方案（含 tenant_access_token 认证流程、JSON 输出格式说明）
- `references/feishu-doc-image-insertion.md` — 飞书文档插入图片的完整 3 步 API 流程（upload → create block → PATCH bind），含完整 Python 代码示例和常见错误排查
- `scripts/get_bitable_urls.py` — 封装脚本：输入 app_id/app_secret/app_token/table_id，输出 `{"图片": [], "音频": [], "视频": [], "_all_urls": {}}`