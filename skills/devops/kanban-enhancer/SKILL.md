---
name: kanban-enhancer
description: >
  Kanban 看板增强工具集。不修改 Hermes 核心代码，通过外部脚本 + cron 轮询
  在 Kanban 外围增加 4 项能力：(1) 工具亲和性检查——分派任务时检查 Profile 是否有对应工具
  (2) 结果标准化——强制 result 字段为 JSON 格式
  (3) 失败升级链——自动跨 Profile 升级失败任务
  (4) 验证门禁——为关键任务加 verify 环节
  不要用于：无 Kanban 的场景、单 Profile 任务。
  触发词：kanban增强、看板增强、kanban enhancer、检查看板
engine: cron
tags:
  - kanban
  - enhancement
  - architecture
triggers:
  - kanban增强
  - 看板增强
  - kanban enhancer
  - 检查看板
related_skills:
  - hermes-studio-ops
  - orchestrator-loop
---

# Kanban Enhancer — 看板增强工具

> 不修改 Hermes 核心代码，通过外部脚本 + cron 轮询在 Kanban 外围增加能力

## 架构

```
Kanban 增强器（cron 每5分钟轮询）
  │
  ├── tool_affinity.py
  │     └── 读取 Profile能力矩阵.md + 看板任务 → 检查工具匹配
  │
  ├── result_standardizer.py
  │     └── 读取已完成任务 → 强制 result 为 JSON 格式
  │
  ├── failure_escalator.py
  │     └── 读取失败任务 → 按升级链自动转移
  │
  └── verification_gate.py
        └── 读取已完成任务 → 创建验证子任务
```

## 状态文件

所有状态持久化在 `~/.kanban-enhancer-state.json`，格式：

```json
{
  "escalated_task_xxx": true,
  "verified_task_xxx": true,
  "last_run": "2026-07-24T10:00:00"
}
```

## 使用方式

### 手动运行

```
python scripts/kanban_enhancer.py
```

### 自动轮询

通过 cron job 每5分钟自动运行一次（见 `cron_setup` 部分）。

## 工具亲和性检查规则

当 Kanban 创建任务时，enhancer 检查分配的目标 Profile 是否拥有执行该任务所需的工具：

| 任务类型关键词 | 所需工具 | 允许的 Profile |
|--------------|---------|--------------|
| 爬取/采集/抓取/scrape/crawl | Apify MCP / Tabbit MCP | bigdata-director, default |
| 热点/热搜/趋势/trend | TrendRadar MCP | operations-director, default |
| 飞书/feishu/文档/表格/推送 | Feishu CLI / Docx API | operations-director, default |
| 代码/开发/重构/code/dev | OpenCode CLI | engineering-director, default |
| prd/产品/需求/用户/竞品 | pm-skills (68项) | product-manager, default |
| 测试/test/qa/质量/验证 | test-scenarios | qa-director, default |
| 磁盘/清理/维护/backup | 系统CLI | helper, default |
| 设计/ui/ux/配色/布局 | vision_analyze + image_generate | designer, default |
| 电商/淘宝/京东/抖音/数据 | Tabbit + Apify | bigdata-director, default |

## 失败升级链

```
Level 1: 原Profile重试2次（由Kanban内置failure_limit控制）
Level 2: 同级Profile接盘
  engineering-director ←→ qa-director（研发-测试互转）
  operations-director ←→ bigdata-director（运营-数据互转）
Level 3: 升级到default（人工介入，human_gate）
Level 4: 标记为blocked，通知用户
```

## 结果标准化格式

所有 Kanban 任务的 `result` 字段必须遵循以下 JSON 格式：

```json
{
  "status": "success | failed | partial",
  "summary": "简要描述执行结果（不超过500字）",
  "artifacts": [
    {"type": "feishu-table | file | url | image", "url": "..."},
    {"type": "file", "path": "C:/path/to/output"}
  ],
  "duration_seconds": 120,
  "errors": []
}
```

## 依赖

| 组件 | 用途 |
|------|------|
| Python 3.8+ | 运行脚本 |
| sqlite3 | 读取 Kanban DB（Python 内置） |
| Profile能力矩阵.md | 工具亲和性检查的数据源 |
| cron job | 每5分钟轮询 |

## 注意事项

1. 不修改 Hermes 核心代码，所有操作通过 Kanban CLI 和 SQLite 完成
2. 状态文件防重复处理，同一个任务不会重复升级
3. Kanban DB 使用 WAL 模式，读操作不会阻塞写操作
4. 每次运行输出报告，可通过飞书推送通知