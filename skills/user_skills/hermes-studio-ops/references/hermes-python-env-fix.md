# Hermes Bundled Python 修复记录

## 问题

Hermes 自带两个 Python 版本：

| 目录 | 状态 | 说明 |
|------|:----:|------|
| `0.18.0/win-x64/python/` | ❌ 已删除 | 旧版，含完整 stdlib，Hindsight 装在此处 |
| `0.18.2/win-x64/python/` | ⚠️ 精简版 | 缺少 `Lib/encodings`、`DLLs/` 等 stdlib，无法 import 任何包 |
| `0.19.0/win-x64/python/` | ✅ 完整版 | 有完整 stdlib，可正常 pip install |

## 修复方法

### 方案 A：从 0.19.0 拷贝 stdlib 到 0.18.2（临时）
```python
import shutil
py019 = "~/.hermes-web-ui/desktop-runtime/hermes/0.19.0/win-x64/python"
py0182 = "~/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/python"
shutil.copytree(f"{py019}/Lib/encodings", f"{py0182}/Lib/encodings")
shutil.copytree(f"{py019}/DLLs", f"{py0182}/DLLs")
```
但 0.18.2 缺的模块不止这些（importlib, _bootsubsearcher 等），逐个补不完。

### 方案 B：设置 PYTHONHOME 环境变量（推荐）
```bash
set PYTHONHOME=C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.19.0\win-x64\python
```
这告诉 Python 解释器去哪里找 stdlib。设置后 0.18.2 的 python.exe 也能正常 import。

### 方案 C：直接使用 0.19.0 Python
Hermes 的 `execute_code` 沙箱实际使用 0.19.0 的 site-packages（通过 PYTHONPATH 注入）。可直接用 0.19.0 的 python.exe 运行 hindsight：
```python
python_019 = "~/.hermes-web-ui/desktop-runtime/hermes/0.19.0/win-x64/python/python.exe"
env = os.environ.copy()
env["PYTHONHOME"] = os.path.dirname(os.path.dirname(python_019))
# 然后 subprocess.run 即可
```

## Hindsight 关键信息

- **正确包名**：`hindsight-client`（不是 `hindsight`，那个是英国公司的测试工具）
- **当前版本**：0.8.4（2026-07-22 安装）
- **pip install**：`pip install hindsight-client`（无编译依赖，纯 Python）
- **安装位置**：0.19.0 Python 的 site-packages
- **插件位置**：`plugins/memory/hindsight/`（已被拷贝到 `~/.hermes/plugins/memory/hindsight/`）
- **配置**：`~/.hermes/hindsight/config.json`（mode=local_embedded, bank_id=hermes）
- **mode=local_embedded**：Hindsight 运行在 Hermes 进程内，不需要独立 daemon
- **mode=remote**：需要 hindsight 云服务 API key
- **限制**：Hermes 的 `memory` 工具有 10,000 字符硬编码上限，与 Hindsight 无关

## 验证命令

```python
# 验证 hindsight 可用
import hindsight_client
from hindsight_client import Hindsight

# 验证插件
from plugins.memory.hindsight import HindsightMemoryProvider
```
