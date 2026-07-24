---
name: apikey-image-gen
description: >
  当用户需要apikey-image-gen时使用。
  不要用于：无关场景。
  触发词：生成图片、AI生图、图片编辑、文生图
version: 1.2.0
author: Ekko
license: MIT
platforms: [linux, macos, windows, termux]
metadata:
  hermes:
    tags: [api.apikey.fun, custom-provider, image-generation, image-editing, media]
prerequisites:
  commands: [curl]
triggers:
  - 生成图片
  - AI生图
  - 图片编辑
  - 文生图

---

# APIKEY Image Generation

Use this skill when the user wants to generate an image, generate an image from a reference image, or edit an existing image.

## 用户偏好 (User Preference) — 2026-07-18 更新

**当前默认：豹剪 `api.bjzy.nfai.top` → `gpt-image-2-4k`**

| 优先级 | Provider | 模型 | 状态 |
|:------:|----------|------|:----:|
| 🥇 **首选** | **豹剪** (`api.bjzy.nfai.top`) | **gpt-image-2-4k** | ✅ 稳定，无安全拦截 |
| 🥈 备选 | 豹剪 | `doubao-seedream-4-0` | ✅ 可用（豆包模型） |
| 🥉 备选 | iliu.ai (心流) | `sora-v4-fast` (视频) | ✅ 视频生成可用 |
| ❌ 停用 | cdn.wusag.com (心流) | `gpt-image-2` | 502 服务器不可用 |

### 豹剪 API 详情

- **Base URL**: `https://api.bjzy.nfai.top/v1`
- **API Key**: `sk-naweFNcH8H7sGyDcNYhOf86GbHSrs23Lb1cFDiwjDyPYb265`
- **生图模型**: `gpt-image-2-4k`(4K ✅), `gpt-image-2-2k`, `gpt-image-2-1k`, `doubao-seedream-4-0`
- **视频模型**: 暂未验证 sora-2/veo（视频走 iliu.ai sora-v4-fast）
- **调用方式**: `POST /v1/chat/completions`（与心流格式相同））
- **197 模型可用**（含 Claude/GPT/DeepSeek），全部 OpenAI 兼容格式
- **无安全拦截**: gpt-image-2-4k 不会返回"安全策略拦截"
- **模型路由**: `gpt-image-2-4k` 实际路由为 `gpt-image-2-vip`（见 reference 常见错误表）
- **CDN**: 图片托管在 `pro.filesystem.site`，下载需带浏览器 User-Agent 头
- **⚠️ SSL 问题**: `requests` 库调用报 `SSLError: record layer failure`，必须用 `urllib.request.urlopen(context=ctx)` 绕过，其中 `ctx` 为禁用证书验证的 SSL context

### 视频生成

- **Provider**: iliu.ai (`https://iliu.ai/v1`)
- **模型**: `sora-v4-fast`
- **API Key**: `sk-jDRslt0kupSc7zgHGPkbTuqG2FPnFyznmqpgntGLzq2N9z2L`
- **端点**: `POST /v1/videos/generations`（异步，返回 task_id）
- **查状态**: `GET /v1/videos/{task_id}`（轮询直至 status=completed）
- **支持尺寸**: 960x960, 1280x720, 720x1280, 1920x1080, 1080x1920, 1080x1080
- **耗时**: 约 2-3 分钟

### 豹剪 API（2026-07 新发现）

Provider `豹剪` 支持 gpt-image-2-4k 且无安全拦截：
- Base URL: `https://api.bjzy.nfai.top/v1`
- API Key: `sk-naweFNcH8H7sGyDcNYhOf86GbHSrs23Lb1cFDiwjDyPYb265`
- 可用生图模型：`gpt-image-2-4k`(4K), `gpt-image-2-2k`(2K), `gpt-image-2-1k`(1K), `doubao-seedream-4-0`(豆包)
- 197 模型可用（含 Claude/GPT/DeepSeek），全部走 OpenAI 兼容格式
- 视频模型（sora-2/veo）暂未测试通过

### 降级策略

如果 `iliu.ai` 上的 gpt-image-2 返回"安全策略拦截"，优先尝试 **豹剪** 的 gpt-image-2-4k（同模型名，不同 endpoint），其次切到 FAL。

