# CLI 工具参考

## edrawmind_cli.py 完整参数参考

零依赖 Python 脚本，通过 EdrawMind HTTP API 将 Markdown 转化为专业思维导图。

### 调用方式

```bash
# 方式1: 从文件读取
python edrawmind_cli.py input.md [OPTIONS]

# 方式2: 从 stdin 读取（管道）
echo "# AI\n## ML\n- DL" | python edrawmind_cli.py - [OPTIONS]

# 方式3: 内联文本（推荐，无需临时文件）
python edrawmind_cli.py --text "# AI\n## ML\n- Deep Learning" [OPTIONS]
```

### 参数列表

#### 输入参数
| 参数 | 说明 |
|------|------|
| `FILE` | Markdown 文件路径，`-` 表示 stdin。与 `--text` 互斥 |
| `--text MARKDOWN` | 内联 Markdown 内容，`\n` 表示换行。与 FILE 互斥 |

#### 样式参数
| 参数 | 值域 | 说明 |
|------|------|------|
| `-l N, --layout N` | 1–12 | 布局类型，默认 1 |
| `-t N, --theme N` | 1–10 | 主题风格 |
| `-b BG, --background BG` | 1–15 或 `#RRGGBB` | 画布背景 |
| `--line-hand-drawn` | flag | 手绘连线 |
| `--fill STYLE` | none/pencil/watercolor/charcoal/paint/graffiti | 节点填充手绘 |

#### 网络参数
| 参数 | 说明 |
|------|------|
| `--api-key KEY` | API 密钥（可选，当前免费） |
| `--api-url URL` | 自定义 API 端点（覆盖区域检测） |
| `--region auto/cn/global` | 区域选择，默认 auto 自动探测 |
| `--insecure` | 跳过 SSL 验证（仅开发用） |

#### 输出参数
| 参数 | 说明 |
|------|------|
| `-o PATH, --output PATH` | 保存 JSON 响应到文件 |
| `--json` | 输出完整 JSON 到 stdout |
| `-q, --quiet` | 仅输出 file URL |
| `--open` | 在默认浏览器中打开生成的思维导图 |
| `--no-validate` | 跳过 Markdown 输入验证 |
| `-V, --version` | 显示版本号 |

### 成功响应格式

```json
{
  "file_url": "https://edrawmind.com/...",
  "thumbnail_url": "https://edrawmind.com/thumb/...",
  "extra_info": {
    "elapsed_ms": 962,
    "request_id": "aaf23d94f8d044e68ba2211213b922c7"
  }
}
```

| 字段 | 说明 |
|------|------|
| `file_url` | 在线编辑链接，**必须展示给用户** |
| `thumbnail_url` | 缩略图预览 URL |

### 错误状态码

| HTTP | 含义 |
|------|------|
| 200 code=0 | 成功 |
| 4xx | 参数错误（格式校验失败） |
| 429 | 频率限制，重试 |
| 5xx | 服务端错误 |

### API 端点

- 国内: `https://mindapi.edrawsoft.cn/api/ai/mind_agent/skills/markdown_to_mindmap`
- 国际: `https://api.edrawmind.com/api/ai/mind_agent/skills/markdown_to_mindmap`

自动 TCP 探测选择最快节点，缓存 24 小时。也可用 `--region cn` 或 `--region global` 强制指定。

### 请求体格式

```json
{
  "text": "# AI\n## ML\n- Deep Learning",
  "layout_type": 1,
  "theme_style": 9,
  "background": "8",
  "line_hand_drawn": true,
  "fill_hand_drawm": "pencil"
}
```

注意：`fill_hand_drawm` 拼写（上游 API 的固有字段名，非笔误）。
