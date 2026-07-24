# Hermes Studio v0.6.12 → v0.6.30 版本差异

> 内化文档版本 vs 实际运行版本（2026-07-16 检查）

## 环境

| 项目 | 值 |
|------|-----|
| Internalized manual | v0.6.12（577 行中文操作手册） |
| 实际 Web UI | **0.6.30** |
| 实际 Runtime | **0.18.2** |
| 版本跳跃 | 0.6.12 → 0.6.30（18+ 小版本） |

## 新增模块（v0.6.12 没有）

| 模块 | 端点 | 用途 |
|------|------|------|
| Coding Agents | 10 | Codex / Claude Code 安装、配置、运行 |
| TTS | 11 | 文字转语音生成 + 设置 |
| STT | 10 | 语音转文字转录 + 设置 |
| Runtime Versions | 9 | 运行时版本管理（升降级 WebUI/Runtime） |
| Update | 7 | 自更新管理 |
| API Docs | 2 | OpenAPI 路由目录（操作手册、接口文档） |
| Journey | 1 | Hermes Agent 学习路径图 |
| Media | 2 | 媒体资源生成 |
| Write Gate | 4 | Hermes Agent 写入审批 |
| Models | 13 | 模型 ID 查看与配置 |
| Providers | 3 | 模型 Provider 配置管理 |
| Webhook | 1 | 传入 Webhook |
| Weixin | 3 | 微信扫码登录 |

## OAuth 支持（全部新增）

Anthropic, Codex, Copilot, Gemini, Nous, xAI

## 大幅扩展的模块

| 模块 | v0.6.12 端点 | v0.6.30 端点 | 新增内容 |
|------|-------------|-------------|---------|
| Sessions | ~10 | **37** | 文件夹/搜索/统计/多选项 |
| Profiles | ~3 | **14** | 运行时状态/启动/重启 |
| Kanban | ~8 | **25** | 完整列/卡片/工作流 |
| MCP | ~3 | **7** | 测试/工具查询 |
| Auth | ~5 | **16** | 用户管理/锁定IP/多用户/密码管理 |

## 引用说明

此差异通过对比以下来源得出：
1. 用户内化的 v0.6.12 中文操作手册（577 行，存在 D:\Obsidian\Note）
2. `hermes_studio_api_openapi_get()` 实时返回的 OpenAPI 模块列表
3. `GET /api/hermes/runtime-versions` 返回的活动版本

## 复用方法

每次收到关于 Hermes Studio 功能的查询时：
1. 检查 `GET /api/hermes/runtime-versions` 的 `webUiVersion`
2. 与内化文档版本对比
3. 如果不匹配，用 `hermes_studio_api_openapi_get()` 扫描新模块
4. 必要时更新本文档与 SKILL.md 的差异表
