# mijia-smart-home 实操参考

2026-07-18 会话记录，首次集成 mijiaAPI v4.1.3 到 Hermes

## 安装验证

```bash
uv tool install mijiaAPI
uvx mijiaAPI --help
# 会看到: Mijia API CLI (v4.1.3)
```

uv tool list 确认：
```
mijiaapi v4.1.3
- mijiaAPI
```

## 二维码登录流程（Windows 终端编码问题应对）

由于 Hermes git-bash/MSYS 终端输出有编码问题（ 乱码），不能直接用 terminal 看二维码。

### 方法 1：后台 terminal + 重定向到文件

```bash
# 在后台运行，输出到文件
terminal(background=True, command="uvx mijiaAPI login > /c/Users/Admin/AppData/Local/Temp/mijia_login_output.txt 2>&1")

# 然后读文件
execute_code: open("C:/Users/Admin/AppData/Local/Temp/mijia_login_output.txt").read()
```

输出中包含：
```
也可以访问链接查看二维码图片: https://account.xiaomi.com/pass/qr/login?ticket=lp_...
```

### 方法 2：execute_code 用 subprocess.PIPE

```python
import subprocess, time
proc = subprocess.Popen(
    ["uvx", "mijiaAPI", "login"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)
time.sleep(3)
proc.kill()  # 杀掉进程（它在等扫码，不会自己退出）
# 输出包含 QR 图片 URL
```

### 下载并展示二维码

```python
import urllib.request
url = "https://account.xiaomi.com/pass/qr/login?ticket=..."
img_path = "/tmp/mijia_qr_login.png"
urllib.request.urlretrieve(url, img_path)
# 然后用 Markdown 展示
```

## Hermes Studio API 添加 MCP Server

### 查看已有 MCP Server

```python
GET /api/hermes/mcp/servers
```

### 添加 mijia-api MCP Server

⚠️ **关键**：API 需要 `name` + 嵌套 `config`，不是平铺字段。检查 Hermes Studio mcp.js 源码发现 `addServer` handler 会校验 body 必须存在 `name` 和 `config` 字段。

```python
POST /api/hermes/mcp/servers
{
  "name": "mijia-api",
  "config": {
    "command": "uvx",
    "args": ["mijiaAPI", "mcp"],
    "enabled": true
  }
}
```

错误示例（会返回 400）：
```python
# ❌ 缺少 name → "Valid server name is required"
{ "command": "uvx", "args": ["mijiaAPI", "mcp"], "enabled": true }
# ❌ 缺少嵌套 config → "config object is required"
{ "name": "mijia-api", "command": "uvx", "args": ["mijiaAPI", "mcp"], "enabled": true }
```

**重载 MCP**：MCP server 添加后通常自动连接。如需重载：`POST /api/hermes/mcp/reload`（注意：reload 可能超时 300s，不影响已添加的 server，超时后新会话即可使用新工具）。

## MCP Server login 工具

MCP server 内置的 login 工具会：
1. 先尝试刷新已有 token
2. 失败则生成二维码，在后台线程长轮询等待扫码
3. 返回 QR 图片 URL
4. 用户扫码后调用 login_status 查结果

返回格式：
```json
{
  "status": "pending" | "success" | "error",
  "message": "..."
}
```

## 项目文件位置（uv tool）

```
C:\Users\Admin\AppData\Roaming\uv\tools\mijiaapi\Lib\site-packages\mijiaAPI\
├── __init__.py
├── __main__.py        # CLI 入口
├── apis.py            # 核心 API（mijiaAPI 类、QRlogin、_get_qr_login_data）
├── devices.py         # 设备封装
├── errors.py          # 异常定义
├── logger.py
├── mcp_server.py      # MCP Server 实现（login/login_status 工具定义）
├── miutils.py         # 加密/签名工具
└── version.py

认证文件：~/.config/mijia-api/auth.json
CLI 入口：~/.local/bin/mijiaAPI.exe
```

## 关键发现 1：`qr` 字段不一定可用

**不要依赖 `login_data['qr']` 字段**。这个字段是小米服务器返回的一个二维码图片链接，但实测它可能为空/None，导致 CLI 不会输出 "也可以访问链接查看二维码图片" 这句话。

**可靠做法**：从 `login_data['loginUrl']` 本地生成二维码。

```python
from qrcode import QRCode
qr = QRCode(border=2, box_size=10)
qr.add_data(login_data["loginUrl"])
img = qr.make_image(fill_color="black", back_color="white")
img.save("mijia_qr_login.png")
```

## 关键发现 2：长轮询必须保持运行

`_complete_qr_login()` 是一个阻塞的长轮询调用（等待 120 秒超时）。如果杀掉这个进程，扫码后也不会完成登录。

**正确流程**：

```python
# 1. 获取登录数据 + 生成二维码
api = mijiaAPI(...)
data = api._get_qr_login_data()

# 2. 本地生成二维码图片展示给用户
img_path = generate_qr(data["loginUrl"])

# 3. 保持进程存活，等待用户扫码
# 这个必须在后台线程或独立的子进程中运行
result = api._complete_qr_login(data)  # 阻塞
```

## 关键发现 3：从 UV 工具包导入到 Python 脚本

`uv tool install` 把包装在独立环境里，不在标准 Python sys.path 中。必须手动添加：

```python
# Windows:
sys.path.insert(0, r"C:\Users\Admin\AppData\Roaming\uv\tools\mijiaapi\Lib\site-packages")

# 通用写法：
import os
site = os.path.expanduser("~/AppData/Roaming/uv/tools/mijiaapi/Lib/site-packages")
sys.path.insert(0, site)
```

## 用户偏好：失败时简单重试

当二维码过期或 CLI 输出异常时，**直接重新执行一次完整的登录流程**。不要深入排查失败原因、不要分析堆栈——简单重试即可。（用户原话："重新做一遍而已啊"）
```
QRlogin() → _get_qr_login_data() → 刷新token尝试 → 生成二维码 → _print_qr(loginUrl) → _complete_qr_login()
_get_qr_login_data() 返回 login_data 含: loginUrl（二维码原始链接）, qr（二维码图片URL）, lp（长轮询地址）
```

### MCP login 工具 (mcp_server.py)
```
@mcp.tool login():
  1. 检查 _api 是否可用，尝试刷新
  2. 创建新 api → _get_qr_login_data()
  3. 若 refreshed: 返回 "Token 刷新成功"
  4. 否则: 后台线程 _login_worker → 返回 QR 图片 URL
  return "二维码图片链接: {login_data['qr']}"
```