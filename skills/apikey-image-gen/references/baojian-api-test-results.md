# 豹剪 API 测试结果 (2026-07-18)

## Provider 信息
- Base URL: https://api.bjzy.nfai.top/v1
- API Key: sk-naweFNcH8H7sGyDcNYhOf86GbHSrs23Lb1cFDiwjDyPYb265

## 可用模型（197个）
含 Claude/GPT/DeepSeek/豆包/Gemini/Grok 全系列。

## 图片生成测试
| 模型 | 结果 |
|------|:----:|
| gpt-image-2-4k | ✅ 成功（4K） |
| gpt-image-2-2k | ✅ 成功（2K） |
| gpt-image-2-1k | ✅ 成功（1K） |
| doubao-seedream-4-0 | ✅ 成功（豆包模型） |
| gpt-image-2 | ⏰ 超时 |
| gemini-3-pro-image-preview | ❌ 429 Too Many Requests |

## 视频生成测试
| 模型 | 结果 |
|------|:----:|
| sora-2 | ❌ 500 Internal Server Error |
| veo_3_1 | ❌ 429 Too Many Requests |

## 调用方式
POST https://api.bjzy.nfai.top/v1/chat/completions
Authorization: Bearer sk-naweFNcH8H7sGyDcNYhOf86GbHSrs23Lb1cFDiwjDyPYb265
Content-Type: application/json

{
  "model": "gpt-image-2-4k",
  "messages": [{
    "role": "user",
    "content": [{"type": "text", "text": "prompt here"}]
  }]
}

## 模型路由（2026-07-20 发现）
- `gpt-image-2-4k` 请求 → 服务端实际路由为 `gpt-image-2-vip`
- 响应中 `model` 字段返回 `gpt-image-2-vip`，非请求时传入的 `gpt-image-2-4k`
- 这不影响使用，但调试时注意不要被 model 字段迷惑

## 响应格式
- 图片 URL 在 `choices[0].message.content` 中，格式为 Markdown：
  ```
  ![https://pro.filesystem.site/cdn/...](https://pro.filesystem.site/cdn/...)
  [点击下载](https://pro.filesystem.site/cdn/download/...)
  ```
- 不要用 `choices[0].message.content` 的 JSON 解析——直接提取 Markdown 图片链接

## CDN 注意事项
- 图片 CDN 域名：`pro.filesystem.site`
- URL 路径模式：`/cdn/{YYYYMMDD}/{hash}.png`
- 下载时必须加浏览器 User-Agent 头，否则 CDN 返回 403：
  ```
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
  ```
- 可下载链接（download 路径）与直接预览链接（cdn 路径）都可访问
- 建议下载后立即保存到本地，CDN 链接可能有时效性

## 常见错误
| 错误 | 原因 | 解决 |
|------|------|------|
| 401 Invalid token | 用了心流 Key（sk-jDRslt...） | 换豹剪 Key（sk-naweFNc...） |
| 403 下载失败 | 缺 User-Agent 头 | 加浏览器 UA 头 |
| 超时 | 复杂 prompt 生成慢 | 增加 timeout 到 180s |
