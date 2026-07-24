# TrendRadar 搭建记录

安装位置：`~/Developer/TrendRadar/`
Python虚拟环境：`.venv/Scripts/python.exe`
MCP Server入口：`.venv/Scripts/trendradar-mcp.exe`（已注册为Hermes MCP Server）

## 关键命令
```bash
cd ~/Developer/TrendRadar
uv run trendradar                    # 运行热点聚合
uv run trendradar --doctor           # 体检
uv run trendradar --test-notification # 测试推送
```

## 配置
- `config/config.yaml` — 主配置（平台、通知、AI分析）
- `config/frequency_words.txt` — 关键词过滤规则
- `config/timeline.yaml` — 调度时间线

## 推送渠道
支持：飞书 / 钉钉 / 企业微信 / Telegram / 邮件 / ntfy / Bark / Slack
在 config.yaml 的 `notification.channels` 下配置。

## 状态
- ✅ 已完成安装和依赖
- ✅ 已注册为 Hermes MCP Server
- ⏳ 需要配置飞书 Webhook URL 和 AI API Key 后才能启用推送和 AI 分析
