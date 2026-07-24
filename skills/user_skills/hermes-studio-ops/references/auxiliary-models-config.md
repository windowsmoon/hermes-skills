# Auxiliary Models API 配置

## 用途
Hermes Studio 的辅助模型配置，用于非对话类任务（Vision/生图/生视频/Web提取等）。

## API
```bash
# 查看当前配置
GET /api/hermes/config/auxiliary-models

# 更新指定任务类型的模型（只传要改的 key）
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

## 支持的任务类型

| 任务 Key | 说明 | 当前配置（2026-07-22） |
|----------|------|:-------------------:|
| `vision` | 图片/视频视觉理解 | custom:gemini → gemini-3.5-flash |
| `image_generation` | 图片生成 | custom:豹剪 → gpt-image-2-4k |
| `video_generation` | 视频生成 | custom:视频生成(iliu.ai) → sora-v4-fast |
| `web_extract` | 网页内容提取 | custom:183399 → MiniMax-M3 |
| `title_generation` | 标题生成 | custom:agnes → agnes-2.0-flash |
| `approval` | 写操作审批 | custom:183399 → deepseek-v4-pro |
| `profile_describer` | Profile 描述 | custom:183399 → deepseek-v4-pro |
| `mcp` | MCP 回调 | custom:agnes → agnes-2.0-flash |

## 注意事项
- PUT 只传需要修改的 key，其他保持不变（不是全量替换）
- 每个任务有自己的 timeout（秒）：vision=120, web_extract=360, image_generation=120
- Provider 名称必须与 Hermes 配置的 provider 名匹配
- 2026-07-22: vision 从 qwen3-vl-plus 切换到 gemini-3.5-flash，因为 qwen-vl 的 vision_analyze 报错 "model not found"
