# Auxiliary Models API 配置指南

> Hermes Studio API 的 `auxiliary-models` 端点用于配置非对话类任务的专用模型（视觉、生图、生视频、网页提取等）。

## 端点

```
GET  /api/hermes/config/auxiliary-models  → 查看当前配置
PUT  /api/hermes/config/auxiliary-models  → 更新配置
```

## 当前支持的任务类型

| key | label | 默认超时 | 说明 |
|-----|-------|:--------:|------|
| `vision` | Vision | 120s | 图片/视频视觉理解 |
| `image_generation` | Image generation | 120s | 文本生图 |
| `video_generation` | Video generation | 600s | 文本生视频 |
| `web_extract` | Web extract | 360s | 网页内容提取 |
| `compression` | Compression | 120s | — |
| `title_generation` | Title generation | 30s | — |
| `approval` | Approval | 30s | 写操作审批 |
| `profile_describer` | Profile describer | 60s | — |
| `mcp` | MCP | 30s | — |
| `skills_hub` | Skills hub | 30s | — |
| `session_search` | Session search | 30s | — |
| `flush_memories` | Flush memories | 30s | — |
| `kanban_decomposer` | Kanban decomposer | 180s | — |
| `triage_specifier` | Triage specifier | 120s | — |
| `curator` | Curator | 600s | — |

## 配置结构

### 完整配置示例（GET 返回）

```json
{
  "tasks": [
    {"key": "vision", "label": "Vision", "default_timeout": 120},
    {"key": "web_extract", "label": "Web extract", "default_timeout": 360},
    ...
  ],
  "auxiliary": {
    "vision": {
      "provider": "custom:gemini",
      "model": "gemini-3.5-flash",
      "timeout": 120
    },
    "image_generation": {
      "provider": "custom:豹剪",
      "model": "gpt-image-2-4k",
      "timeout": 120,
      "api_key": "sk-...",
      "base_url": "https://api.bjzy.nfai.top/v1"
    },
    "video_generation": {
      "provider": "custom:视频生成(iliu.ai)",
      "model": "sora-v4-fast",
      "timeout": 600,
      "api_key": "sk-...",
      "base_url": "https://iliu.ai/v1"
    }
  }
}
```

### 更新时只传要改的部分

```json
PUT /api/hermes/config/auxiliary-models
{
  "auxiliary": {
    "vision": {
      "provider": "custom:gemini",
      "model": "gemini-3.5-flash",
      "timeout": 120
    }
  }
}
```

- 不需要传完整的 auxiliary 对象，只需传要修改的 key
- 其他未传的 key 保持原值不变
- 每个 key 至少需要 `provider` + `model`
- 某些 provider 需要额外字段：`api_key`、`base_url`

## 应用层调用链

Hermes Agent 在以下情况会自动调用 auxiliary model：
1. **vision_analyze(image_url)** → 走 `auxiliary.vision` 配置的 provider/model
2. **image_generate(prompt)** → 走 `auxiliary.image_generation`
3. **视频分析**（vision 调用时传 video 数据）→ 同样走 `auxiliary.vision`
4. **web_extract(url)** → 走 `auxiliary.web_extract`

## 实践记录

### Gemini 3.5 Flash 配置为 vision provider（2026-07-22）

```bash
# 1. 测试 API Key 和 vision 能力
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=$KEY \
  -d '{"contents":[{"parts":[{"text":"描述这张图"},{"inline_data":{"mime_type":"image/jpeg","data":"..."}}]}]}'

# 2. 在 Hermes Studio 中配置
PUT /api/hermes/config/auxiliary-models
{
  "auxiliary": {
    "vision": {
      "provider": "custom:gemini",
      "model": "gemini-3.5-flash",
      "timeout": 120
    }
  }
}
```

**关键验证：**
- ✅ Gemini 3.5 Flash 支持视频分析（10MB+、12秒视频测试通过）
- ✅ 1M tokens 上下文窗口
- ✅ 免费额度：1,500 次/天
- ⚠️ Deep Research Max 功能不可用（需 GCP 企业账号 + Interactions API）
- ⚠️ 标准 Gemin API Key 无法调用 Deep Research 模型

### 其他支持的 Gemini 视觉模型

| 模型 | Vision | 1M上下文 | 备注 |
|------|:------:|:--------:|------|
| gemini-3.5-flash | ✅ | ✅ | 推荐，免费 |
| gemini-3.5-flash-lite | ✅ | ✅ | 更快更省 |
| gemini-2.5-flash | ✅ | ✅ | 旧版 |
| gemini-2.5-pro | ✅ | ✅ | 更强但可能收费 |

## 注意事项

- `vision` 任务默认超时 120s — 大视频可能需要调大
- Gemini API video 输入限制：最大约 20MB base64 编码
- auxiliary-models 配置不验证 provider 是否存在，配错了也不会报错（直到实际调用时）
- 切换 provider 后已经存在的会话会立即生效（不需要重启）