如果 iliu.ai 的 gpt-image-2 返回"安全策略拦截"或"无法生成图像"，这是 provider 端的限制，非 Key 问题。可尝试：
1. 换英文 prompt 重试
2. 切到 FAL（配置 `auxiliary.image_generation.provider` → FAL）

## Primary Path: Direct API Call via `/v1/chat/completions`

For 心流grop provider (`iliu.ai/v1`), the Hermes Web UI media endpoint's standard OpenAI image endpoints (`/v1/images/generations`, `/v1/images/edits`, `/v1/responses`) are not supported. Always call the provider's **`/v1/chat/completions`** endpoint directly with a vision-capable model:

1. Try `gpt-image-2` (primary)
2. If it fails → `gemini-3-pro-image-preview` (fallback)

See "Fallback: Direct Chat Completions with Vision Models" below for the implementation.

Only attempt the direct chat-completions approach. Do not use any built-in image generation tool (FAL.ai, etc.). If a direct API call returns `401`, `403`, connection failure, or any other auth/token error, stop and report the provider error to the user.

```yaml
custom_providers:
  - name: fun-codex
    base_url: https://api.apikey.fun/v1
    api_key: ...
    model: gpt-5.5
    api_mode: codex_responses
```

Example with another configured provider:

```yaml
custom_providers:
  - name: agnes
    base_url: https://agnes.example/v1
    api_key_env: AGNES_API_KEY
    model: agnes-image-2.1-flash
```

Endpoint:

```bash
POST <Hermes Web UI base URL>/api/hermes/media/apikey-image-generate
```

Resolve the Hermes Web UI base URL in this order:

1. `HERMES_WEB_UI_URL` environment variable, if set.
2. `http://127.0.0.1:${PORT}`, if `PORT` is set.
3. `http://127.0.0.1:8648` for the Web UI single-server default.

Common local ports:

- Development API backend: `http://127.0.0.1:8647`. Use this with `npm run dev`; do not target the Vite frontend port.
- Web UI single-server default: `http://127.0.0.1:8648`.
- Desktop app default: `http://127.0.0.1:8748`.
- Custom port: set `HERMES_WEB_UI_URL` to the full base URL, or set `PORT` to use `http://127.0.0.1:${PORT}`.

When Hermes Web UI is running from Docker Compose, the default external URL is `http://127.0.0.1:6060`.

Authentication:

Send the Hermes Web UI server bearer token. This token is accepted only by Hermes Web UI media generation endpoints for agent skills; it is not a general Web UI login token.

Resolve the token in this order:

1. `AUTH_TOKEN` environment variable, if set.
2. `${HERMES_WEB_UI_HOME}/.token`, if `HERMES_WEB_UI_HOME` is set.
3. `${HERMES_WEBUI_STATE_DIR}/.token`, if `HERMES_WEBUI_STATE_DIR` is set.
4. `~/.hermes-web-ui/.token`.

Profile selection:

Use the current Hermes profile from the run instructions by sending `X-Hermes-Profile`.

If the run instructions include `[Current Hermes profile: <name>]`, include:

```bash
-H "X-Hermes-Profile: <name>"
```

Replace `<name>` with the exact profile name from the run instructions. Never send a placeholder value such as `<name>` or `<current-hermes-profile>`.

If no current profile is provided, omit the header and let the server fall back to the current Hermes active profile.

## Modes

### Text To Image

Use when there is no input image.

```json
{
  "mode": "text",
  "prompt": "A high quality product image of a matte black mechanical keyboard on a clean desk",
  "size": "1024x1024",
  "output_path": "/absolute/path/to/output.png"
}
```

The server calls `POST /v1/images/generations` against the `fun-codex` base URL.
If `provider`, `provider_name`, or `custom_provider` is present, the server calls the requested provider's base URL instead.

### Image To Image

Use when the user provides a reference image and wants a new image based on it.

```json
{
  "mode": "image",
  "prompt": "Use this reference composition and generate a refined technology brand poster",
  "image_path": "/absolute/path/to/reference.png",
  "size": "1024x1024",
  "output_path": "/absolute/path/to/output.png"
}
```

