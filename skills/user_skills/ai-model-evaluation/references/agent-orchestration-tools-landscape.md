# 国内外 Agent 编排/管理工具全景（2026年7月）

## 国际产品

### Paseo — 最接近"手机管理多 Agent"的工具
- 官网：paseo.sh | GitHub: 10.6k stars
- 收费：**免费开源**（只出模型 API 调用费，Paseo 不抽成）
- 定位：自托管的编程 Agent 统一控制台
- 核心能力：
  - 手机上管 Claude Code、Codex、Hermes Agent、OpenCode 等 40+ Agent
  - 跨 Provider 混编（Claude Code 派 Codex 子Agent）
  - Workspace 体系：一个工作区同时跑多个 Agent + Terminal + 浏览器
  - 原生支持 ACP 协议
- 安装方式：桌面 App / CLI / Docker
- 手机配对：扫 QR 码，走 relay 中继（不暴露公网端口）
- 国内可用性：完全可用，开源自托管不依赖境外服务

### 国际同类对比
| 产品 | 类型 | 手机端 | 跨 Provider | 收费 |
|------|------|--------|------------|------|
| Paseo | Agent 管理平台 | ✅ 核心 | ✅ | 免费开源 |
| OpenCode Desktop | Agent 桌面端 | ❌ | ✅ | 免费 |
| Codex App | Agent 管理 | ✅ | ❌ 自家 | 免费+订阅 |

---

## 国内产品

### 腾讯 WorkBuddy
- 官网：workbuddy.cn | 微软商店可下载
- 收费：**免费**（每月送 500 积分）
- 定位：全场景 AI 办公工作台
- 核心能力：
  - 多 Agents 并行工作
  - 自然语言执行复杂任务（做 PPT/写文档/自动化）
  - 集成腾讯办公生态（微信/腾讯文档）
  - Windows 桌面端
- 和 Paseo 的区别：强在办公场景而非编程 Agent 编排

### 腾讯 QClaw
- 定位：AI 编程 Agent，本地执行 + 微信直连
- 适合办公自动化
- 数据本地存储

### 字节 Coze / 扣子
- 定位：云端 Agent 工作流编排平台
- 核心：构建复杂 Bot，非管理编程 Agent
- 收费：免费额度 + 付费

### Dify
- 定位：开源低代码 LLM 应用平台
- 核心：构建 AI 应用而非管理 Agent
- 可自部署
- 收费：开源免费 + 云服务版付费

### Kimi Work（月之暗面）
- 定位：AI 办公工作台
- 类似 WorkBuddy，强在办公场景
- 收费：免费 + 会员

### 阿里百炼
- 定位：企业级大模型服务平台
- 支持多 Agent 编排
- 收费：按量计费

### 腾讯 CodeBuddy
- 定位：AI 代码编辑器（类似 Cursor）
- 集成腾讯生态

---

## 关键概念解析

### ACP (Agent Communication Protocol)
Agent 通信协议——Agent 之间、Agent 与管理器之间的标准通信接口。
"通过 ACP 协议暴露 CLI" = 一个工具按 ACP 标准写好命令行接口，管理器就能自动发现、启动、通信、停止它，像标准插座插头。

### Paseo 架构
```
手机 App / 桌面 App / Web / CLI
        ↕ (relay 中继 / 直连)
    Paseo Daemon (跑在你的 PC 或服务器上)
        ↕ (ACP 协议)
    Agent CLI (Claude Code / Codex / Hermes / ...)
```

### 为什么国内没有 Paseo 的对标
因为 Paseo 管的是**跑在你本地电脑上的编程 Agent CLI**，国内大厂走的是**云端编排 + 自家生态**路线。如果你想在手机上管 Hermes + Codex，Paseo 本身就是最佳选择。