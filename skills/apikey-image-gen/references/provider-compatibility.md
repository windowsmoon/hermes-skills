# Provider Compatibility: Image Endpoints

Discovered during a cloud-horse image editing session (2026-07-08) against two Chinese API aggregators. Records which endpoints work and which do not, plus the successful fallback path.

## Provider: 心流grop

**Base URL:** `https://cdn.wusag.com/v1`
**API Key:** `sk-jDR...` (configured in custom_providers)
**Models tested:** `gpt-image-2`, `grok-imagine-image`, `grok-imagine-image-pro`, `grok-imagine-image-edit`

### Endpoint Test Results

#### `/v1/images/generations` (via mode="text")

| Model | Result |
|---|---|
| `gpt-image-2` | `502: image generation stream ended without image data` — request accepted, upstream returned empty SSE stream |
| `grok-imagine-image-pro` | `502: image generation stream ended without image data` |
| `grok-imagine-image` | Not tested via this path |

#### `/v1/images/edits` (via mode="edit")

| Model | Result |
|---|---|
| `gpt-image-2` | `502: Syntax error at index 1: invalid char\nevent: image_generation.complete` — upstream returned SSE stream, Hermes Web UI expected JSON |
| `grok-imagine-image` | `502: Syntax error no sources available, the input json is empty` |
| `grok-imagine-image-edit` | `503: No available channel for model grok-imagine-image-edit under group default` |

#### `/v1/responses` (via mode="image")

| Model | Result |
|---|---|
| `gpt-image-2` | `400: 该平台不支持【/v1/responses】端点调用` — provider explicitly blocks this endpoint |
| `agnes-image-2.1-flash` | `404: Not Found` |

#### ✅ `/v1/chat/completions` (direct — primary path)

| Model | Result |
|---|---|
| `gpt-image-2` | `200 OK` — returns markdown `![image](https://oss.filenest.top/uploads/...)`. This is the **primary** image generation model. |
| `gemini-3-pro-image-preview` | `200 OK` — fallback if `gpt-image-2` fails. |
| `grok-imagine-image` | `200 OK` — also works but NOT preferred. Do NOT use. |

### Notes

- **The correct API path for 心流grop is `/v1/chat/completions`**, NOT `/v1/images/generations` or `/v1/responses`. The Hermes Web UI media endpoint constructs the wrong upstream URL (doubling `/v1/` or calling unsupported endpoints).
- **Always try `gpt-image-2` first**, fallback to `gemini-3-pro-image-preview`. Do not use `grok-imagine-image`.

## Provider: agnes

**Base URL:** `https://apihub.agnes-ai.com/v1`
**Models tested:** `agnes-image-2.0-flash`, `agnes-image-2.1-flash`

### Endpoint Test Results

| Endpoint | Model | Result |
|---|---|---|
| `/v1/images/generations` (mode="text") | `agnes-image-2.1-flash` | `400: Setting \`response_format\` is not supported by openai, agnes-t2i-general-model. To drop it, set \`litellm.drop_params = True\`` |
| `/v1/images/generations` (mode="text") | `agnes-image-2.0-flash` | Same error — the Hermes Web UI sends a `response_format` param that the upstream model rejects |
| `/v1/responses` (mode="image") | `agnes-image-2.1-flash` | `404: Not Found` |

### Notes

- The root cause is the Hermes Web UI's media endpoint adding `response_format` to the upstream request. Configuring `litellm.drop_params = True` on the provider proxy side would fix it, but that's outside the agent's control.
- Neither `agnes-image-*` model works through the current Hermes Web UI media pipeline.

## General Guidelines

1. **Always try the Hermes Web UI endpoint first** — it handles auth, file reading, and output saving automatically.
2. **If the error code is 502 with an upstream error message**, examine the upstream body:
   - `Syntax error` or SSE content → provider doesn't return JSON-compliant responses for that endpoint → switch to `/v1/chat/completions` fallback.
   - `stream ended without image data` → provider accepted request but returned empty → try again with simpler prompt or different model.
   - `not supported` → provider explicitly blocks the endpoint → don't retry.
3. **If the error code is 400** (like agnes's `response_format`), the param incompatibility is at the Hermes Web UI middleware level — cannot work around without modifying the Web UI, so fall back to direct API call.
4. **For the fallback** via `/v1/chat/completions`:
   - The model must be a vision model that can PROCESS an input image (e.g. `grok-imagine-image` on 心流grop).
   - Send the image as `data:image/jpeg;base64,...` in a user message with content type `image_url`.
   - The model returns a markdown image link, not raw binary — extract the URL and download it separately.
   - CDN URLs (R2, Cloudflare) 403 without a browser `User-Agent` header.
