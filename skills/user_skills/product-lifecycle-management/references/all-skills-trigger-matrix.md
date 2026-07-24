# 全技能触发词汇总

## 分类说明

- **用户自定义** — 你要求我创建的 skill
- **系统/外部** — Hermes 预装或第三方 source 安装
- **pm-skills** — 从 GitHub 安装的 68 个 PM 框架子技能（通过 `product-lifecycle-management` 间接调用）

## 用户自定义 Skill

| Skill | 触发词 / 你说 | 说明 |
|-------|-------------|------|
| `ppt-generation` | `做一份PPT` / `用GordenPPT做一份XXX` / `用AiPPT生成XXX` / `用ChatPPT创建XXX` | PPT统一入口，自动路由到最合适的工具 |
| `product-lifecycle-management` | `让产品经理做...` / `启动产品生命周期` | 4阶段18步产品生命周期状态机 |
| `orchestrator-loop` | `任务：...` / `开始任务` | 多阶段任务编排框架 |
| `acp-dev-pipeline` | `帮我开发一个...` | TDD-first 开发流水线：先写测试 → 再写代码 → 验证通过交付 |
| `prompt-optimizer` | `帮我优化提示词：...` | LLM API 提示词优化 |
| `document-parsing` | `处理这个目录` / `解析文档` | MinerU 批量文档转 Obsidian |
| `xhs-cli` | `小红书搜一下...` | 小红书搜索/互动 |
| `agently-mail` | `帮我发一封邮件` / `我最近收到了哪些邮件？` | Agent QQ 邮箱收发 |
| `bailian-cli` | `百炼 看图：...` / `百炼 搜索：...` / `百炼 朗读：...` / `百炼 画一个...` | DashScope API 全模态 |
| `tabbit-browser` (MCP) | `用浏览器打开...` / `帮我截图` | Tabbit 浏览器自动化（21个MCP工具）|
| `heartflow` | `心虫评估：...` / `心虫分享：...` | 对话深度复盘与认知分析 |
| `video-use` | `帮我把这些剪一下` | AI 视频剪辑 |
| `step-annotate` | (需描述截图批注需求) | 截图编号批注 |

## 系统/外部 Skill

| Skill | 触发词 / 你说 |
|-------|-------------|
| `apikey-image-gen` | `帮我生成一张图...` |
| `hyperframes` / `remotion` | `做一个AI视频...` |
| `coze-workflow-automation` | `用扣子运行...` |
| `libtv-cli` / `libtv-feishu-auto` | LibTV 画布操作 |
| `feishu-cli` | `飞书...` |
| `grok-image-to-video` | 图片转视频 |
| `markdown-viewer` | 图表/可视化 |
| `browser-automation` | 浏览器自动化 |
| `cloudflare-tunnel-setup` | Cloudflare 隧道 |

## pm-skills 子技能（68个）

通过 `product-lifecycle-management` 的 18 步流水线间接调用。不单独触发，详见 `pm-skills/` 目录。

## 已安装的独立 CLI 工具

| 工具 | 安装位置 | 用法命令 |
|------|---------|---------|
| `chatppt` | `@yooai/cli v1.2.4` | `chatppt ppt generate "主题"` |
| `opencode` | `opencode-ai v1.17.9` | `opencode acp` / `opencode [project]` |
| `bl` | `@alibaba/bailian-cli`（未公开） | — |