The server calls `POST /v1/responses` against the `fun-codex` base URL.
If `provider`, `provider_name`, or `custom_provider` is present, the server calls the requested provider's base URL instead.

### Image Edit

Use when the user wants to modify an existing image while preserving parts of it.

```json
{
  "mode": "edit",
  "prompt": "Change the background to blue and keep the subject unchanged",
  "image_path": "/absolute/path/to/source.png",
  "size": "1024x1024",
  "output_path": "/absolute/path/to/edited.png"
}
```

The server calls `POST /v1/images/edits` against the `fun-codex` base URL.
If `provider`, `provider_name`, or `custom_provider` is present, the server calls the requested provider's base URL instead.

## Request Fields

- `mode`: `text`, `image`, or `edit`.
- `prompt`: required.
- `provider`: optional configured custom provider name. Defaults to `fun-codex`. `custom:<name>` is accepted and normalized to `<name>`.
- `provider_name`: optional alias for `provider`.
- `custom_provider`: optional alias for `provider`.
- `image_path`: local png, jpeg, or webp path. Required for `image` and `edit` unless using `image_url` or `image_base64`.
- `image_url`: optional alternative image input.
- `image_base64`: optional alternative image input. If it is not a data URI, include `mime_type`.
- `n`: number of images. Defaults to `1`.
- `size`: defaults to `1024x1024`. Common values: `1024x1024`, `1536x1024`, `1024x1536`, `2048x2048`, `3840x2160`, `2160x3840`, `auto`.
- `quality`: defaults to `auto`.
- `model`: optional override. If omitted, text/edit modes use `gpt-image-2`; image mode uses the selected provider's `model` when configured, then falls back to `gpt-5.4-mini`.
- `image_model`: optional image tool model for image mode. Defaults to `gpt-image-2`.
- `output_path`: optional absolute output file path. If omitted, the server saves to `${HERMES_WEB_UI_HOME:-~/.hermes-web-ui}/media/*.png`.
- `timeout_ms`: defaults to `600000`.

## Curl Template

```bash
TOKEN="${AUTH_TOKEN:-}"
if [ -z "$TOKEN" ] && [ -n "${HERMES_WEB_UI_HOME:-}" ] && [ -f "$HERMES_WEB_UI_HOME/.token" ]; then
  TOKEN="$(cat "$HERMES_WEB_UI_HOME/.token")"
fi
if [ -z "$TOKEN" ] && [ -n "${HERMES_WEBUI_STATE_DIR:-}" ] && [ -f "$HERMES_WEBUI_STATE_DIR/.token" ]; then
  TOKEN="$(cat "$HERMES_WEBUI_STATE_DIR/.token")"
fi
if [ -z "$TOKEN" ] && [ -f "$HOME/.hermes-web-ui/.token" ]; then
  TOKEN="$(cat "$HOME/.hermes-web-ui/.token")"
fi
if [ -z "$TOKEN" ]; then
  echo "Missing Hermes Web UI token. Check AUTH_TOKEN, HERMES_WEB_UI_HOME, HERMES_WEBUI_STATE_DIR, or ~/.hermes-web-ui/.token." >&2
  exit 1
fi

BASE_URL="${HERMES_WEB_UI_URL:-}"
if [ -z "$BASE_URL" ]; then
  BASE_URL="http://127.0.0.1:${PORT:-8648}"
fi
BASE_URL="${BASE_URL%/}"

curl -sS -X POST "$BASE_URL/api/hermes/media/apikey-image-generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "mode": "text",
    "provider": "fun-codex",
    "prompt": "A cinematic 4K photo of a silver robot hand holding a small glowing cube",
    "size": "3840x2160",
    "output_path": "/absolute/path/to/output.png"
  }'
```

Successful responses include:

```json
{
  "ok": true,
  "mode": "text",
  "output_paths": ["/absolute/path/to/output.png"],
  "provider": "fun-codex",
  "base_url": "https://api.apikey.fun/v1"
}
```

If the response code is `missing_fun_codex_provider`, tell the user to configure `fun-codex` in the selected/requested profile's `config.yaml`.
If the response code is `missing_apikey_image_provider`, tell the user to configure the requested provider in the selected/requested profile's `config.yaml`, or omit `provider` to use the default `fun-codex` provider.

