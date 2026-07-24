# 脚本使用指南

## batch_annotate.py

**路径**: `~/AppData/Local/hermes/skills/step-annotate/scripts/batch_annotate.py`
**依赖**: PIL/Pillow（Hermes 运行时自带，已在 uv venv 中预装）

### 功能

根据 `annotations.json` 批量给截图添加编号批注（红框+箭头+编号圆+说明文字）。

### 调用方式（在 Hermes Agent 中）

```python
from hermes_tools import execute_code

code = '''
import subprocess, json, os

script = os.path.expanduser(
    "~/AppData/Local/hermes/skills/step-annotate/scripts/batch_annotate.py"
)
config = "/tmp/annotations.json"
subprocess.run(["python", script, config], check=True)
'''
```

或者直接用 terminal：

```bash
python ~/AppData/Local/hermes/skills/step-annotate/scripts/batch_annotate.py /tmp/annotations.json
```

这里的 `python` 使用 Hermes 运行时自带的 Python（3.12，Pillow 已预装）。

### 配置文件 fields 说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `number` | int | 是 | 编号，全局递增 |
| `text` | str | 是 | 标注显示的文字 |
| `x, y` | int | 是 | 目标框左上角坐标（像素） |
| `width, height` | int | 是 | 目标框尺寸（像素） |
| `output_name` | str | 否 | 输出文件名（不含路径），不指定则自动生成 |
| `style` | object | 否 | 单标注独立的样式覆盖 |

全局样式（外层 `style`）：

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `box_color` | [255, 69, 0] | 框和文字颜色（橙色） |
| `box_width` | 3 | 框线宽度 |
| `arrow_color` | [255, 69, 0] | 箭头颜色 |
| `font_size` | 16 | 字体大小 |
| `number_bg_color` | [255, 69, 0] | 编号圆背景色 |
| `number_fg_color` | [255, 255, 255] | 编号文字颜色 |

### 输出

脚本会在每张图片所在目录下创建 `标注完成/` 子目录，放入带批注的副本。
文件名优先用 `output_name`，否则自动拼接 `步骤<编号>-<首个标注文字>.png`。

### 注意事项

- 所有图片路径必须是绝对路径（脚本从系统路径运行）
- 使用 `os.path.expanduser()` 解析 `~` 路径
- 坐标确保不超出图片尺寸范围
- font 自动检测：微软雅黑 > 宋体 > 黑体 > 默认
