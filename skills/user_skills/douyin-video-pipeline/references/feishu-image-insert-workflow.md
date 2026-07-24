# 飞书文档图片插入完整工作流

## 背景

飞书 docx API 的 `block_type=17`（图片块）在直接 REST 调用下所有参数格式都返回 `1770001 invalid param`。必须使用 `lark-cli docs +media-insert` 命令。

## 核心命令

```bash
# ✅ 方式A：追加到文档末尾（bot 身份，始终可用，推荐）
lark-cli docs +media-insert \
  --doc <document_id> \
  --file <相对路径图片> \
  --align center \
  --width 800 \
  --caption "图片标题" \
  --as bot \
  --format json

# ✅ 方式B：追加到文档末尾（user 身份）
lark-cli docs +media-insert \
  --doc <document_id> \
  --file <相对路径图片> \
  --align center \
  --width 800 \
  --as user \
  --format json

# ⚠️ 方式C：插入到指定位置前（仅 user 身份可用）
# bot 身份不支持 --selection-with-ellipsis（code -32602 invalid token）
lark-cli docs +media-insert \
  --doc <document_id> \
  --file <相对路径图片> \
  --align center \
  --width 800 \
  --selection-with-ellipsis "来源：" \
  --before \
  --as user \
  --format json
```

## 关键参数

| 参数 | 说明 | 必需 |
|------|------|:----:|
| `--doc` | 文档 ID 或 URL | ✅ |
| `--file` | **相对路径**（绝对路径报 `unsafe file path`） | ✅ |
| `--as` | `bot` 或 `user`。文档是bot创建则用bot | ✅ |
| `--align` | `left` / `center` / `right` | ❌ |
| `--width` | 显示宽度（px），高度自动按比例 | ❌ |
| `--caption` | 图片标题文字 | ❌ |
| `--selection-with-ellipsis` | 🔴 **仅 user 身份可用**。bot身份报invalid token | ❌ |
| `--before` | 在匹配文本前插入 | ❌ |

## 身份选择（重要）

| 场景 | `--as` | 说明 |
|------|--------|------|
| 文档用 tenant_access_token 创建 | `bot` | ✅ bot追加末尾可用；❌ selection-with-ellipsis不可用 |
| 文档用 user OAuth 创建 | `user` | 需要扫码授权，但定位功能可用 |

## 最终策略：先写文字，后append图片（简单可靠）

**结论：** `--as bot` + `--selection-with-ellipsis` 报 invalid token（无法定位插入），所以不做定位插入。
流程统一为：**建文档 -> REST API写文字 -> lark-cli --as bot append图片**。图片在文档末尾，搭配编辑链接一起用。

## 删除多余的 block

```bash
# 方式1：delete_range（推荐）
lark-cli docs +update \
  --doc <doc_id> \
  --mode delete_range \
  --selection-with-ellipsis "要删除的文字" \
  --as bot

# 方式2：replace_range（当 delete_range 匹配失败时）
lark-cli docs +update \
  --doc <doc_id> \
  --mode replace_range \
  --selection-with-ellipsis "要替换的文字" \
  --markdown " " \
  --as bot
```

**注意：** `delete_range` 对包含 `://`、`.` 等特殊字符的文本可能匹配失败。此时用 `replace_range` + `--markdown " "` 替代。

## Python 完整示例

```python
import subprocess, json, shutil, os, requests

DOC_ID = "KnKFdjrDDocFr5xxbUwcvrKencd"
RUN_JS = r"C:/Users/Admin/AppData/Roaming/npm/node_modules/@larksuite/cli/scripts/run.js"
WORK_DIR = "C:/Users/Admin"

def feishu_insert_image_append(doc_id, local_path, caption=""):
    """插入图片到飞书文档（追加到末尾）
    
    ✅ bot身份可用，稳定可靠。
    图片在文档末尾，如果想让图片在顶部，应在创建文档后立即调用此函数。
    """
    filename = os.path.basename(local_path)
    shutil.copy2(local_path, os.path.join(WORK_DIR, filename))
    
    cmd = ["node", RUN_JS, "docs", "+media-insert",
           "--doc", doc_id,
           "--file", filename,
           "--align", "center",
           "--width", "800",
           "--as", "bot",
           "--format", "json"]
    if caption:
        cmd += ["--caption", caption]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=WORK_DIR)
    os.remove(os.path.join(WORK_DIR, filename))
    
    resp = json.loads(result.stdout) if result.stdout else json.loads(result.stderr)
    return resp.get("ok", False), resp.get("data", {})

def feishu_insert_link(doc_id, label, url, bold=True):
    """插入带超链接的文本块"""
    token = _get_tenant_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {"children": [{
        "block_type": 2,
        "text": {
            "elements": [
                {"text_run": {"content": label, "text_element_style": {"bold": bold}}},
                {"text_run": {"content": url, "text_element_style": {"link": {"url": url}}}}
            ]
        }
    }]}
    r = requests.post(
        f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
        headers=headers, json=body, timeout=15)
    return r.json().get("code") == 0

def _get_tenant_token():
    APP_ID = "cli_aa92b1fa06395cb0"
    APP_SECRET = "***FEISHU_SECRET***"
    r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=10)
    return r.json()["tenant_access_token"]

# 标准流程示例
ok, data = feishu_insert_image_append(
    DOC_ID, "C:/Users/Admin/Desktop/image.png",
    caption="图片标题"
)
if ok:
    print(f"✅ 插入成功! block_id={data['block_id']}")

feishu_insert_link(DOC_ID, "思维导图在线编辑：", "https://mm.edrawsoft.cn/app/editor/xxx")
```

## 已知问题

| 问题 | 现象 | 方案 |
|------|------|------|
| block_type=17 REST API | 全部返回 1770001 | 只能用 lark-cli |
| `--as user` 插 bot 文档 | 1770032 forBidden | 改用 `--as bot` |
| `--file` 绝对路径 | unsafe file path | 复制到 cwd 用相对路径 |
| `delete_range` 匹配URL | 特殊字符匹配失败 | 改用 `replace_range` + `--markdown " "` |

### 🐛 `--selection-with-ellipsis` + bot 身份 = invalid token

**现象：** 用 `--as bot` + `--selection-with-ellipsis "文本"` 时，在 "Locating block matching selection" 阶段返回 `code=-32602, message="invalid token"`。但**去掉 `--selection-with-ellipsis` 直接 append 到末尾就成功**。

**触发条件：**
- `--as bot` 参数
- `--selection-with-ellipsis` 定位文本
- bot 身份虽然 auth status 显示 ready，但定位阶段的 API 调用会报 invalid token
- 该问题在 lark-cli v1.0.48 和 v1.0.73 都存在（更新未修复）

**根因推测：** lark-cli bot 身份加载文档内容做文本定位时，走了一条不同的内部认证通道，该通道的 token 格式不被接受。append 末尾模式直接创建 block，不走定位通道，所以成功。

**解法：**
1. ✅ **标准流程：** 建文档 -> 写文字 -> append图片到末尾。图片在末尾但搭配编辑链接，用户翻到就看得到。
2. ⚠️ **workaround：** 用 marker 辅助定位——先用 REST API 插入唯一标记文本（如 `ZZ_IMAGE_MARKER_ZZ`），再用 `--as bot` append 图片（不带selection），然后手动删除标记。
3. ❌ `--as user` 配 selection-with-ellipsis 可用定位，但 user 插 bot 文档会 1770032 forBidden。
