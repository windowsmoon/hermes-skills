---
name: ppt-master
description: >
  当用户需要通过PPT Master引擎生成精致PPT时使用。
  ChatPPT CLI引擎，支持79种模板、字体选择、图片风格、页数定制。
  不要用于：简单PPT（走AiPPT）、离线PPT（走GordenPPT）、HTML演示（走uiux-slides）。
  触发词：PPT Master、精致PPT、ChatPPT、专业PPT、定制PPT
tags:
  - ppt
  - presentation
  - ppt-master
  - slides
  - native
triggers:
  - PPT Master
  - 精致PPT
  - ChatPPT
  - 专业PPT
  - 定制PPT

---

# PPT Master Skill

## 安装位置

- 仓库: `~/Developer/ppt-master/`
- 依赖: 已安装（python-pptx, PyMuPDF, Pillow, edge-tts 等）
- 工作流技能: `skills/ppt-master/SKILL.md`

## 触发方式

本 skill 被 **smart-ppt** 统一入口调度，精致模式自动路由到 PPT Master。

不直接触发，通过入口说：
- `生成一个关于XXX的PPT` → 我选路由
- `精致模式，用PPT Master做一个XXX的PPT` → 直接走 PPT Master

## 使用方式

将 raw 材料（PDF/DOCX/图片）放入 `~/Developer/ppt-master/projects/` 目录，然后告诉我：

```
请用 projects/xxx/sources/xxx.pdf 生成一份PPT
```

## 工作流路线

PPT Master 提供 4 条路线，由 Agent 自动选择：

| 路线 | 场景 | 说明 |
|------|------|------|
| 直接生成 | 从资料/主题生成全新 PPT | 默认路线，AI 自由设计 |
| 套模板 | 填入你已有的 PPT 模板 | 保留原设计，填入新内容 |
| 创建模板 | 从参考资料提炼品牌模板 | 制作可复用的模板 |
| 增强 | 给已有 PPT 加转场/动画/旁白 | 增量增强 |

## 6 种设计风格

| 风格 | 适合场景 |
|------|---------|
| 杂志风 | 建筑/设计/摄影，编辑感 |
| 新闻/财经风 | 深色仪表盘，数据驱动 |
| 瑞士风 | 严格栅格，克制排版 |
| 毛玻璃 SaaS | 产品 UI 感，半透明叠层 |
| 孟菲斯波普 | 高饱和原色，活泼俏皮 |
| Risograph Zine | 双色印刷质感，手作文化 |

## 脚本路径

```bash
# 源材料转换
python ~/Developer/ppt-master/scripts/source_to_md.py <file>

# 项目管理
python ~/Developer/ppt-master/scripts/project_manager.py init <name> --format ppt169

# SVG → PPTX
python ~/Developer/ppt-master/scripts/svg_to_pptx.py <project_path>
```

## 注意事项

- 推荐模型: Claude Opus 或 Gemini 3.5 Flash（当前模型 deepseek-v4-flash 可能略逊）
- 需要材料放入 projects/ 目录
- 生成后输出在 exports/<name>_<timestamp>.pptx