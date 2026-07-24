# TrendRadar 搭建记录 (2026-07-18)

## 安装
- git clone https://github.com/sansan0/TrendRadar ~/Developer/TrendRadar
- uv sync（litellm 是大包，需 long timeout）
- trendradar v6.10.0，Python 3.12

## MCP Server
- 已注册为 Hermes MCP Server（trendradar-mcp）
- STDIO 模式
- 命令路径: ~/Developer/TrendRadar/.venv/Scripts/trendradar-mcp.exe

## 配置
- 飞书 Webhook 已配置
- AI_API_KEY 已配置（183399 deepseek-v4-flash）
- 已启用 8 个平台：微博/知乎/抖音/百度热搜/B站热搜/今日头条/澎湃新闻/贴吧
- frequency_words.txt 清空 = 不过滤，返回全部热点
