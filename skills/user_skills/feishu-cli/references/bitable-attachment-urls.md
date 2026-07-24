# 多维表格附件 tmp_download_url 批量获取方案

## 问题背景

飞书多维表格（Bitable）附件字段（type=17）只返回：
```json
{"file_token": "xxx", "name": "文件名.jpg", "size": 12345}
```
不包含可访问的 URL。需要通过飞书 Drive API 换取临时下载链接（tmp_download_url）。

## 已知方案对比

| 方案 | 结果 | 说明 |
|------|------|------|
| `lark-cli +record-download-attachment` | ✅ 成功 | User 身份下载到本地，无 URL 输出 |
| `lark-cli drive +download` | ❌ 403 | Bot 权限无法访问 bitable 附件 |
| `api GET /im/v1/files/{token}` | ❌ user token 不支持 | 仅接受 Bot token |
| `lark-cli api GET .../batch_get_tmp_download_url` (POST) | ❌ 404 | 该端点仅支持 GET |
| **`tenant_access_token` + GET `/batch_get_tmp_download_url`** | ✅ **成功** | 正确方式 |

## 正确方案：tenant_access_token + GET batch_get_tmp_download_url

### Step 1 — 获取 tenant_access_token

```python
import urllib.request, json

data = json.dumps({"app_id": "cli_xxx", "app_secret": "xxx"}).encode()
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=data, headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=15) as resp:
    result = json.loads(resp.read())
token = result["tenant_access_token"]
```

### Step 2 — 获取单条 tmp_download_url（逐个请求）

⚠️ **必须逐个请求**：批量传多个 file_token 会返回空数组。

```python
import urllib.request, urllib.parse

params = urllib.parse.urlencode({
    "file_tokens": file_token,       # 单个 token，不是逗号分隔
    "extra": '{"bitablePermission":"bitable_file_download_token"}'
})
url = f"https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url?{params}"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req, timeout=15) as resp:
    result = json.loads(resp.read())
tmp_url = result["data"]["tmp_download_urls"][0]["tmp_download_url"]
```

### 关键参数

- **`file_tokens`**：单个 file_token 字符串，**不要**逗号分隔多个（批量传会返回空）
- **`extra`**：`{"bitablePermission":"bitable_file_download_token"}` — **必须传**，否则多维表格附件返回空
- **必须用 GET**：POST 请求返回 404
- **频率限制**：每个请求间隔 ≥ 0.2 秒

## 输出 JSON 格式

```json
{
  "图片": ["文件名||tmp_url", ...],
  "音频": ["文件名||tmp_url", ...],
  "视频": ["文件名||tmp_url", ...],
  "_all_urls": {"文件名": "tmp_url", ...}
}
```

格式说明：
- `图片/音频/视频` 数组：每个元素为 `文件名||tmp_url`（双竖线分隔）
- `_all_urls`：扁平 dict，key=文件名，value=url，便于后续工具按名取用
- 分类逻辑：按扩展名（.jpg/.png→图片，.mp3→音频，.mp4→视频）

## 已知多维表格配置（来自 memory）

| 字段 | app_token | table_id | 附件字段 |
|------|-----------|----------|----------|
| LibTV 自动化 | HeYWbu1Ppa2MEWs9AjJc09WJnce | tblEsoWpihj5JwM3 | 图片(type=17)、音频(type=17)、视频(type=17) |

字段类型对照：序号(1005)、分镜描述(1)、图片(17)、音频(17)、视频(17)、提示词(1)、视频URL(15)、状态(3)

## 调用方式（后续业务触发）

用户提业务需求时，AI 根据意图判断：
1. 识别目标多维表格（从 memory 或字段特征判断）
2. 识别需要哪类附件（图片/音频/视频）
3. 调用 `get_bitable_urls.py` 获取 URL JSON
4. 将 URL 直接传给后续工具（libtv、image_generate 等）

**无需用户指定表格/字段**，AI 自主判断。