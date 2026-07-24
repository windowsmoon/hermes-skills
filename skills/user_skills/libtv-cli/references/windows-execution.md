# Windows 环境下的 LibTV CLI 执行要领

## 快速入口（必须先读）

> **本会话最重要的教训**：LibTV CLI 是 Windows 原生 `.exe`，在 Hermes `execute_code` 沙箱中运行时必须满足以下全部条件，缺一不可：
> 1. 使用**绝对路径** `C:/Users/Admin/.libtv/libtv.exe`
> 2. 传入**完整环境变量**（`env={**os.environ, "PATH": r"C:\Users\Admin\.libtv;" + os.environ.get("PATH", "")}`），否则 Windows 找不到依赖的 DLL
> 3. 用 `text=True` 读 stdout（CLI 输出是 UTF-8 JSON）
> 4. 错误诊断：先试 `--version`，再试 `--help`，确认进程能启动再走完整命令

## Hermes 沙箱环境的 PATH 陷阱

在 Hermes 的 `execute_code` 沙箱中执行 Windows 原生命令（如 `libtv.exe`、`curl.exe`）时，必须使用**绝对路径**，不要依赖 `PATH` 环境变量。沙箱进程的 PATH 通常不包含用户自定义目录（如 `C:\Users\Admin\.libtv`）。

### 正确做法

```python
import subprocess, os, json

libtv = r"C:\Users\Admin\.libtv\libtv.exe"
env = {k: v for k, v in os.environ.items()}
env["PATH"] = r"C:\Users\Admin\.libtv;" + env.get("PATH", "")

# ✅ 绝对路径 + 完整环境变量 + text=True
r = subprocess.run(
    [libtv, "--version"],
    capture_output=True, text=True,   # text=True 读取 UTF-8 JSON 输出
    env=env, timeout=15
)
print(r.stdout)

# ✅ 完整命令示例（node list）
r = subprocess.run(
    [libtv, "node", "list", "-p", "a412891277714b22b8f902e948c4af4a"],
    capture_output=True, text=True, env=env, timeout=20
)
data = json.loads(r.stdout)  # stdout 是 JSON

# ❌ 常见错误：
# 1. 只传 PATH 字符串不传完整 env → 找不到 Windows 系统 DLL
# 2. capture_output=True 但不传 env → PATH 里没有 C:\Users\Admin\.libtv
# 3. 不用 text=True 而读二进制 → JSON 解析失败
```

### 临时代替方案：用 subprocess.Popen + 线程监控

`libtv login web` 会启动一个本地 HTTP 回调服务器并**无限阻塞等待**，不能用 `subprocess.run()` 直接调用（会超时）。

用线程 + 非阻塞读取来监控输出：

```python
import subprocess, threading, os

output_lines = []
def run_login():
    proc = subprocess.Popen(
        ['C:/Users/Admin/.libtv/libtv.exe', 'login', 'web'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env={**os.environ, 'PATH': r'C:\Users\Admin\.libtv;' + os.environ.get('PATH', '')}
    )
    for line in proc.stdout:
        output_lines.append(line)
        print(line, end='')
    proc.wait()

t = threading.Thread(target=run_login, daemon=True)
t.start()
# 主线程继续监控 output_lines 中的 callback URL
```

### 在 Hermes 终端中直接运行

Hermes 内嵌终端（通过 `terminal` 工具）可以运行 `libtv` 命令，但当前会话出现过**所有终端命令返回同一段乱码**的损坏状态，此时切换到 `execute_code`（subprocess）是可靠的替代方案。

## 节点操作关键语法

- `libtv node <节点名或ID>` — 查询节点详情（**不是** `libtv node get <名>`，没有 `get` 子命令）
- 节点详情返回 JSON，含 `data.url`（图片数组）、`data.taskInfo`（taskId、status、progressPercent）
- status=2 表示生成成功，status=3 表示失败
- `libtv project use <uuid>` 会写入 `.libtv/project.json`，之后命令省略 `-p`

## 安装后验证

```bash
libtv --version          # 应输出 1.1.1
libtv --help             # 显示所有子命令
```

## 凭据文件位置

Windows：`%USERPROFILE%\.libtv\credentials.json`（即 `C:\Users\Admin\.libtv\credentials.json`）

## 关键常量（2026-07-07 确认）

| 常量 | 值 |
|------|----|
| CLI 版本 | 1.1.1 |
| 可执行文件 | `C:\Users\Admin\.libtv\libtv.exe` |
| 账号 | PMD_TV（至尊版VIP，accountId=3408792） |
| OpenAPI 默认项目 UUID | `a412891277714b22b8f902e948c4af4a` |
| OpenAPI 项目 workspaceId | `226356` |