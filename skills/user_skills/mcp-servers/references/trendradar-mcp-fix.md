# TrendRadar MCP 修复记录

## 问题现象

TrendRadar MCP 连接失败，Hermes 无法拉起。直接运行 `trendradar-mcp.exe` 报错：

```
ImportError: cannot import name 'FastMCP' from 'fastmcp' (unknown location)
```

## 根因

`fastmcp==2.12.5` 包的 pip wheel 安装不完整，`site-packages/fastmcp/__init__.py` 文件缺失。同时 `uv sync` 覆盖了 pip 安装的包，导致包结构损坏。

## 修复命令

```bash
cd C:\Users\Admin\Developer\TrendRadar
.venv\Scripts\python.exe -m pip install --force-reinstall --no-deps fastmcp==2.12.5
```

关键参数：
- `--force-reinstall`：强制重新安装，覆盖损坏的文件
- `--no-deps`：只重装 fastmcp 本身，不升级依赖（避免破坏 TrendRadar 的依赖锁定）

## 验证

```bash
# 检查 __init__.py 是否存在
ls .venv\Lib\site-packages\fastmcp\__init__.py

# 直接运行 exe（应该保持运行，等待 MCP 协议输入）
.venv\Scripts\trendradar-mcp.exe
```

如果 exe 启动后保持运行（不立即报错），说明修复成功。

## 注意事项

- 不要用 `uv sync` 修复——uv 会锁死依赖版本，但它的包安装机制可能不完整
- pip 的 `--no-deps` 是关键：只重装目标包，不碰其他依赖
- 如果还有其他包也损坏了，重复此模式：`pip install --force-reinstall --no-deps <package>==<version>`