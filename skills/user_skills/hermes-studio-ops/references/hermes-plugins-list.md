# Hermes Plugins 配置速查

> 基于 `hermes plugins list --json` 输出，共 80 个插件（v1.0.0）。

## 快速配置命令

```bash
hermes config set web_providers.<name>.api_key <KEY>
hermes config set web_providers.<name>.enabled true
hermes config set plugins.<plugin-name>.api_key <KEY>
hermes plugins enable <plugin-name>
```

## web_providers（需要 API Key）

| 插件 | 需要 Key | 状态 | 说明 |
|------|----------|------|------|
| web-tavily | ✅ | ✅ 已配 | 搜索+内容提取+爬取 |
| web-exa | ✅ | ✅ 已配 | 深度语义搜索（AI 原生，非聚合） |
| web-firecrawl | ✅ | ✅ 已配 | 搜索+抓取+云浏览器 |
| web-parallel | ✅ | ❌ 未配 | AI 原生搜索，独立索引（82 CPM，比 Exa 贵） |
| web-brave-free | ✅ (免费) | ❌ 未配 | Brave 搜索免费层，2k次/月 |
| web-ddgs | ❌ | ❌ 未配 | DuckDuckGo，无需 Key |
| web-searxng | ❌ | ❌ 未配 | 自建 SearXNG 实例，隐私搜索 |
| web-xai | ✅ | ❌ 未配 | xAI Grok 网页搜索 |

> **Parallel.ai 结论**：不是搜索聚合器，是独立 AI 原生搜索引擎。价格最贵（82 CPM vs Exa 24 CPM）。与 Exa 功能重叠，已有 Exa 可不配。

## plugins（需要 API Key）

### Model Provider 类

| 插件 | Key 前缀 | 已配置 |
|------|----------|--------|
| alibaba-provider | `ms-` | ✅ |
| xiaomi-provider | `sk-` | ✅ |
| anthropic-provider | sk-ant- | ❌ 推荐配 |
| gemini-provider | AIza... | ❌ 推荐配 |
| openrouter-provider | sk-or- | ❌ 推荐配 |
| deepseek-provider | sk- | ❌ 已有 183399 覆盖 |
| minimax-provider | — | ❌ 已有 topapi 覆盖 |
| xai-provider | — | ❌ 已有心流grop 覆盖 |
| 其他（bedrock/kimi/vertex/azure/ollama等） | — | ❌ 按需 |

### 浏览器后端类

| 插件 | Key | 状态 |
|------|-----|------|
| browser-firecrawl | 同 firecrawl | ✅ 已 enable |
| browser-browser-use | BROWSER_USE_API_KEY | ❌ 按需 |
| browser-browserbase | BROWSERBASE_API_KEY | ❌ 按需 |
| real-browser-mcp | 无需 Key | ✅ 已安装使用 |

> **real-browser-mcp 已覆盖本地浏览器控制**（控制用户本地 Edge，保留所有登录状态），browser-browser-use/browser-browserbase 是云端方案，不需要除非有特殊需求。

### 生图/视频类

| 插件 | 状态 | 说明 |
|------|------|------|
| 心流grop（custom_providers） | ✅ 主用 | GPT-5.5 + gpt-image-2 + gemini-3-pro-image |
| videogen（custom_providers） | ✅ 主用 | grok-imagine-video-1.5-fast |
| fal（图片） | ❌ 推荐配 | flux-2-klein、flux-2-pro 等 |
| fal（视频） | ❌ ⭐推荐配 | Veo 3.1、Kling 等（比 grok-video 强） |
| krea | ❌ 按需 | Krea 2 Large |
| openai | ❌ 按需 | gpt-image-2 |
| xai（图片+视频） | ❌ 按需 | grok-imagine |

### 平台接入类

| 平台 | AppID | Secret | 接入方式 | 状态（2026-07-09） |
|------|-------|--------|---------|------------------|
| **微信** | 4a75b8ba (account_id) | token: `4a75b8ba...` | WebSocket (`base_url=https://ilinkai.weixin.qq.com`) | ✅ **连接正常** — 历史记录（07-08 19:26）证明能收发 |
| **企业微信** | BotID: `aibmZNHLk4PBJ3gawTCqmC7C50DD04-_0Qu` | `47t9L5jMLkt991qKBE3t6yXGL5hIKZq5ojewmMkABi4` | WebSocket (`wss://openws.work.weixin.qq.com`) | ✅ **连接正常** — 无错误日志 |
| **飞书** | AppID: `cli_aa92b1fa06395cb0` | `***FEISHU_SECRET***` | WebSocket (lark-oapi) | ⚠️ **连接建立但不稳定** — `Adapter loop unavailable` 错误导致消息被丢弃；需重启验证 |
| **QQ** | AppID: `1904979924` | `bot:v1_Rpgy-...` | QQ WebSocket Gateway | ❌ **完全无法连接** — `QQAdapter.connect() got an unexpected keyword argument 'is_reconnect'` 是 Hermes SDK 版本 Bug，当前无解，需等官方更新 |

