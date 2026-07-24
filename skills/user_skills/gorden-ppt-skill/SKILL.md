---
name: GordenPPTSkill
description: >
  当用户需要gorden-ppt-skill时使用。
  不要用于：无关场景。
  触发词：GordenPPT、离线PPT、PPT模板、本地生成PPT
tags:
  - ppt
  - presentation
  - template
  - slides
  - office
triggers:
  - GordenPPT
  - 离线PPT
  - PPT模板
  - 本地生成PPT

---

# GordenPPT Skill

## 安装

仓库已克隆到 `~/Developer/GordenPPTSkill/`

依赖：`python-pptx`（已安装）

## 使用方法

### 方式一：通过本 Skill 生成

告诉我要做什么 PPT，我会：
1. 选择合适的模板
2. 生成内容大纲
3. 调用 `scripts/build_pptx.py` 生成 PPT
4. 提供下载路径

### 方式二：命令行直接生成

```bash
python ~/Developer/GordenPPTSkill/scripts/build_pptx.py \
    ~/Developer/GordenPPTSkill/templates/<模板名>/template.pptx \
    edits.json \
    output.pptx \
    --detail ~/Developer/GordenPPTSkill/templates/<模板名>/detail.json
```

## 可用模板

| 模板 | 风格 | 适用场景 |
|------|------|---------|
| `architecture-deck` | 架构风 | 技术方案/架构介绍 |
| `competition-speech` | 大赛风 | 路演/答辩/比赛 |
| `cute-orange-class` | 清新教学 | 教育培训/公开课 |
| `data-viz-deck` | 数据可视化 | 数据分析报告 |
| `geometric-summary` | 几何简约 | 商务汇报 |
| `mckinsey-style` | 麦肯锡风 | 咨询报告/战略规划 |
| `minimal-business-summary` | 极简商务 | 通用商务 |
| `operations-deck` | 运营风 | 运营方案/复盘 |
| `premium-corp` | 高端企业 | 企业介绍/品牌 |
| `quarterly-illust` | 季度插画 | 季度总结 |
| `red-patriot-*` | 党政风 | 党建/党政汇报 |
| `red-teaching-*` | 红色教学 | 思政教学 |
| `report-massive-*` | 超多图表 | 数据密集型报告 |
| `report-savior` | 拯救报告 | 快速美化 |
| `thesis-*` | 论文答辩 | 毕业论文/开题 |
| `top-thesis` | 顶尖论文 | 学位论文/答辩 |

## 效果展示

生成效果可参考 GitHub 仓库的截图（信息密度高、排版复杂、商务质感）。
