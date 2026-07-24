# 外部 CLI/MCP 工具集成模式

## 通用安装流程

```
1. 确定工具类型
   ├─ npm 包 → npm install -g <package>
   ├─ pip 包 → uv pip install <package>
   ├─ GitHub 项目 → git clone / 下载zip + npm install
   └─ MCP Server → 注册到 Hermes Studio /api/hermes/mcp/servers

2. 配置认证
   ├─ OAuth → 运行 auth login，捕获 URL 给用户扫码
   ├─ API Key → 从已有 provider 取或用用户提供的
   └─ Cookie → 浏览器提取或程序化提取

3. 注册为 Hermes Skill（如果是独立能力）
   skill_manage action=create

4. 注册为 MCP Server（如果是 MCP 服务）
   POST /api/hermes/mcp/servers {name, config: {command, args, env}}
```

## 本 Skill 集成的工具

| 工具 | 方式 | 通讯协议 |
|------|------|---------|
| OpenCode | npm 全局安装 | CLI 标准输出（不走 ACP） |

## 常见问题

- **npm 包 404** → 可能发布在内部 registry，换 pip/Python 脚本替代
- **MCP Server 启动不了** → 检查 env 变量、路径是否正确
- **终端输出乱码** → 改用 Python subprocess 代替 terminal tool 捕获输出
- **OpenCode 是 TUI 模式** → 用 terminal(pty=true) 配合，或通过 ACP 服务器模式（仅用于 Paseo 编排）