### 平台已知错误

| 平台 | 错误信息 | 解决方案 |
|------|---------|---------|
| **QQ** | `is_reconnect` unexpected keyword | ❌ 无解，需等 Hermes 更新 |
| **飞书** | `Adapter loop unavailable for 120s` | 重启 Gateway；检查飞书应用权限 |
| **飞书** | `Profile 'writer' enables port-binding but multiplex_profiles is on` | 在 `writer` profile config.yaml 删除 `platforms.feishu`，只保留 default |

### 其他工具类

| 插件 | 需要 Key | 状态 |
|------|----------|------|
| disk-cleanup | ❌ | ✅ 已 enable，自动清垃圾 |
| security-guidance | ❌ | ✅ 已 enable，安全提示 |
| langfuse | ✅ | ❌ 推荐配，可观测 |
| spotify | ✅ | ❌ 娱乐向，语音控制 |

---

## QQ Bot 配置详情

```yaml
# 写入 config.yaml 的 gateway.platforms.qqbot.extra
gateway:
  platforms:
    qqbot:
      enabled: true
      extra:
        app_id: "1904979924"
        client_secret: "bot:v1_Rpgy-..."
        markdown_support: true
        dm_policy: allowlist
```

> ⚠️ **token 格式**：`bot:v1_xxx` 是 QQ 开放平台的 Bot Secret。配置写入后需要**重启整个 Hermes 桌面应用**才能完全生效。

> ⚠️ **已知 Bug**：`QQAdapter.connect() got an unexpected keyword argument 'is_reconnect'` 是 Hermes SDK 版本与 QQ 官方 SDK 不兼容问题，**当前版本无解**，QQ 完全无法连接，需等 Hermes 更新版本修复。

---

## 企业微信(WeCom)配置详情

```yaml
gateway:
  platforms:
    wecom:
      enabled: true
      extra:
        bot_id: "aibmZNHLk4PBJ3gawTCqmC7C50DD04-_0Qu"
        secret: "47t9L5jMLkt991qKBE3t6yXGL5hIKZq5ojewmMkABi4"
        home_channel: null
```

> ⚠️ **企微需要公网回调地址**：如果企业微信管理后台启用了"接收消息"，需要填写回调地址。WebSocket 模式（`wss://openws.work.weixin.qq.com`）不需要公网 IP。

---

## 飞书配置详情

```yaml
platforms:
  feishu:
    extra:
      app_id: "cli_aa92b1fa06395cb0"
      app_secret: "***FEISHU_SECRET***"
```

> ⚠️ **多 profile 冲突**：如果开了 `gateway.multiplex_profiles`，飞书只能配置在 default profile，不能同时配置在其他 profile（如 `writer`），否则会报错退出。

---

## 关键配置路径

```bash
# Hermes CLI 路径（bundled Python Scripts）
hermes_cli="C:\\Users\\Admin\\.hermes-web-ui\\desktop-runtime\\hermes\\0.18.0\\win-x64\\python\\Scripts\\hermes.cmd"

# web_providers 配置（web搜索类）
$hermes_cli config set web_providers.tavily.api_key <KEY>
$hermes_cli config set web_providers.exa.api_key <KEY>
$hermes_cli config set web_providers.firecrawl.api_key <KEY>

# plugins 配置（provider/其他）
$hermes_cli config set plugins.alibaba-provider.api_key <KEY>
$hermes_cli config set plugins.xiaomi-provider.api_key <KEY>

# 启用无 Key 插件
$hermes_cli plugins enable browser-firecrawl
$hermes_cli plugins enable disk-cleanup
$hermes_cli plugins enable security-guidance

# 查看插件状态
$hermes_cli plugins list --json

# config 查看
$hermes_cli config show
```

## 错误修正

- ❌ `write_file` / `patch` 直接写 `config.yaml` → 拒绝（安全敏感）
- ✅ 使用 `hermes config set` 命令写入
- ❌ `plugins.web-tavily.*` → 无效
- ✅ `web_providers.tavily.*` → 正确
- ❌ disk-cleanup / security-guidance 需要 config set → 无需 Key，只需 `hermes plugins enable`