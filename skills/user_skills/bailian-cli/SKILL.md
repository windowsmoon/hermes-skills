---
name: bailian-cli
description: >
  当用户需要通过阿里云百炼/DashScope API调用多模态能力时使用。
  支持：文本生成、图像理解、图像生成、语音识别TTS、搜索。
  不要用于：非阿里云百炼的模型调用、日常LLM对话（走default模型）。
  触发词：百炼、DashScope、阿里云百炼、通义千问API、调用多模态模型
tags:
  - bailian
  - dashscope
  - qwen
  - multimodal
  - aliyun
triggers:
  - 百炼
  - DashScope
  - 阿里云百炼
  - 通义千问API
  - 调用多模态模型

---

# 百炼 CLI (DashScope API 版)

## 说明

由于阿里云百炼官方 CLI 包未公开到 npm 公共源，本脚本通过 DashScope API 实现同等功能。

## 可用命令

```bash
python ~/AppData/Local/hermes/scripts/bailian_cli.py <模式> <输入> [选项]
```

| 模式 | 命令 | 说明 |
|------|------|------|
| **文本对话** | `chat "你好"` | qwen3.7-plus |
| **图像理解** | `vision "描述这张图" --file photo.jpg` | qwen3-vl-plus |
| **图像生成** | `image "一只猫"` | qwen-image-2.0 |
| **联网搜索** | `search "今天天气"` | qwen-web-search |
| **语音合成** | `tts "你好世界"` | → 保存为 mp3 |
| **语音识别** | `asr --file audio.mp3` | qwen3-asr-flash |
| **模型列表** | `models` | 查看所有可用模型 |

## 选项

| 参数 | 说明 |
|------|------|
| `--model, -m` | 指定模型（默认自动选择） |
| `--system, -s` | 设置 System Prompt |
| `--file, -f` | 输入文件（图片/音频） |

## 示例

```bash
# 分析图片
python bailian_cli.py vision "这个界面有什么问题" --file screenshot.png

# 生成电商主图
python bailian_cli.py image "纯黑色男装T恤，简约风，白色背景"

# 联网搜索
python bailian_cli.py search "2024年AI发展趋势"

# 语音转文字
python bailian_cli.py asr --file meeting.mp3
```

## 备用：硅基流动 DeepSeek OCR + TTS

当阿里云 DashScope TTS 接口不可用时，可切换用 硅基流动（SiliconFlow）API：

### DeepSeek OCR（图片文字识别）

```python
python ~/AppData/Local/hermes/scripts/sf_cli.py ocr <图片路径> [提示词]
```

模型：`deepseek-ai/DeepSeek-OCR`（硅基流动）
API Key：同 `HINDSIGHT_LLM_API_KEY`（在 `~/.hermes/.env`）

### CosyVoice TTS（语音合成）

API 接口可用但需确认 voice 参数。测试过的 voice 名称均未通过，建议用 Hermes 内置 `text_to_speech` 工具作为 TTS 兜底，或直接用 Edge TTS。

### SenseVoice ASR（语音识别）

模型：`FunAudioLLM/SenseVoiceSmall`（硅基流动）

### 完整模型列表

硅基流动上可用的服务（已验证）：
| 服务 | 模型 | 状态 |
|------|------|------|
| DeepSeek OCR | `deepseek-ai/DeepSeek-OCR` | ✅ 可用 |
| PaddleOCR | `PaddlePaddle/PaddleOCR-VL-1.5` | ✅ 可用 |
| CosyVoice TTS | `FunAudioLLM/CosyVoice2-0.5B` | ⚠️ voice 参数待确认 |
| SenseVoice ASR | `FunAudioLLM/SenseVoiceSmall` | ✅ 可用 |
| MOSS TTS | `fnlp/MOSS-TTSD-v0.5` | ⚠️ |
| TeleSpeech ASR | `TeleAI/TeleSpeechASR` | ✅ 可用 |

## 注意

- 使用 DashScope API Key（`sk-3256...b1`）
- 硅基流动 Key（`HINDSIGHT_LLM_API_KEY`）来自 `~/.hermes/.env`
- 图像生成需等待 10-30 秒
- 搜索有免费额度