## Agent Config (config.yaml auxiliary)

This skill targets the Hermes Web UI media endpoint. Separately, the Hermes Agent's own `config.yaml` (at `~/AppData/Local/hermes/config.yaml`) has an `auxiliary` section that controls which provider/model the agent prefers for its built-in `image_generate` tool. To set a preferred provider:

```yaml
auxiliary:
  ...
  image_generation:
    primary:
      provider: "custom:心流grop"
      model: "gpt-image-2"
      api_path: "/v1/chat/completions"
    fallback:
      provider: "custom:心流grop"
      model: "gemini-3-pro-image-preview"
      api_path: "/v1/chat/completions"
    timeout: 600
  video_generation:
    provider: "custom:心流grop"
    model: "grok-imagine-video-1.5-fast"
    timeout: 600
```

Providers like `心流grop` (with `gpt-image-2`, `grok-imagine-image`) or `agnes` (with `agnes-image-2.1-flash`) are common image-capable custom providers.

## Provider Compatibility & Fallback

Not all custom providers support the standard OpenAI image endpoints (`/v1/images/generations`, `/v1/images/edits`, `/v1/responses`). Common Chinese API aggregators (like `心流grop` / `cdn.wusag.com`) often lack some of these endpoints. See `references/provider-compatibility.md` for detailed error transcripts.

### Known Provider Behaviours

| Provider | `/v1/images/generations` | `/v1/images/edits` | `/v1/responses` | ✅ `/v1/chat/completions` (vision) |
|---|---|---|---|---|
| **心流grop** (`cdn.wusag.com`) | ❌ returns empty stream | ❌ SSE parse error / no channel | ❌ 400 "not supported" | ❌ 502 (server down) |
| **心流grop** (`iliu.ai`) | ❌ not supported | ❌ not supported | ❌ not supported | ⚠️ `gpt-image-2` safety blocked, `gemini-3-pro-image-preview` returns empty |
| **agnes** (`apihub.agnes-ai.com`) | ❌ `response_format` param error | — | ❌ 404 | — |

### Fallback: Direct Chat Completions with Vision Models

When the Hermes Web UI media endpoint fails, call the provider's **`/v1/chat/completions`** endpoint **directly** using a vision-capable model. Order of preference:

1. **`gpt-image-2`** (default primary)
2. **`gemini-3-pro-image-preview`** (fallback if gpt-image-2 fails)

Steps:
1. Read the local image and base64-encode it.
2. POST to `{provider_base_url}/v1/chat/completions` with the image as a `data:image/...;base64,...` URL in the messages array.
3. The model returns a markdown response containing an `![image](https://...)` URL — the generated image is hosted on the provider's CDN.
4. Download the image URL with a browser-like `User-Agent` header (CDN may 403 without it).

```python
import json, urllib.request, base64, re, os

# Read & encode image
with open(image_path, 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

def call_image_model(model_name, image_b64, prompt_text):
    """Call provider's /v1/chat/completions for image generation."""
    payload = {
        "model": model_name,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                {"type": "text", "text": prompt_text}
            ]
        }]
    }
    req = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())

# Primary: gpt-image-2
try:
    result = call_image_model("gpt-image-2", img_b64, prompt)
except Exception as e:
    # Fallback: gemini-3-pro-image-preview
    result = call_image_model("gemini-3-pro-image-preview", img_b64, prompt)

# Extract image URL from response
content = result["choices"][0]["message"]["content"]  # ![image](https://...)
match = re.search(r'https://[^\s\)]+', content)
if match:
    download_req = urllib.request.Request(
        match.group(0),
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    with urllib.request.urlopen(download_req) as dl:
        with open(output_path, 'wb') as f:
            f.write(dl.read())
```

### Download Pitfalls

- Generated image URLs often point to R2/Cloudflare-protected CDNs that 403 without a `User-Agent` header — always pass one.
- The URL may be a temporary pre-signed URL that expires; download it immediately.
- Some providers return `webp` or non-standard extensions; save with the correct extension from the URL or force `.jpg`.