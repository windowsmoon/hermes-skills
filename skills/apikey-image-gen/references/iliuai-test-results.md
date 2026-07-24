# iliu.ai 测试结果 (2026-07-17)

## 背景
- 心流grop 原域名 `cdn.wusag.com` 返回 502 Bad Gateway
- 用户提供替代域名 `iliu.ai` 作为 base URL
- API Key: 沿用原心流 Key

## 测试结果

| 模型 | 结果 |
|------|------|
| `POST iliu.ai/v1/chat/completions` (gpt-image-2) | ⚠️ 服务器连通成功，但安全策略拦截："您的请求无法用于生成图像。该请求可能因安全政策被拦截" |
| `POST iliu.ai/v1/chat/completions` (gemini-3-pro-image-preview) | ⚠️ 返回空内容（无 error，无图片 URL） |
| 英文 prompt 测试 | 同样被安全策略拦截 |

## 结论
- iliu.ai 服务器是活的（无 502/504）
- 但 gpt-image-2 的安全策略与 cdn.wusag.com 一致，正常 prompt 也被拦
- 这不是域名问题，是 provider 对 gpt-image-2 模型做了安全限制
- FAL.ai 是当前可用的替代方案（Key 已配，FLUX 模型）
