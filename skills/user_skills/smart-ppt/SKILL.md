---
name: smart-ppt
description: >
  当用户需要生成PPT演示文稿时使用。
  用于5种模式路由：简单模式(AiPPT)、精致模式(PPT Master)、离线模式(GordenPPT)、零成本模式(HTML演示)、花钱模式(ChatPPT)。
  不要用于视频编辑、数据分析报告、或非演示文稿类的文档生成。
  触发词：生成PPT、做演示文稿、创建幻灯片、做汇报、PPT制作
tags:
  - ppt
  - presentation
  - smart
  - routing
  - docmee
  - ppt-master
  - gordenppt
  - chatppt
  - html
triggers:
  - 生成PPT
  - 做演示文稿
  - 创建幻灯片
  - 做汇报
  - PPT制作

---

# 智能PPT生成器 — 5模式路由

## 触发方式

> "生成一个关于【主题】的PPT"
> "生成一个关于【主题】的PPT，这是我的资料【附件/文字】"

## 完整路由决策树

```
你说：生成一个关于XXX的PPT（可附文字/文件）
  ↓
Step 1: 文多多生成大纲（SSE 流式，1982+字）
  ↓
Step 2: 我问你：哪种模式？
  │
  ├─ ① 简单模式 — 文多多走完6步 → PPT下载链接
  │
  └─ ② 精致模式 →
       │  Step 2a: 逐项问你参数（选择题格式）
       │  Step 2b: 尝试 ChatPPT（79模板）
       │  ├─ 成功 → 下载PPT
       │  └─ code=11500(额度用完) → 自动降级
       │       └─ GordenPPTSkill(21套模板，离线本地)
       │
       └─ ③ HTML 演示模式（完全免费，自定风格）
          → 我逐项问你所有视觉参数（选择题格式，8题）
          → 生成可交互HTML → 浏览器打开 → Ctrl+P 导出PDF
```

---

## 各模式详细说明

### ① 简单模式 → AiPPT / 文多多

**适合：** 快速出稿，内容不复杂，不求排版极致

**流程：**
```
1. 文多多生成大纲（SSE 流式）
2. 自动走完 6 步 → PPT 下载链接
```

**依赖：** 文多多 API Key ✅ 已配置
**限制：** 模板随机分配，不可选；需要网络

---

### ② 精致模式 → PPT Master ★ 推荐

**适合：** 追求最高排版质量，需要原生可编辑 PPTX

**流程：**
```
1. 把你的材料放入 ~/Developer/ppt-master/projects/<name>/sources/
2. 我按 PPT Master 工作流驱动：
   ├─ 源材料→Markdown 转换
   ├─ 项目初始化
   ├─ AI 设计规范确认（风格/页数/配色）
   ├─ SVG 生成
   └─ SVG→PPTX 导出
3. 输出: exports/<name>_<timestamp>.pptx
```

**6 种设计风格：** 杂志风 / 新闻财经风 / 瑞士风 / 毛玻璃 SaaS / 孟菲斯波普 / Zine 风

**依赖：** Python 3.10+ ✅ / 本地 ~/Developer/ppt-master/ ✅ / 依赖已装 ✅

**注意：** 推荐 Claude Opus 或 Gemini 3.5 Flash 获得最佳效果；当前 deepseek-v4-flash 可用但排版精细度可能略逊

---

### ③ 离线模式 → GordenPPT

**适合：** 无网络环境，需要中文模板，党政/论文/答辩场景

**流程：**
```
1. 选模板（21套中文模板）
2. 生成 edits.json
3. python build_pptx.py → 本地 PPTX
```

**可用模板：**
| 场景 | 推荐模板 |
|------|---------|
| 技术方案/架构 | architecture-deck |
| 商务汇报/咨询 | mckinsey-style |
| 极简商务 | minimal-business-summary |
| 数据分析 | data-viz-deck |
| 论文答辩 | thesis-* |
| 党政风 | red-patriot-* |
| 运营方案 | operations-deck |

**依赖：** python-pptx ✅ / 21套本地模板 ✅ / 完全离线

---

### ④ 零成本模式 → HTML 演示文稿

**适合：** 零预算，需要自定义视觉风格，响应式演示

**流程：**
```
1. 我按你选的风格参数生成完整 HTML
2. 浏览器打开 → Ctrl+P 导出 PDF
```

**特点：**
- 不消耗任何 API 额度
- 自定义配色/字体/布局/动画
- 支持 Chart.js 图表
- 响应式布局（手机/平板/桌面）
- 可分享链接，无需安装

**依赖：** 无（纯 HTML/CSS/JS 生成）

---

### ⑤ 花钱模式 → ChatPPT

**适合：** 愿意付费充值，想要 79 套模板

**状态：** ⚠️ 免费额度已用完，需充值后使用

**流程：**
```
1. 选模板（79套）
2. 选页数/字体/图片风格
3. chatppt ppt generate → 下载
```

**注意：** 返回 code=11500 表示额度用完，需联系 @yooai 充值

---

## 路由优先级

| 你的场景 | 推荐模式 | 工具 |
|---------|---------|------|
| 追求最高质量 | ② 精致模式 | PPT Master |
| 需要快速出稿 | ① 简单模式 | AiPPT |
| 无网络 | ③ 离线模式 | GordenPPT |
| 零预算 | ④ 零成本模式 | HTML |
| 愿意付费 | ⑤ 花钱模式 | ChatPPT |
| 党政/论文/答辩 | ③ 离线模式 | GordenPPT |
| 已有模板想复用 | ② 精致模式(套模板) | PPT Master |

## 依赖检查

| 工具 | 状态 | 备注 |
|------|------|------|
| PPT Master 仓库 | ✅ ~/Developer/ppt-master/ | 已 clone |
| PPT Master 依赖 | ✅ pip install 完成 | python-pptx, PyMuPDF, Pillow 等 |
| GordenPPTSkill | ✅ 21套模板 | 离线可用 |
| AiPPT 文多多 | ✅ API Key 已配 | ak_s_Q1m1s3T6Fs5imN4_ |
| ChatPPT CLI | ⚠️ 额度用完 | 需充值 |
| HTML 演示 | ✅ 零成本 | 随时可用 |

## 参考文件

- PPT Master 原生 skill: `~/AppData/Local/hermes/skills/productivity/ppt-master/SKILL.md`
- GordenPPTSkill: `~/AppData/Local/hermes/skills/gorden-ppt-skill/SKILL.md`
- AiPPT 文多多: `~/AppData/Local/hermes/skills/aippt-skill/SKILL.md`
- 精装模式已知问题与降级链路: `references/elaborate-mode--pitfalls-and-fallbacks.md`
- 样式预设: `~/AppData/Local/hermes/skills/smart-ppt/references/style-presets.md`