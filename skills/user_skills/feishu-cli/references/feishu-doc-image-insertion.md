# Feishu Document Image Insertion — Complete API Flow

Three-step process using `tenant_access_token` (no OAuth needed):

1. **Upload** → `POST /drive/v1/medias/upload_all` → get `file_token`
2. **Create block** → `POST /docx/v1/documents/{doc_id}/blocks/{doc_id}/children` → create image block (block_type=27, **without** token)
3. **Bind token** → `PATCH /docx/v1/documents/{doc_id}/blocks/{new_block_id}` → attach the `file_token`

## Complete Python Example

```python
import json
import requests

APP_ID = "cli_xxxxxxxxxxxxxxxxxxxx"
APP_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
DOC_ID = "KnKFdjrDDDocFr5xxbUwcvrKencd"

# ── Step 0: Get tenant_access_token ──────────────────────────
r = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET},
    timeout=15,
)
token = r.json()["tenant_access_token"]
headers = {"Authorization": f"Bearer {token}"}

# ── Step 1: Upload image to drive ────────────────────────────
with open("mindmap.png", "rb") as f:
    img_bytes = f.read()

files = {
    "file_name": (None, "mindmap.png"),
    "parent_type": (None, "docx_image"),
    "parent_node": (None, ""),
    "size": (None, str(len(img_bytes))),
    "file": ("mindmap.png", img_bytes, "image/png"),
}
r = requests.post(
    "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all",
    headers=headers,
    files=files,
    timeout=120,
)
file_token = r.json()["data"]["file_token"]
print(f"file_token: {file_token}")

# ── Step 2: Create image block (NO token in body) ────────────
r = requests.post(
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{DOC_ID}/blocks/{DOC_ID}/children",
    headers={**headers, "Content-Type": "application/json"},
    json={
        "children": [{
            "block_type": 27,
            "image": {"width": 0, "height": 0}   # width/height required, token NOT here
        }]
    },
    timeout=15,
)
new_block_id = r.json()["data"]["children"][0]["block_id"]
print(f"new_block_id: {new_block_id}")

# ── Step 3: Bind file_token via PATCH ────────────────────────
r = requests.patch(
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{DOC_ID}/blocks/{new_block_id}",
    headers={**headers, "Content-Type": "application/json"},
    json={"replace_image": {"token": file_token}},
    timeout=15,
)
print(f"Patch result: {r.json()}")
```

## Key Points

| Aspect | Detail |
|--------|--------|
| `block_type` | **27** for image blocks |
| Step 2 body | `image` field MUST have `width`/`height`, MUST **NOT** have `token` |
| Step 3 endpoint | `PATCH …/blocks/{new_block_id}` (not the document root) |
| Step 3 body | `{"replace_image": {"token": "…"}}` |
| Media upload | `parent_type: "docx_image"` + `parent_node: ""` (empty string) |
| Token type | `tenant_access_token` works for document image insertion |
| Failure mode | If tenant token lacks permission, fall back to manual paste |

## Common Errors

| Error | Likely Cause |
|-------|-------------|
| `InvalidBlockType` | Wrong `block_type` value (use 27) |
| `PermissionDenied` | Token lacks docx write scope or doc is not in this tenant |
| Image not showing | Step 3 PATCH was skipped or wrong `block_id` was used |
| `TextFieldConvFail` | Wrong field format in insert body (irrelevant here) |