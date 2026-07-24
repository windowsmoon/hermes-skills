# xhs-cli 在 Hermes Studio 环境中的安装

## 安装到 Hermes 运行时环境

xhs-cli 需要安装在 Hermes 的 bundled Python 环境下，才能被 Hermes Agent 直接调用。

### Bundled Python 路径

```
C:\Users\<user>\.hermes-web-ui\desktop-runtime\hermes\<version>\win-x64\python\python.exe
```

当前环境 (2026-07-17): `0.18.2`，全路径：
```
C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.2\win-x64\python\python.exe
```

### 安装命令

```bash
# 直接安装（需网络，已在 v0.1.4 验证通过，32 依赖 28s 完成）
uv pip install --python <bundled-python-path> xhs-cli

# 安装后会同时拉取 xiaohongshu-cli 依赖，将 xhs.exe 从 v0.1.4 升级到 v0.6.4
# xiaohongshu-cli 使用逆向工程 API，比原始 xhs-cli（camoufox 浏览器）更快
# 两个包共用同一个 xhs.exe 入口点

# 如果PyPI下载慢, 先下载wheel再本地安装
pip download xhs-cli -d D:\\hermes-data\\downloads
uv pip install --python <bundled-python-path> --no-index --find-links D:\\hermes-data\\downloads xhs-cli
```

### 验证安装

xhs.exe 会出现在 bundled Python 的 Scripts/ 目录下：

```
<bundled-python-dir>/Scripts/xhs.exe
```

验证命令（通过 execute_code 中的 Python subprocess，而非 terminal 工具——git-bash 可能有编码问题）：

```python
import subprocess, os
script_dir = os.path.join(os.path.dirname(python_path), "Scripts")
xhs_exe = os.path.join(script_dir, "xhs.exe")
result = subprocess.run([xhs_exe, "--help"], capture_output=True, text=True, timeout=30)
print(result.stdout[:500])
```

预期输出应显示 `xhs — Xiaohongshu CLI tool 🍰` 及命令列表。

## 调用方式

xhs.exe 不在系统 PATH 中（Hermes bundled Python Scripts 目录不自动加入 PATH），调用时必须使用完整路径：

```python
import subprocess
script_dir = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/python/Scripts")
xhs = os.path.join(script_dir, "xhs.exe")
# 例：搜索
result = subprocess.run([xhs, "search", "关键词", "--json"], capture_output=True, text=True, timeout=60)
print(result.stdout)
```

也可以先用 Hermes bundled Python 执行：`<python.exe> -m xhs_cli`（需确认包提供 `__main__.py`）。

## 首次使用

```bash
# 1. 登录 (自动提取Chrome cookies, 或QR码)
xhs login

# 2. 验证状态
xhs status
xhs whoami

# 3. 搜索
xhs search "关键词"
```

### QR 码登录与 Camoufox 问题

`xhs login --qrcode` 使用 Camoufox（反指纹 Firefox）展示 QR 码，但这需要先下载 492MB 的 Firefox 二进制包。

**常见失败**：GitHub 连接不稳定导致 `IncompleteRead`（下载 100-200MB 后断连），报错：
```
camoufox.exceptions.CamoufoxNotInstalled: official/stable is not installed.
```

**方案A：手动下载安装（已验证可行）**
从 GitHub Releases 手动下载 zip，放到 `~/.camoufox/`（不解压），然后运行：
```bash
python -m camoufox fetch
```
会自动检测 zip 并解压安装。SHA256 校验：`d5b83d1c419f4fdfcdea08428f82a34cd1f06f754388354d33c4ff64877cfb94`

安装后浏览器位于 `%LOCALAPPDATA%\camoufox\camoufox\Cache\browsers\...`，~934MB。之后 `xhs login --qrcode` 可直接弹出 QR 码窗口。

**方案B：Playwright Chromium 替代（Camoufox 不可用时）**
见 `references/camoufox-workaround.md` — 使用 Playwright Chromium 替代，脚本直接在桌面打开浏览器窗口显示 QR 码。

关键步骤：
1. 安装 Playwright Chromium: `python -m playwright install chromium`
2. 用 Playwright 脚本打开小红书登录页，截图 QR 码
3. 用户扫码后自动获取 cookie 并导入 xhs CLI

没有 Chrome/Edge 登录态时，browser-cookie3 可能返回空。此时只能用 QR 码登录。

## 已安装依赖（v0.1.4，32 包）

关键依赖：camoufox 0.5.4, playwright 1.60.0, browser-cookie3 0.20.1, lxml 6.1.1, numpy 2.5.1, orjson 3.11.9, pycryptodomex 3.23.0, rich-click 1.9.8

## 已知问题

- Hermes Studio 环境下 `uv tool install` 可能因 PATH 问题不可用，改用 `uv pip install --python <bundled-python-path>`
- camoufox 首次下载约需几十秒（下载 Firefox 浏览器二进制）
- 如果 `xhs.exe` 不在 PATH 中, 使用完整路径调用（见上）
- 通过 `execute_code` 中的 Python subprocess 调用比 `terminal` 工具更稳定（terminal 的 git-bash 可能输出二进制乱码）
