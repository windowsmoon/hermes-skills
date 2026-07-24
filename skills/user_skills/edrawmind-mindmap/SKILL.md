---
name: edrawmind-mindmap
description: >
  当用户需要edrawmind-mindmap时使用。
  不要用于：无关场景。
  触发词：思维导图、脑图、mindmap、整理思路
tags:
  - mindmap
  - 思维导图
  - 脑图
  - edrawmind
  - mindmaster
  - 万兴脑图
  - 亿图脑图
related_skills:
  - markdown-viewer
  - douyin-video-pipeline
thread_control: roll
triggers:
  - 思维导图
  - 脑图
  - mindmap
  - 整理思路

--- 

# EdrawMind（万兴脑图）思维导图生成 Skill

## 功能描述

通过 EdrawMind HTTP API 将自然语言主题或已有 Markdown 文档转化为专业思维导图。支持 12 种布局、10 种主题、15 种背景、手绘风格。

> ⚠️ EdrawMind = 原 MindMaster（亿图脑图），万兴科技旗下产品

**两种调用方式（二选一）：**

| 方式 | 特点 | 适用场景 |
|------|------|---------|
| 🥇 **直接 API 调用**（推荐） | 零依赖，纯 Python 标准库，无需下载脚本 | 集成到 pipeline/skill，快速出图 |
| 🥈 **CLI 脚本** | 完整的命令行界面，支持文件/stdin/--text 输入 | 手工调试，复杂参数组合 |

详见 `references/api-direct-call.md`（API 方式）和 `references/download-cli.md`（CLI 方式）。

## 触发条件

- 用户说：「生成思维导图」「脑图」「mindmap」「导图」
- 用户说：「把 XX 做成思维导图」「画个图」「可视化大纲」
- 用户描述的结构化内容需要树状图呈现
- pipeline 中 Step 2 分析完成后需要渲染思维导图（见 `douyin-video-pipeline` skill）

## 前置条件

### 无需 API Key（推广期免费）

当前推广期免费使用，API Key 可选（通过 `X-API-Key` header 或 `--api-key` 参数）。国内自动路由到 `mindapi.edrawsoft.cn`，国际到 `api.edrawmind.com`。

### 输入格式要求

输入必须是**结构良好的 Markdown**，使用标题层级表示树状结构：

- `#` → 根节点（中心主题），建议仅一个
- `##` → 一级分支、`###` → 二级分支，以此类推
- `-`/`*`/`+`/`1.` 列表项 → 子节点，缩进列表项 → 更深层子节点
- 必须包含至少一个标题和至少一个列表项
- 节点文字简洁（中文 3-10 字，英文 3-5 词），去除编号前缀
- 建议最大深度 5 层，最大节点数约 150 个

详细格式规范参见 `references/markdown-format.md`。

---

# Edrawmind Mindmap

## Step 1 - 准备 Markdown 内容

两种方式：

### A. 从已有内容转换（推荐）

将树状结构转为 Markdown：

```markdown
# 项目架构
## 前端
- React
- TypeScript
- Tailwind
## 后端
- Python
- FastAPI
- PostgreSQL
## 部署
- Docker
- K8s
```

### B. 根据用户描述起草

如果用户只说了主题（如「帮我生成一张 Loop Engineering 的思维导图」），先起草一个大纲 Markdown，展示给用户确认，再调用 API。

---

## Step 2 - 选择布局类型（layout_type）

根据内容特点选择最合适的布局（1–12），默认 `1`（MindMap 双向导图）。

**智能推断：**
- 含"原因/影响/根因/分析" → `8`（鱼骨图）
- 含"时间/进度/计划/里程碑/路线图" → `7`（时间轴）
- 含"组织/部门/团队/人员架构" → `5`（向下组织结构图）
- 含"分类/体系/全景/层级" → `4`（向下对称树状图）
- 含"对比/矩阵/SWOT" → `12`（矩阵图）
- 含"对比表/需求/功能清单" → `11`（树型表格）
- 含"清单/目录/大纲/列举" → `10`（括号图）
- 含"演示/发散/放射/展示" → `9`（扇形放射图）
- 其他/未指定 → `1`（MindMap）

完整列表：
| # | 名称 | 适用场景 |
|---|------|---------|
| 1 | 双向导图 (MindMap) | 默认、发散思维 |
| 2 | 右向导图 (RightMap) | 单侧展开 |
| 3 | 右下树状图 (RightTree) | 项目分解 |
| 4 | 向下对称树状图 (DownTree) | 分类体系 |
| 5 | 向下组织结构图 (OrgDown) | 组织架构 |
| 6 | 向上组织结构图 (OrgTop) | 报告/汇总 |
| 7 | 向右时间轴 (TimelineRight) | 时间线/路线图 |
| 8 | 右向鱼骨图 (FishboneRight) | 根因分析 |
| 9 | 扇形放射图 (Sector) | 展示/发散 |
| 10 | 右向括号图 (BracketRight) | 大纲/列举 |
| 11 | 树型表格 (TreeTable) | 需求/功能清单 |
| 12 | 矩阵图 (Matrix) | 对比/SWOT |

各布局视觉效果详见 `references/style-guide.md`。

---

## Step 3 - 选择主题风格（theme_style）

传入 `1`–`10`，默认不传则保持导入时原始主题。

