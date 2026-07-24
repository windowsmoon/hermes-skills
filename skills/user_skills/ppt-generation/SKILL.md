---
name: ppt-generation
description: >
  当用户要求生成PPT演示文稿时使用。
  自动路由到最佳引擎（AiPPT/PPT Master/GordenPPT/HTML演示/ChatPPT），根据用户选择的简单/精致模式自动匹配。
  不要用于：Word文档生成、PDF报告、思维导图（走edrawmind-mindmap）、HTML页面（走frontend-design）。
  触发词：生成PPT、做个PPT、演示文稿、幻灯片、做一份PPT
tags:
  - ppt
  - presentation
  - slides
  - routing
  - ppt-master
  - gorden-ppt
  - aippt
  - chatppt
triggers:
  - 生成PPT
  - 做个PPT
  - 演示文稿
  - 幻灯片
  - 做一份PPT

---

# PPT 生成 — 统一入口（5模式路由）

## 工作模式

你说"生成一个关于XXX的PPT" → 我列出 5 种模式让你选：

| # | 模式 | 工具 | 适用场景 |
|---|------|------|---------|
| ① 🟢 | 简单模式 | AiPPT/文多多 | 快速出稿，一键生成 |
| ② 🔵 | 精致模式 ★ | PPT Master | 最高质量，原生可编辑 |
| ③ 🟡 | 离线模式 | GordenPPTSkill | 无网络，党政/论文/答辩 |
| ④ ⚪ | 零成本模式 | HTML 演示 | 零预算，自定义风格 |
| ⑤ 💰 | 花钱模式 | ChatPPT | 79模板，需充值 |

## 工具详情

### ① AiPPT / 文多多（简单模式）
- 在线 API，6 步自动生成
- 模板随机分配
- 需网络

### ② PPT Master（精致模式 ★ 推荐）
- 安装于 `~/Developer/ppt-master/`
- SVG→DrawingML 原生 PPTX
- 6 种设计风格：杂志/新闻/瑞士/毛玻璃/孟菲斯/Zine
- 4 条工作流：直接生成/套模板/创建模板/增强
- 需 Python 3.10+（Hermes 自带）

### ③ GordenPPTSkill（离线模式）
- 21 套中文模板
- python-pptx 本地生成
- 完全离线

### ④ HTML 演示（零成本模式）
- 纯 HTML/CSS/JS 生成
- 浏览器打开，Ctrl+P 导出 PDF
- 零成本，自定义风格

### ⑤ ChatPPT（花钱模式）
- 79 套模板
- 云端渲染
- ⚠️ 免费额度已用完，需充值

## 依赖

| 工具 | 状态 | 路径 |
|------|------|------|
| PPT Master | ✅ 已装 | ~/Developer/ppt-master/ |
| GordenPPTSkill | ✅ 已装 | ~/Developer/GordenPPTSkill/ |
| AiPPT 文多多 | ✅ API Key 已配 | ~/AppData/Local/hermes/scripts/aippt_cli.py |
| ChatPPT CLI | ⚠️ 额度用完 | @yooai/cli |
| HTML 演示 | ✅ 随时可用 | frontend-design + uiux-slides |