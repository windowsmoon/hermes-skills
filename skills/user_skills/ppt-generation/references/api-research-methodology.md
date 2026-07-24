# 国内AI工具API调研方法（会话经验沉淀）

## 不要止步于"无公开API"

当用户问一个工具能否被Agent调用时，至少检查以下4层：

### 第1层：官方文档
- `工具名 + api` 官网搜索
- `工具名 + developer` / `工具名 + open-platform`
- 例：Gamma → `developers.gamma.app`（有官方API v1.0）
- 例：文多多AiPPT → `docmee.cn/open-platform`（有REST API + SDK）

### 第2层：GitHub生态
- `工具名 + mcp`（MCP服务器）
- `工具名 + cli`（命令行工具）
- `工具名 + sdk` 或 `工具名 + python`（SDK封装）
- `工具名 + skill`（AI Agent技能）
- 例：讯飞智文 → `aippt-mcp`（MCP服务器，⭐8）
- 例：Gamma → `gamma-app-mcp`（PyPI包）
- 例：AiPPT → `docmee/aippt-api-python-demo`（⭐32）

### 第3层：npm/PyPI
- `npm search 工具名`
- `pip search 工具名`
- 例：ChatPPT → `@yooai/cli`（npm）

### 第4层：第三方封装/社区项目
- 搜索 `工具名 + api + golang/java/go` 等跨语言SDK
- 检查工具网页的Network请求，有时有未文档化的API

## 已验证的工具API清单

| 工具 | 集成方式 | 状态 |
|------|---------|------|
| Gamma.app | MCP (`gamma-app-mcp`) + Python SDK + Skill | ✅ 需Pro套餐 |
| 讯飞智文 | MCP (`aippt-mcp`) | ✅ 免费 |
| 文多多AiPPT | REST API + SDK (Python/Java/Go) | ✅ 免费接入 |
| GordenPPT | Hermes Skill + CLI | ✅ 免费离线 |
| ChatPPT | npm CLI (`@yooai/cli`) | ✅ 免费有额度 |
