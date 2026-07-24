# Hindsight + SiliconFlow 部署全流程

在 Hermes Studio 上部署 Hindsight 作为外部 Memory Provider，使用硅基流动的免费/低价 API。

## 架构

```
Hermes Agent Gateway (hermes_cli.main gateway run)
    │
    ├─ memory.provider: hindsight (in ~/.hermes/config.yaml)
    │
    └─ Hindsight Daemon (hindsight-embed -p hermes daemon start)
         │  Port 9100  │  Log: ~/.hindsight/profiles/hermes.log
         │
         ├── 内嵌 PostgreSQL (pg0-embedded)
         ├── LLM: SiliconFlow DeepSeek-V4-Flash (记忆提取/综合)
         └── Embedding: SiliconFlow BAAI/bge-m3 (免费)
```

## 前置条件

- Hermes Studio 已安装并运行
- uv 可用
- 硅基流动 API Key

## 安装步骤

### Step 1: 安装核心包

```bash
# 客户端库 (纯Python, 轻量)
uv pip install --python <bundled-python-path> hindsight-client>=0.6.1

# 嵌入式 daemon CLI
uv pip install --python <bundled-python-path> hindsight-embed>=0.1.0

# API Server (含 PostgreSQL 等重型依赖)
# 如果网络慢，先下载再本地安装：
pip download hindsight-api-slim==0.8.4 -d D:\hermes-data\hindsight_deps
uv pip install --python <bundled-python-path> --no-index --find-links D:\hermes-data\hindsight_deps hindsight-api-slim==0.8.4

# 嵌入式 PostgreSQL
uv pip install --python <bundled-python-path> pg0-embedded
```

> Windows bundled Python 路径：`C:\Users\<user>\.hermes-web-ui\desktop-runtime\hermes\<version>\win-x64\python\python.exe`

### Step 2: 创建 hindsight-embed Profile

```bash
hindsight-embed profile create hermes --port 9100
```

### Step 3: 配置环境变量

```bash
hindsight-embed profile set-env hermes HINDSIGHT_API_LLM_PROVIDER openai
hindsight-embed profile set-env hermes HINDSIGHT_API_LLM_MODEL Pro/deepseek-ai/DeepSeek-V4-Flash
hindsight-embed profile set-env hermes HINDSIGHT_API_LLM_BASE_URL https://api.siliconflow.cn/v1
hindsight-embed profile set-env hermes HINDSIGHT_API_KEY <your-siliconflow-key>
hindsight-embed profile set-env hermes HINDSIGHT_API_EMBEDDINGS_PROVIDER openai
hindsight-embed profile set-env hermes HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL https://api.siliconflow.cn/v1
hindsight-embed profile set-env hermes HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL BAAI/bge-m3
hindsight-embed profile set-env hermes HINDSIGHT_API_RERANKER_PROVIDER rrf
hindsight-embed profile set-env hermes HINDSIGHT_API_PORT 9100
```

### Step 4: 创建 Hermes Hindsight 配置

`~/.hermes/hindsight/config.json`:
```json
{
  "mode": "local_external",
  "api_url": "http://127.0.0.1:9100",
  "bank_id": "hermes",
  "recall_budget": "mid",
  "memory_mode": "hybrid",
  "auto_retain": true,
  "auto_recall": true,
  "retain_context": "conversation between Hermes Agent and the User"
}
```

### Step 5: 设置 Hermes memory provider

通过 Hermes Studio API：
```bash
PUT /api/hermes/config
{"section":"memory","values":{"provider":"hindsight","memory_enabled":true}}
```

或直接写 `~/.hermes/config.yaml`:
```yaml
memory:
  provider: hindsight
```

### Step 6: 启动 daemon

```bash
hindsight-embed -p hermes daemon start
```

验证：`hindsight-embed -p hermes daemon status` 应显示 "Daemon is running"
健康检查：`curl http://127.0.0.1:9100/health` → `{"status": "healthy", "database": "connected"}`

### Step 7: 重启 Hermes 网关

```bash
# 通过 Hermes Studio API 重启
# POST /api/hermes/profiles/{name}/gateway/restart

# 或直接找到 gateway PID 并 kill
# Hermes Studio 会自动重启
```

### Step 8: 启动 Control Center (可选)

```bash
hindsight-embed -p hermes control start
# 打开: http://localhost:7878/?token=<随机token>
# 可在此界面浏览记忆库、搜索、管理配置
```

### Step 9: 开机自启

见 skill 模板 `templates/hermes-hindsight-startup.bat`。

放入 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` 目录。

## 通过 Hermes Studio API 配置 memory provider

当 `hermes` CLI 不可用时（Hermes Studio 环境）：

```bash
# 设置 memory provider
curl -X PUT http://127.0.0.1:8748/api/hermes/config \
  -H "Content-Type: application/json" \
  -d '{"section":"memory","values":{"provider":"hindsight","memory_enabled":true}}'

# 验证
curl http://127.0.0.1:8748/api/hermes/config?section=memory
```

注意：该 API 修改的是 Web UI 层配置，底层网关仍需 `~/.hermes/config.yaml` 或重启后生效。

## 常见问题

| 错误 | 原因 | 解决 |
|------|------|------|
| `Invalid LLM provider: openai_compatible` | `llm_provider` 不支持 `openai_compatible` | 用 `openai` + 设 `llm_base_url` |
| `Unknown reranker provider: none` | `none` 不是合法值 | 用 `rrf` 或 `siliconflow` |
| `pg0-embedded is required` | 未装嵌入式 PostgreSQL | `uv pip install pg0-embedded` |
| `Resource deadlock avoided` | 有残留进程锁住文件 | kill 所有 hindsight/python 进程重试 |
| File locked / Access denied | Hermes 网关占用 .pyd 文件 | kill 网关进程后再 pip install |
| `Failed to acquire lock` | uv 锁冲突 | 清空 `~/AppData/Local/uv/cache/*.lock` |
| 网络超时下载包 | 大包下载慢 | 外网 `pip download` 后本地 `--no-index --find-links` |

## 三种模式对比

| 模式 | Daemon 管理 | PostgreSQL | 适用场景 |
|------|:-----------:|:----------:|----------|
| `cloud` | Hindsight 云端 | 云端 | 有 API key 时最省事 |
| `local_embedded` | Hermes 自动管理 | 内嵌 pg0 | 想全自动但能接受重型依赖 |
| `local_external` | 手动 hindsight-embed | 内嵌 pg0 | 需要独立控制 daemon 生命周期 |

## 开机自启 (Windows)

在 `D:\Program\Hermes Studio\relate program\` 下创建启动脚本:

```powershell
# hindsight-start.cmd
hindsight-embed -p hermes daemon start
```

加入 Windows 任务计划程序或开机启动项。
