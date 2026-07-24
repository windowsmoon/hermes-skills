# MinerU 云端 API 参考

> 来源：mineru.net 官方文档（2026-07-21）

## 两种 API 模式

### 🎯 精准解析 API（需 Token）

| 项目 | 值 |
|------|-----|
| 接口 | `POST /api/v4/extract/task`（单文件）或 `POST /api/v4/file-urls/batch`（批量） |
| 模型 | `pipeline`（默认） / `vlm`（推荐） / `MinerU-HTML` |
| 文件大小 | ≤ 200MB |
| 页数 | ≤ 200 页 |
| 批量 | ≤ 200 个文件 |
| 输出格式 | ZIP（含 Markdown + JSON，可导出 DOCX/HTML/LaTeX） |
| 调用方式 | 异步（提交 → 轮询结果） |
| 免费额度 | 每天 1000 页最高优先级，超出部分优先级降低 |

### ⚡ Agent 轻量解析 API（免 Token）

| 项目 | 值 |
|------|-----|
| 接口 | `POST /api/v1/agent/parse/url` 或 `POST /api/v1/agent/parse/file` |
| 模型 | 固定 pipeline 轻量模型 |
| 文件大小 | ≤ 10MB |
| 页数 | ≤ 20 页 |
| 输出格式 | 仅 Markdown（CDN 链接） |
| 认证 | IP 限频（无需 Token） |

## 支持的格式

PDF、图片（png/jpg/jpeg/jp2/webp/gif/bmp）、Doc、Docx、PPT、PPTx、XLS、XLSx

## 使用示例

### 精准 API（单文件）

```python
import requests

token = "你的 MinerU Token"
url = "https://mineru.net/api/v4/extract/task"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
data = {
    "url": "https://cdn-mineru.openxlab.org.cn/demo/example.pdf",
    "model_version": "vlm"
}
resp = requests.post(url, headers=headers, json=data)
print(resp.json())
```

### 轮询结果

```python
task_id = resp.json()["data"]["taskId"]
result_url = f"https://mineru.net/api/v4/extract/result/{task_id}"
resp = requests.get(result_url, headers=headers)
# 轮询直到 status == "done"
```

### Agent 轻量 API

```python
url = "https://mineru.net/api/v1/agent/parse/url"
data = {
    "url": "https://example.com/document.pdf",
    "model_version": "pipeline"
}
resp = requests.post(url, json=data)
```

## MCP Server

```json
{
  "mcpServers": {
    "mineru": {
      "type": "streamableHttp",
      "url": "https://mcp.mineru.net/mcp",
      "env": { "MINERU_API_TOKEN": "your token" }
    }
  }
}
```

## 注册获取 Token

1. 打开 https://mineru.net/apiManage
2. 注册账号
3. 在 API 管理页面创建 Token