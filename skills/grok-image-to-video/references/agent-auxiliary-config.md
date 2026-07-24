---
description: "Agent Auxiliary Config — Image & Video Generation provider settings"
---

# Agent Auxiliary Config — Image & Video Generation

The Hermes Agent's `config.yaml` (at `~/AppData/Local/hermes/config.yaml`) supports an `auxiliary` section that routes various sub-tasks to a user-preferred provider/model pair. Two keys control multimodal generation:

```yaml
auxiliary:
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
    provider: "custom:videogen"
    model: "grok-imagine-video-1.5-fast"
    api_path: "/v1/chat/completions"
    timeout: 600

custom_providers:
  - name: "心流grop"
    base_url: "https://cdn.wusag.com/v1"
    model: "gpt-5.5"
    api_mode: "chat_completions"
  - name: "videogen"
    base_url: "https://cdn.wusag.com/v1"
    model: "grok-imagine-video-1.5-fast"
    api_mode: "chat_completions"
```

## 常用模型一览

| Provider | 能力 | 模型 | API 路径 |
|---|---|---|---|
| **心流grop** | 生图（主） | `gpt-image-2` | `/v1/chat/completions` |
| **心流grop** | 生图（备用） | `gemini-3-pro-image-preview` | `/v1/chat/completions` |
| **videogen** | 生视频 | `grok-imagine-video-1.5-fast` | `/v1/chat/completions` |
| **心流grop** | 生视频（备用） | `omni_flash`, `veo_3_1-fast`, `sora-2` | `/v1/chat/completions` |
| **agnes** | 生图 | `agnes-image-2.0-flash`, `agnes-image-2.1-flash` | `/v1/chat/completions` |
| **agnes** | 生视频 | `agnes-video-v2.0` | `/v1/chat/completions` |

## 视频模型响应模式（关键区别）

| 模型 | URL 在哪里 | 是否 SSE 流 | 处理方式 |
|---|---|---|---|
| `grok-imagine-video-1.5-fast` | `delta.content`（进度完成后） | ✅ 强制 SSE，不可关闭 | 逐行解析 SSE，从 `delta.content` 提取 `proxy.wusag.com` URL |
| `omni_flash` | `message.content`（直接返回） | ❌ 普通 JSON | 直接 `json.loads(resp.read())`，从 `content` 提取 `download-2.oaibox.xyz` URL |

## 正确路径 vs 错误路径

心流grop 上的模型**不支持**以下 OpenAI 标准端点：
- ❌ `/v1/images/generations` — 返回空 SSE 流
- ❌ `/v1/images/edits` — SSE 解析错误
- ❌ `/v1/responses` — 400 不支持
- ✅ `/v1/chat/completions` — 唯一正确路径

所有生图、生视频调用统一走 `/v1/chat/completions`，model 决定生成什么类型。
