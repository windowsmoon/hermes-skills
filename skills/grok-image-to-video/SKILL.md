---
name: grok-image-to-video
description: >
  当用户需要grok-image-to-video时使用。
  不要用于：无关场景。
  触发词：图片转视频、图片动起来、grok视频
version: 1.2.0
author: Ekko
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [xAI, Grok, image-to-video, video-generation, media]
prerequisites:
  commands: [curl]
triggers:
  - 图片转视频
  - 图片动起来
  - grok视频

---

# Grok Image To Video

Use this skill when the user wants to animate a local image into a short video with xAI Grok Imagine.

Do not use any built-in image or video generation tool as a fallback. If the Hermes Web UI endpoint returns `401`, `403`, connection failure, or any other error, stop and report the Hermes Web UI error to the user.

## Workflow

Call the local Hermes Web UI media endpoint. Pass a local image path; the server will check for xAI credentials, read the file, convert it to a base64 data URI, call xAI, poll until completion, and optionally save the generated mp4.

Endpoint:

```bash
POST <Hermes Web UI base URL>/api/hermes/media/grok-image-to-video
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

When Hermes Web UI is running from the provided Docker Compose setup, the default external URL is `http://127.0.0.1:6060`.

Authentication:

The endpoint is protected by Hermes Web UI auth. Always send the Hermes Web UI server bearer token. This token is accepted only by Hermes Web UI media generation endpoints for agent skills; it is not a general Web UI login token.

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

Required JSON fields:

- `image_path`: local path to a png, jpeg, or webp image.
- `prompt`: motion and style instructions for the generated video.

Optional JSON fields:

- `duration`: seconds, 1 to 15. Defaults to 8.
- `output_path`: local path where the server should save the mp4. If omitted, the server saves to `${HERMES_WEB_UI_HOME:-~/.hermes-web-ui}/media/<request_id>.mp4` and creates the `media` directory if needed.
- `timeout_ms`: maximum wait time. Defaults to 600000.

Example:

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

curl -sS -X POST "$BASE_URL/api/hermes/media/grok-image-to-video" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "image_path": "/absolute/path/to/input.png",
    "prompt": "Animate the subject with a slow cinematic push-in and subtle natural motion.",
    "duration": 8,
    "output_path": "/absolute/path/to/output.mp4"
  }'
```

If the response has `code: "missing_xai_token"`, tell the user to set `XAI_API_KEY` or complete xAI OAuth login in Hermes Web UI before retrying, OR fall back to a custom video provider (see "Custom Provider Fallback" below).

## Custom Provider Fallback

If the Hermes Web UI xAI endpoint is unavailable, call the configured video provider's API directly via `/v1/chat/completions` with a video-capable model.

### Provider Configuration

Add a dedicated video provider to `custom_providers` in config.yaml:

```yaml
custom_providers:
  - name: "videogen"
    base_url: "https://cdn.wusag.com/v1"
    api_key: "sk-..."
    model: "grok-imagine-video-1.5-fast"
    api_mode: "chat_completions"
```

Set `video_generation` in the `auxiliary` section to use it:

```yaml
auxiliary:
  ...
  video_generation:
    provider: "custom:videogen"
    model: "grok-imagine-video-1.5-fast"
    api_path: "/v1/chat/completions"
    timeout: 600
```

### Direct API Call

grok-imagine-video-1.5-fast 强制返回 SSE 流式响应（即使不传 `stream: true`），响应中：

- `delta.reasoning_content` 只含进度百分比（如 `视频正在生成 50%`）
- `delta.content` 含最终的**视频下载 URL**

必须解析 SSE 流才能拿到 URL，不能用 `json.loads(resp.read())` 直接解析。

```python
import json, urllib.request, base64, re

with open(image_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "model": "grok-imagine-video-1.5-fast",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {"type": "text", "text": prompt_text}
        ]
    }]
}

req = urllib.request.Request(
    f"{base_url}/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
)

# grok-imagine-video-1.5-fast 强制 SSE 流，必须逐行解析
with urllib.request.urlopen(req, timeout=300) as resp:
    raw_text = b""
    for line in resp:
        raw_text += line

# 从 SSE 流中提取 delta.content 的 URL（非 reasoning_content）
video_url = None
for chunk_text in raw_text.decode('utf-8').split('\n\n'):
    if not chunk_text.strip().startswith('data: ') or chunk_text == 'data: [DONE]':
        continue
    try:
        chunk = json.loads(chunk_text[6:])
        delta = chunk.get("choices", [{}])[0].get("delta", {})
        content = delta.get("content", "")
        if content and ('proxy.wusag.com' in content or '/video' in content or '.mp4' in content):
            urls = re.findall(r'https://[^\s<>\)\'\"]+', content)
            if urls:
                video_url = urls[0]
                break
    except Exception:
        pass

if video_url:
    dl_req = urllib.request.Request(
        video_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://cdn.wusag.com/",
        }
    )
    with urllib.request.urlopen(dl_req, timeout=120) as dl:
        with open(output_path, "wb") as f:
            f.write(dl.read())
else:
    raise RuntimeError(f"No video URL found in SSE stream. Raw: {raw_text.decode('utf-8')[-500:]}")
```

### 模型响应模式

不同视频模型返回 URL 的位置不同：

| 模型 | URL 在 | 是否 SSE 流 | 示例响应字段 |
|---|---|---|---|
| `grok-imagine-video-1.5-fast` | `delta.content`（进度完成后） | ✅ 强制 SSE | `content: https://proxy.wusag.com/...video?id=...` |
| `omni_flash` | `message.content`（直接返回） | ❌ 普通响应 | `content: ✅ 视频生成完成\n[下载](https://download-2.oaibox.xyz/...)` |

**注意**：不要传 `stream: false` 试图阻止 SSE——`grok-imagine-video-1.5-fast` 忽略该参数，始终返回 SSE。

### omni_flash 直接调用参考

```python
# omni_flash 返回普通 JSON（非 SSE），URL 在 message.content 中
with urllib.request.urlopen(req, timeout=300) as resp:
    result = json.loads(resp.read())

content = result["choices"][0]["message"]["content"]
urls = re.findall(r'https://[^\s\)\]]+', content)
video_url = urls[0]  # 取第一个匹配到的 URL
```

## Agent Config (config.yaml auxiliary)

The Hermes Agent's own `config.yaml` (at `~/AppData/Local/hermes/config.yaml`) has an `auxiliary` section that can control which provider/model the agent prefers for video generation. The recommended setup uses a dedicated videogen provider:

```yaml
auxiliary:
  ...
  video_generation:
    provider: "custom:videogen"        # dedicated video provider
    model: "grok-imagine-video-1.5-fast"
    api_path: "/v1/chat/completions"    # correct API path for this provider
    timeout: 600
```

Common video-capable models available through third-party providers include `grok-imagine-video-1.5-fast`, `veo_3_1-fast`, `omni_flash`, `sora-2`, and `agnes-video-v2.0`. Check the provider's advertised model list before settling on one.

Return the generated `output_path`.