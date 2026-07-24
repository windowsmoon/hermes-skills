---
name: trendradar
description: >
  当用户要求查看或监控热点话题/趋势时使用。
  支持8平台（微博/知乎/抖音/B站/头条/百度/微信/36氪）+ AI语义过滤 + 飞书推送。
  不要用于：搜索特定信息（走unified-search）、深度分析某个话题（走sn-deep-research）。
  触发词：今天的热点、热点、热搜、趋势、监控、看看今天什么火
triggers:
  - 今天的热点
  - 热点
  - 热搜
  - 趋势
  - 监控
  - 看看今天什么火
tags:
  - trendradar

---

# TrendRadar 热点监控

## 触发词

> "帮我拉今天的热点" → 不过滤，全量推送
> "抓取关于 AI视频 的热点" → AI 语义理解，只推相关

## 动态逻辑

用户说 **"帮我拉今天的热点"**
  → 清空 frequency_words.txt（全部热点）
  → 运行 TrendRadar → 全量推飞书
  → 不启用 AI 过滤

用户说 **"抓取关于 xxx 的热点"**
  → 写入 xxx 到 frequency_words.txt
  → 运行 TrendRadar → AI 语义过滤
  → 大模型判断每条标题是否跟 xxx 概念相关
  → 只推匹配的到飞书

**区别**：大模型只在"抓取关于"时启用语义理解。
"拉热点"时不过滤、不调 AI，节省额度。

## 已启用平台（8个）
微博 · 知乎 · 抖音 · 百度热搜 · B站热搜 · 今日头条 · 澎湃新闻 · 贴吧

## 推送
飞书 Webhook 已配置，结果自动推送至飞书群。

## MCP
TrendRadar MCP Server 已注册，可通过 MCP 协议调用热点数据分析。

## 控制脚本
`scripts/trendradar_ctl.py` 支持：
- `set <关键词>` — 设置过滤关键词
- `clear` — 清空关键词（全量模式）
- `run` — 运行 TrendRadar
