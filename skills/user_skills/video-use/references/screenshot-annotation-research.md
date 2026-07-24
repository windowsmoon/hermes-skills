# 截图批注工具调研结论

> 为 AI 教程内容创作者寻找"批量截图编号批注 + Agent 可调用"工具的调研结果。

## 调研范围

覆盖以下渠道，寻找能**批量**给已有截图加**编号标记/箭头/文字**、且能被 Agent（CLI/API/MCP/Hermes Plugin/Hermes Skill）集成的工具：

| 渠道 | 结果 |
|------|------|
| Hermes 插件市场 | 无截图批注相关插件 |
| MCP 官方服务器 | 7 个官方 MCP Server，无图片处理类 |
| GitHub 开源项目（StepMark, Instrata, screensnap 等） | 均为交互式 GUI，无批量/无 API |
| 社区 MCP 服务器 | 未发现图片批注类 |
| PyPI | 无截图批注 CLI 包（已验证） |

## 已评估工具清单

| 项目 | 类型 | 能否批量批注？ | 能否被 Agent 调用？ |
|------|------|:--------------:|:-------------------:|
| **StepMark** | Windows 桌面 GUI（Tauri + React） | ❌ 一张一张手动 | ❌ 纯 GUI，无 CLI/API |
| **Instrata** | Windows 桌面 GUI（Tauri + Vue） | ❌ 同上手动 | ❌ 无 CLI/API |
| **screensnap** | 在线 HTML 网页工具 | ❌ 浏览器手动 | ❌ 无 API |
| **marker-helper** | Chrome 扩展 | ❌ 只对网页 DOM 有效 | ❌ 无法处理本地截图 |
| **screen-activity-doc-generator** | Python GUI | ❌ 手动操作 | ❌ 无 API |

## 结论

**不存在**能同时满足"批量截图编号批注 + Agent 可调用"这两个条件的现成开源工具。

## 推荐方案

自行编写 Python CLI 脚本，用 Pillow 在截图上绘制编号标记：

```python
# batch_annotate.py 核心逻辑（Pillow 实现）
from PIL import Image, ImageDraw, ImageFont

def annotate_image(image_path, markers, output_path):
    """在图片上绘制编号标注。
    
    markers = [
        {"x": 150, "y": 80, "text": "点击这里", "number": 1, "color": "red"},
        {"x": 400, "y": 200, "text": "选择模型", "number": 2, "color": "blue"},
    ]
    """
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    # Pillow 绘图逻辑：画圆圈编号 + 箭头 + 文字标签
    # ...
    img.save(output_path)
```

这个脚本：
- **可以被 Agent 直接调用**（`execute_code` 或 `terminal` 运行）
- **支持批量**（遍历文件夹）
- **内容可定义**（通过 JSON 配置文件指定每个标记的位置、编号、文字）
- **未来可扩展为 Hermes Skill**（注册到 skills/ 目录即可）

## 使用方式

```bash
# 单文件
python batch_annotate.py --input screenshot.png --output output.png --markers '[
  {"x":150,"y":80,"text":"打开 ComfyUI","number":1},
  {"x":400,"y":200,"text":"加载模型","number":2}
]'

# 批量文件夹
python batch_annotate.py --input ./screenshots/ --output ./annotated/ --config annotations.json
```

## 可选集成路径（成本递增）

1. **Python CLI 脚本**（即刻可用）- 用 `execute_code` 或 `terminal` 调用
2. **Hermes Skill**（30 分钟封装）- 注册 skill，通过自然语言触发
3. **MCP Server**（半天开发）- 通过 MCP 协议暴露工具给任意 Agent
4. **桌面 GUI 版**（已有 StepMark 等）- 但需要手动操作

当前建议走方案 1 或 2，对教程制作效率提升最直接。
