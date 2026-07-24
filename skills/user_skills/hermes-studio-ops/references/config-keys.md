# Hermes Config Key 速查（2026-07-08）

## delegation 块

| Key | 当前值 | 用途 |
|-----|--------|------|
| `delegation.max_spawn_depth` | `9999` | 子代理嵌套层数上限 |
| `delegation.max_concurrent_children` | `9999` | 最大并发子代理数 |
| `delegation.orchestrator_enabled` | `true` | 是否允许 orchestrator 角色 |

## web_providers（搜索类）

| Key | 当前状态 | 值 |
|-----|---------|-----|
| `web_providers.tavily.api_key` | ✅ 已配置 | `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` |
| `web_providers.tavily.enabled` | ✅ | `true` |
| `web_providers.exa.api_key` | ✅ 已配置 | `67cc607e-cf49-47da-bec8-087c05488bb5` |
| `web_providers.exa.enabled` | ✅ | `true` |
| `web_providers.firecrawl.api_key` | ✅ 已配置 | `fc-b2fe461...` |
| `web_providers.firecrawl.enabled` | ✅ | `true` |

## plugins（Provider API Keys）

| Key | 当前状态 |
|-----|---------|
| `plugins.alibaba-provider.api_key` | ✅ `ms-6fe8bab9...` |
| `plugins.xiaomi-provider.api_key` | ✅ `sk-crx6w6yy...` |

## Gateway Platforms

| Platform | 配置 |
|----------|------|
| `gateway.platforms.qqbot` | ✅ AppID `1904979924` + Secret 已写入，待 Hermes 重启生效 |
| `gateway.platforms.wecom` | ✅ BotID `aibmZNHLk4PBJ3gawTCqmC7C50DD04-_0Qu` + Secret 已写入，待验证回调 |

## 已启用的插件

- `browser/firecrawl`
- `disk-cleanup`
- `security-guidance`

## 常用 hermes config set 命令

```bash
# 查看当前所有配置
hermes config show

# 查看配置路径
hermes config path

# 设置任意配置项（支持点号路径）
hermes config set delegation.max_spawn_depth 9999
hermes config set web_providers.tavily.api_key <KEY>
hermes config set web_providers.tavily.enabled true
hermes config set gateway.platforms.qqbot.enabled true
hermes config set gateway.platforms.wecom.enabled true
```