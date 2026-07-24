---
name: mcp-servers
description: >-
  通用 MCP 服务器管理 — 在 Hermes 中安装、配置、测试、排错第三方 MCP 服务器。
  当用户需要安装新的 MCP 服务器（如 Apify / 其他 npx 或 uvx 依赖的 MCP），
  或现有 MCP 服务器连接失败需要排查时使用此 skill。
  不要用于：Hermes 内置 MCP（hermes-studio-* 系列）、已作为独立 skill 管理的 MCP（如 mijia-smart-home）。
  触发词：装 MCP、MCP 服务器、安装 XXX 的 MCP、mcp server 配置、MCP 连接失败
category: integrations
triggers:
  - 装 MCP
  - MCP 服务器
  - 安装 XXX 的 MCP
  - mcp server 配置
  - MCP 连接失败
tags:
  - mcp-servers
  - mcp

---

# MCP 服务器管理 — 安装 & 排错指南

## 通用安装流程

### 方式 CLI：hermes mcp add（推荐）

Hermes CLI 提供了交互式 MCP 安装命令，自动处理配置写入：

```bash
# 添加 MCP 服务器（自动写入 config.yaml）
hermes mcp add <server-name> --command <command> --args <args>

# 示例：添加本地的 Node.js MCP 服务器
hermes mcp add my-server \
  --command "C:\path\to\node.exe" \
  --args "D:\path\to\mcp-server\dist\index.js"

# 示例：添加 npx 包 MCP 服务器
hermes mcp add my-server --command npx --args "-y" "@npm/mcp-server"

# 删除 MCP 服务器
hermes mcp remove <server-name>
```

**交互提示**: `hermes mcp add` 连接后会提示 "Enable all N tools? [Y/n/select]:" — 默认选择 Y 启用所有工具。也可以直接用 `input('y\n')` 自动确认。

**注意**: 
- 添加后需要**重启 Hermes Desktop** 或开始新会话才能使用新 MCP 工具
- 当前会话不会自动加载新 MCP 工具
- 删除 MCP 不需要重启，即时生效

### 方式 A：npx 包（Node.js 生态）

### 方式 A：npx 包（Node.js 生态）
```yaml
mcp_servers:
  server-name:
    command: npx
    args:
      - "-y"
      - "@npm-package/mcp-server-name"
    env:
      SOME_API_TOKEN: "your-token-here"
    enabled: true
```

### 方式 B：uvx 包（Python 生态）
```yaml
mcp_servers:
  server-name:
    command: uvx
    args:
      - package-name
      - --optional-flag
    enabled: true
```

### 方式 C：本地 Node.js 脚本
```yaml
mcp_servers:
  server-name:
    command: <node.exe path>
    args:
      - /path/to/server.js
    enabled: true
```

## 配置文件位置

MCP 服务器的配置在：
- **主配置**: `C:\Users\<user>\AppData\Local\hermes\config.yaml`（security-sensitive，需用 `hermes config set` 修改）
- **用户级配置**: `~/.hermes/config.yaml`（可直接编辑，但覆盖范围不同）

推荐使用 `hermes config set mcp_servers.<name>.<key> <value>` 来修改。

## 安装后验证

```bash
# 列出所有 MCP 服务器及状态
hermes mcp list

# 测试单个 MCP 服务器连接
hermes mcp test <server-name>

# 预期输出：✓ Connected (Nms) + 工具列表
```

## 重启要求

MCP 服务器在 **Hermes 启动时加载**。中途修改 config.yaml 添加的 MCP 服务器：
- 可以通过 `hermes mcp test` 测试连接
- 但工具在当前会话中不会出现
- 需要**重启 Hermes Desktop 应用**才能让新 MCP 工具在对话中可用

## 常见排错

1. **Connection closed / 超时**
   - npx/uvx 需要首次下载包，确保网络连接
   - 预安装：`npm install -g <package>` 或 `uv tool install <package>`
   - 测试超时可适当增加 hermes mcp 的超时时间

2. **环境变量名称错误**
   - MCP 服务器文档中使用的环境变量名可能与实际不一致
   - 运行 MCP 服务器本身看错误输出：`npx <package>`（不通过 MCP）
   - 它会直接告诉你缺哪个环境变量

3. **Windows 特殊问题**
   - npx.cmd 是批处理文件，MCP 进程需要能解析 .cmd
   - Hermes 自带的 node 在 `~\\.hermes-web-ui\\desktop-runtime\\hermes\\<version>\\win-x64\\node\\`
   - 使用 `command: npx`（PATH 查找）比绝对路径更兼容

4. **Hermes 版本升级导致 Node 路径失效**
   - Hermes Desktop 自动升级（如 0.18.x → 0.19.x）后，旧版本的 node.exe 会被删除
   - 所有 MCP 配置中硬编码的老版本 node 路径都会失效
   - **诊断**：检查 `~/.hermes-web-ui/desktop-runtime/hermes/` 查看实际版本号
   - **修复**：更新 config.yaml 中所有 `hermes/0.18.x/` → `hermes/0.19.x/` 路径

5. **裸命令名（bare command）找不到**
   - npm 全局包安装后生成 `.cmd` 批处理文件，Hermes MCP 进程管理器直接 spawn 进程不通过 cmd.exe
   - **诊断**：`command` 字段是裸名字（如 `computer-control-mcp`）且非 `.exe` → 大概率有问题
   - **修复**：改为 `command: node` + `args: [完整路径到 dist/index.js]`
     ```yaml
     # ❌ 错误写法（.cmd 文件，Hermes 找不到）
     computer-control-mcp:
       command: computer-control-mcp
     # ✅ 正确写法
     computer-control-mcp:
       command: node
       args:
         - C:\Users\Admin\AppData\Roaming\npm\node_modules\computer-control-mcp\dist\index.js
     ```

6. **Python .venv 包损坏（缺少 __init__.py）**
   - 某些 Python 包的 pip wheel 可能安装不完整（如 `fastmcp==2.12.5`），报错 `ImportError: cannot import name 'FastMCP' from 'fastmcp' (unknown location)`
   - **诊断**：直接运行 `.exe` 看完整 traceback，检查 `site-packages/<package>/__init__.py` 是否存在
   - **修复**：`pip install --force-reinstall --no-deps <package>==<exact-version>`
   - 注意：`uv sync` 也可能导致已有包损坏，此时同样用 `pip install --force-reinstall --no-deps` 修复

## 参考文件

- `references/apify-mcp.md` — Apify MCP 安装 & 数据能力
- `references/trendradar-mcp-fix.md` — TrendRadar MCP 修复记录（fastmcp 包损坏修复）
