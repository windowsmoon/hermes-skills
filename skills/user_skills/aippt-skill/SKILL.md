---
name: aippt-skill
description: >
  当用户需要aippt-skill时使用。
  不要用于：无关场景。
  触发词：AiPPT、文多多、在线生成PPT、AI做PPT
tags:
  - ppt
  - aippt
  - presentation
  - ai
triggers:
  - AiPPT
  - 文多多
  - 在线生成PPT
  - AI做PPT

---

# AiPPT Skill

## 说明

本 Skill 通过 AiPPT.cn（文多多）开放平台 API 生成 PPT。
注意：使用前需要去 https://docmee.cn/open-platform 注册获取 API Token。

## 功能

- 标题生成PPT：输入主题，自动生成大纲和PPT
- 联网智能生成：联网搜索补充内容后生成
- 文件导入生成：上传 PDF/DOCX/TXT/MD 文件生成 PPT
- URL 导入：输入网页链接生成 PPT
- 模板选择：从模板库选择风格
- 导出大纲：先生成大纲，确认后再生成PPT
- 自动导出下载：生成完成后自动下载 PPTX

## 依赖

```bash
pip install requests
```

## 配置

在 ~/.aippt_config.json 中设置：
```json
{
  "api_key": "your_api_key_here"
}
```

API Key 已配置在 ~/.aippt_config.json

## 使用示例

```python
python -c "
# 文多多 AiPPT API 示例
import requests
# 创建生成任务
resp = requests.post('https://api.docmee.cn/v1/ppt/generate', json={
    'title': 'AI 发展趋势报告',
    'template': 'modern-blue',
    'pages': 10
}, headers={'Authorization': 'Bearer YOUR_API_KEY'})
print(resp.json())
"
```
