# TorchVision 兼容性补丁备忘录

## 问题

`basicsr` 1.4.2 在 torchvision 0.23.0+ 下导入失败，报错：

```
ModuleNotFoundError: No module named 'torchvision.transforms.functional_tensor'
```

## 原因

torchvision 0.23.0 移除了 `functional_tensor` 子模块，将其功能合并到 `torchvision.transforms.functional` 中。basicsr 的 `data/degradations.py` 仍引用旧的导入路径。

## 修复方法

```python
# 找到 basicsr 安装位置
# 一般在 python/Lib/site-packages/basicsr/data/degradations.py

# 将第8行:
from torchvision.transforms.functional_tensor import rgb_to_grayscale

# 改为:
from torchvision.transforms.functional import rgb_to_grayscale
```

## 自动修复

```python
import os, subprocess

# 找到 basicsr 位置
result = subprocess.run([sys.executable, "-m", "pip", "show", "basicsr"],
                       capture_output=True, text=True)
loc = None
for line in result.stdout.split("\n"):
    if line.startswith("Location:"):
        loc = line[len("Location:"):].strip()
        break

if loc:
    filepath = os.path.join(loc, "basicsr", "data", "degradations.py")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(
        "from torchvision.transforms.functional_tensor import rgb_to_grayscale",
        "from torchvision.transforms.functional import rgb_to_grayscale"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched!")
```

## 触发条件

安装 GFPGAN 或 Real-ESRGAN 时，如果 `pip install` 失败（basicsr 依赖解决超时），使用 `pip install --no-deps` 分别安装 basicsr、gfpgan、realesrgan，然后打此补丁。

## 依赖版本

| 包 | 测试版本 |
|---|---------|
| basicsr | 1.4.2 |
| torch | 2.8.0+cpu |
| torchvision | 0.23.0 |
| gfpgan | 1.3.8 |
| realesrgan | 0.3.0 |