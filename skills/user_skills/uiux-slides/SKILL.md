---
name: slides
description: >
  当用户需要uiuxslides时使用。
  提供专业的设计/内容/分析能力，支持定制化输出。
  不要用于：无关场景。
  触发词：HTML演示文稿、幻灯片、HTML幻灯片、演示页面
metadata:
  author: claudekit
  version: "1.0.0"
triggers:
  - HTML演示文稿
  - 幻灯片
  - HTML幻灯片
  - 演示页面
tags:
  - uiux-slides
  - slides

---

# Slides

Strategic HTML presentation design with data visualization.

## When to Use

- Marketing presentations and pitch decks
- Data-driven slides with Chart.js
- Strategic slide design with layout patterns
- Copywriting-optimized presentation content

## Subcommands

| Subcommand | Description | Reference |
|------------|-------------|-----------|
| `create` | Create strategic presentation slides | `references/create.md` |

## References (Knowledge Base)

| Topic | File |
|-------|------|
| Layout Patterns | `references/layout-patterns.md` |
| HTML Template | `references/html-template.md` |
| Copywriting Formulas | `references/copywriting-formulas.md` |
| Slide Strategies | `references/slide-strategies.md` |

## Routing

1. Parse subcommand from `$ARGUMENTS` (first word)
2. Load corresponding `references/{subcommand}.md`
3. Execute with remaining arguments
