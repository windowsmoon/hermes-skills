# real-browser-mcp Windows 故障排查

## 已知问题：端口 7225 被旧进程占用（EADDRINUSE）

### 症状
- real-browser-mcp MCP 服务器反复启动失败
- 日志显示 `EADDRINUSE: address already in use 127.0.0.1:7225`
- Edge 扩展显示绿色（已连接），但 Hermes 工具列表里没有 real-browser 的 22 个工具
- 日志：`MCP server 'real-browser' failed initial connection after 3 attempts, giving up`
- 最终：`MCP: registered 0 tool(s) from 0 server(s) (1 failed)`

### 根因
bridge.js 的 `killStaleProcess()` 函数使用 `lsof -ti :7225 -sTCP:LISTEN` 命令来检测并杀掉旧进程。**`lsof` 是 Linux/macOS 命令，Windows 上没有**，所以 kill 操作静默失败，旧进程一直占用端口 7225，新实例无法绑定。

### 修复步骤

**方法一：手动杀进程（推荐，无需重启 Hermes）**
```powershell
# 1. 找到占用 7225 端口的进程 PID
Get-NetTCPConnection -LocalPort 7225 | Select-Object -ExpandProperty OwningProcess

# 2. 杀掉该进程
Stop-Process -Id <PID> -Force

# 3. 验证端口已释放
Get-NetTCPConnection -LocalPort 7225 -ErrorAction SilentlyContinue
```

**方法二：重启 Hermes Desktop**
关闭 Hermes Studio → 重新打开，Hermes 会重新启动 real-browser-mcp 并成功绑定到 7225 端口。

### 验证修复
1. 检查端口是否可用：`Get-NetTCPConnection -LocalPort 7225 -ErrorAction SilentlyContinue`（无输出 = 可用）
2. 在 Hermes 开新会话，检查是否有 real-browser 工具加载
3. 浏览器扩展应显示绿色（断开后自动重连）

### 注意事项
- 杀掉 7225 进程后，Edge 扩展会短暂断开，然后自动重连到新 MCP 实例
- Hermes 在当前会话生命周期内不会重试 MCP 连接——**必须开新会话**
- 如果重启 Hermes 后仍失败，检查任务管理器是否有残留 node 进程（`C:\Users\Admin\.hermes-web-ui\...\node.exe`）

## 长期修复建议
给 real-browser-mcp 提 PR，将 `killStaleProcess()` 改为跨平台兼容：
```python
# Windows 替代方案（netstat 代替 lsof）
netstat -ano | findstr :7225
```