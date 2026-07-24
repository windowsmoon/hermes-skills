# EdrawMind API 直接调用（推荐）

不需要下载 `edrawmind_cli.py`，直接用 Python 标准库 `urllib` + `json` 就能调用 EdrawMind API。
零依赖，适合集成到 pipeline 和其他 skill 中。

## API 信息

| 项目 | 值 |
|------|-----|
| 国内端点 | `https://mindapi.edrawsoft.cn/api/ai/mind_agent/skills/markdown_to_mindmap` |
| 国际端点 | `https://api.edrawmind.com/api/ai/mind_agent/skills/markdown_to_mindmap` |
| 方法 | POST |
| Content-Type | `application/json` |
| 认证 | 可选（`X-API-Key` header），推广期免费 |
| 响应时间 | ~700ms |
| 超时建议 | 30s |

## 请求体

```json
{
  "text": "# Markdown 内容\n## 分支\n- 子项",
  "layout_type": 1,
  "theme_style": 1,
  "background": "1"
}
```

## 响应体

```json
{
  "code": 0,
  "msg": "code-0",
  "data": {
    "file_url": "https://mm.edrawsoft.cn/app/editor/...",
    "thumbnail_url": "https://edrawmind-private.oss-cn-shenzhen.aliyuncs.com/...",
    "extra_info": {
      "request_id": "ecbf07d4...",
      "elapsed_ms": 696
    }
  }
}
```

- `file_url`：在线编辑链接（用户可打开修改、导出 .emmx/PNG/PDF/SVG）
- `thumbnail_url`：阿里云 OSS 缩略图 JPEG（约 70-90KB），有时效性

## 调用代码

### 基础调用（生成 + 下载缩略图）

```python
import urllib.request, json, os, time

EDRAW_API = "https://mindapi.edrawsoft.cn/api/ai/mind_agent/skills/markdown_to_mindmap"

def render_mindmap(markdown_text, layout=1, theme=1, output_path=None):
    if not output_path:
        output_path = f"/tmp/edrawmind_{int(time.time())}.jpg"
    
    body = {"text": markdown_text, "layout_type": layout, "theme_style": theme}
    req = urllib.request.Request(
        EDRAW_API,
        data=json.dumps(body, ensure_ascii=False).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        if result.get("code") != 0:
            return ""
        thumb_url = result["data"]["thumbnail_url"]
        with urllib.request.urlopen(thumb_url, timeout=30) as img_resp:
            img_data = img_resp.read()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(img_data)
        return output_path
    except Exception:
        return ""
```

### 集成到飞书上传（pipeline 场景）

```python
img_path = render_mindmap(md_content)
if img_path:
    # 上传到飞书
    import subprocess
    result = subprocess.run(
        ["lark-cli", "drive", "+upload", "--file", img_path],
        capture_output=True, text=True, timeout=30
    )
    # 获取 drive_url 嵌入文档
```

## 布局类型速查

| # | 名称 | 适用场景 |
|---|------|---------|
| 1 | 双向导图 | 默认/发散思维 |
| 2 | 右向导图 | 单侧展开 |
| 3 | 右下树状图 | 项目分解 |
| 4 | 向下对称树状图 | 分类体系 |
| 5 | 向下组织结构图 | 组织架构 |
| 6 | 向上组织结构图 | 报告/汇总 |
| 7 | 向右时间轴 | 时间线/路线图 |
| 8 | 右向鱼骨图 | 根因分析 |
| 9 | 扇形放射图 | 展示/发散 |
| 10 | 右向括号图 | 大纲/列举 |
| 11 | 树型表格 | 需求/功能清单 |
| 12 | 矩阵图 | 对比/SWOT |

## 主题风格速查

| # | 风格 | 适用场景 |
|---|------|---------|
| 1 | 默认 | 通用 |
| 2 | 知识 | 学习/笔记/知识/教育 |
| 3 | 活力 | 创意/时尚/产品 |
| 4 | 简洁 | 商务/汇报/正式 |
| 5 | 彩虹 | 头脑风暴/活泼 |
| 6 | 素雅 | 文档/报告/打印 |
| 7 | 自然 | 生活/旅游/健康 |
| 8 | 暗色 | 夜间/深色 |
| 9 | 赛博 | 科技/霓虹/炫酷 |
| 10 | 暗黑科技 | 科幻/IT/架构/安全 |

## 注意事项

1. **缩略图有时效性**：OSS URL 含 Expires 参数，建议下载到本地后使用
2. **无需 API Key**：推广期免费，直接调用即可
3. **Markdown 要求**：必须包含至少一个 `#` 标题和至少一个 `-` 列表项
4. **最大节点建议**：约 150 个节点，超大文档按章节拆分
5. **手绘风格影响性能**：节点 > 50 时变慢
6. **网络要求**：需要联网访问云端 API
