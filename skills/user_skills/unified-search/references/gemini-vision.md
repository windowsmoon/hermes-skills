# Gemini 3.5 Flash 视觉理解

## 配置信息
- **Provider**: `custom:gemini`
- **Model**: `gemini-3.5-flash`（支持 vision）
- **API Key**: `AIzaSyA4DUiI0R9nLqymaFu1uQ9fCYgUdvy_mOg`
- **账号**: `fuyaozhishang2023@gmail.com`
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent`
- **上下文**: 1,048,576 tokens（1M）
- **免费额度**: 1,500 次/天（token 本身免费）
- **已验证日期**: 2026-07-22

## 已验证能力
- ✅ 文本生成
- ✅ 图像理解（Vision）— 传入 base64 inline_data 即可
- ✅ 内置 thinking/reasoning

## 使用场景
用户主要用 Gemini 3.5 Flash 做视频/图片视觉理解（vision），
日常文本对话仍走 deepseek-v4-flash。

## 调用方式
```python
import requests, base64

API_KEY = "AIzaSyA4DUiI0R9nLqymaFu1uQ9fCYgUdvy_mOg"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY}"

with open("image.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "contents": [{"parts": [
        {"text": "描述这张图片"},
        {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
    ]}]
}
resp = requests.post(url, json=payload)
text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
```

## 注意
- 不支持 Deep Research / Deep Research Max（需 GCP 企业账号）
- 不支持 MCP 对接
- 标准 Gemini API 不支持 `:interact` 端点
- `generateContent` 是标准端点