**智能推断：**
- "学习/笔记/知识/教育" → `2`
- "创意/活力/时尚/产品" → `3`
- "商务/汇报/正式/简洁" → `4`
- "头脑风暴/彩虹/活泼" → `5`
- "文档/报告/打印/素雅" → `6`
- "生活/旅游/健康/自然" → `7`
- "暗色/夜间/深色" → `8`
- "科技/霓虹/赛博/炫酷" → `9`
- "科幻/IT/架构/安全/暗黑" → `10`
- 未指定 → `1`

---

## Step 4 - 选择画布背景（background）

传入预设编号 `1`–`15` 或自定义 `"#RRGGBB"`（默认无背景）。

**快速推断：**
- "极简/打印/正式" → `2`
- "温馨/商务" → `3`
- "科技/分析" → `4` 或 `11`
- "自然/清新" → `5`
- "文艺/创意" → `6`
- "暗色主题" → `7`/`8`/`14`/`15`
- "复古/手绘感" → `9`
- 品牌色 → 直接传 `"#RRGGBB"`

---

## Step 5 - 选择手绘风格（可选）

两个独立参数：

**`--line-hand-drawn`** — 连线手绘：所有连线变为手绘弯曲风格
**`--fill STYLE`** — 节点填充：`none` / `pencil` / `watercolor` / `charcoal` / `paint` / `graffiti`

**注意：手绘风格影响渲染性能，建议节点数 ≤ 50。** 

**组合推荐：**
- 手绘素描 → `--line-hand-drawn --fill pencil --background 9`
- 水彩 → `--line-hand-drawn --fill watercolor` + 浅色背景
- 炭笔 → `--line-hand-drawn --fill charcoal --background 10`
- 涂鸦 → `--line-hand-drawn --fill graffiti` + 深色背景

---

## Step 6a - 直接 API 调用（推荐，适合 pipeline 集成）

零依赖，只使用 Python 标准库。详见 `references/api-direct-call.md`。

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

成功响应包含 `file_url`（在线编辑链接，必须展示给用户）和 `thumbnail_url`（缩略图预览）。

---

## Step 6b (备选) - 执行 CLI 生成思维导图

> 此方式需要先下载 `scripts/edrawmind_cli.py`，见 `references/download-cli.md`。

### 从文件生成

```python
from hermes_tools import terminal

result = terminal(
    "python scripts/edrawmind_cli.py input.md --layout 1 --theme 9 --background 8",
    timeout=120,
    workdir="<skill_dir>"
)
print(result["output"])
```

### 从文本直接生成

```python
from hermes_tools import terminal

md_content = "# AI学习路线\\n## 基础\\n- Python\\n## 进阶\\n- 深度学习"

result = terminal(
    f'python scripts/edrawmind_cli.py --text "{md_content}" --layout 7 --theme 3',
    timeout=120,
    workdir="<skill_dir>"
)
```

### 参数速查

| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | 路径 | Markdown 文件路径，`-` = stdin |
| `--text` | 字符串 | 内联 Markdown，\\n 换行 |
| `-l / --layout` | 1-12 | 布局类型 |
| `-t / --theme` | 1-10 | 主题风格 |
| `-b / --background` | 1-15 / #RRGGBB | 背景 |
| `--line-hand-drawn` | flag | 手绘连线 |
| `--fill` | 枚举 | 节点填充手绘 |
| `--api-key` | 字符串 | 可选 API Key |
| `--region` | auto/cn/global | API 区域 |
| `-q / --quiet` | flag | 只输出 URL |
| `--open` | flag | 浏览器打开 |
| `--json` | flag | 输出完整 JSON |
| `-o / --output` | 路径 | 保存 JSON |

**必须将 `file_url` 展示给用户**——这是一个可在线编辑的链接。

---

## 常见问题

**Q: 需要付费吗？**
A: 当前推广期免费使用，无需 API Key。

**Q: 支持哪些输出格式？**
A: 返回在线编辑链接和缩略图，用户可直接在浏览器打开并导出为 .emmx / PNG / PDF / SVG 等。

**Q: 内容太长会不会失败？**
A: 建议最大节点数约 150 个，超大文档按章节拆分生成多个思维导图。

**Q: 断网时能用吗？**
A: 不能，需要访问 EdrawMind API 云端渲染。

---

## 备用方案：Mermaid CLI（本地离线）

当 EdrawMind API 不可用或用户需要离线生成时，使用本地 mmdc：

```bash
# 生成 Mermaid mindmap 文件
cat > mindmap.mmd << 'EOF'
mindmap
  root((主题))
    分支1
      内容A
EOF

# 渲染为 PNG
"C:\Users\Admin\AppData\Roaming\npm\mmdc.cmd" -i mindmap.mmd -o output.png -b black -w 1200 -H 900
```

详见 `douyin-video-pipeline` skill 中的 Mermaid 渲染章节。

---

## 已知限制

1. API 依赖网络，国内用户自动路由到 `mindapi.edrawsoft.cn`，国际用户到 `api.edrawmind.com`
2. 手绘风格（`--fill`）在节点数 > 50 时渲染变慢，超过时建议使用非手绘风格
3. 输入必须包含至少一个标题（`#`）和一个列表项（`-`），否则 API 返回验证错误
4. file_url 是临时编辑链接，建议用户及时保存到自己的 EdrawMind 账号
