# Paseo 调研笔记

> 调研时间：2026-07-18
> 官网：https://paseo.sh
> 文档：https://paseo.sh/docs
> GitHub：https://github.com/paseo-ai/paseo (10.6k stars)

## 一句话总结

Paseo 是一个开源、免费的 Agent 编排平台，让你在 PC 上跑 daemon，用手机/桌面/Web/CLI 远程控制多个不同 provider 的 Agent。

## 收费模式

**完全免费，开源。** 无订阅/无付费套餐。官网说 "Self-hosted, multi-provider, open source." 导航栏只有 "Sponsor"（赞助）链接，无 pricing 页面。你只需要自己出底层模型 API 的费用（如 Anthropic/OpenAI API Key），Paseo 不抽成。

## 核心架构

```
PC/服务器上跑 Paseo daemon
    ↓
通过 relay 中继（无需暴露端口）
    ↓
手机 app / Web / CLI / 桌面端连接
    ↓
在手机上管理多个 Agent
```

- Daemon 绑定 localhost，通过 relay 中继安全连接，不暴露公网端口
- 手机端：app.paseo.sh 或 iOS/Android 原生 app
- 扫码连接：terminal 打印二维码，手机 app 扫码即连

## 多 Agent 管理能力

**支持。** 一个 workspace 里可以同时跑多个 Agent 会话，每个会话在手机 app 上开一个 tab：

- 同一个 workspace：可以同时有 Agent 会话、终端、浏览器、diff 视图
- 不同 Provider 混编：Claude Code 和 Codex 可以在同一个 workspace 里共存
- 跨 Provider 编排：Claude Code 可以派 Codex 子Agent，Codex 可以派 Grok Build 子Agent

## 支持的 Agent Provider

**原生支持**（装好 CLI 即可用）：
- Claude Code
- Codex CLI
- OpenCode
- pi

**ACP 目录**（40+，一键安装）：
- Hermes Agent ✅
- Gemini CLI
- GitHub Copilot
- Cursor
- Grok
- Qwen Code
- Kilo Code
- Cline
- Junie
- Mistral Vibe
- 以及更多...

## 什么是 ACP（Agent Communication Protocol）

ACP = Agent Communication Protocol，是 Agent 与编排平台之间的通信协议标准。

通俗理解：
- 传统用法：你手动在 terminal 敲 `codex "写个登录功能"` 来启动 Agent
- ACP 模式：Agent 提供一个符合 ACP 标准的 CLI 接口，Paseo 可以自动发现、启动、下发任务、停止它，不需要你手动敲命令

**类比：** 就像 USB-C 接口——不管什么品牌的设备，只要接口标准统一，插上就能用。ACP 就是 Agent 界的 "标准接口"。

如果 Work Buddy 有 CLI 但不支持 ACP：
→ 可以用 Paseo 的 Custom Provider 机制手动配置接入
→ 如果 Work Buddy 也提供 ACP 接口，则开箱即用

## 手机端体验

- 全功能 parity：手机 app 功能与桌面端一致
- 可以查看所有 workspace 和 session
- 可以给 Agent 发消息
- 可以查看 diff、终端输出
- 可以停止/重启 Agent

## 值得注意的点

- 不捆绑 Agent CLI：Docker 镜像只跑 daemon，需要自己装 Claude Code / Codex 等 CLI
- 手机 app 需要连接 daemon，daemon 离线时手机无法操控
- 适合有 PC/服务器常开机的场景