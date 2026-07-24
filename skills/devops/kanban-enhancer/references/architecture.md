# Kanban Enhancer 架构

> 最后更新：2026-07-24

## 为什么要做这个

Kanban 自带的 `todo→ready→running→done` 状态机缺少中间门禁，导致：

1. **工具不匹配**：decompose LLM 给 engineering-director 分配了一个需要 Tabbit 的任务，但 engineering-director 没有 Tabbit
2. **结果不可审计**：done 任务的 result 字段是自由文本，{"status": "ok"} 和 "完成了" 混在一起
3. **失败无升级**：任务失败就 stuck 在那，不会自动转给其他 Profile 尝试
4. **无验证环节**：没有 Maker/Checker 分离，自己写代码自己确认

## 设计方案

```
┌──────────────────────────────────────────────────────────────┐
│                   Kanban 原版状态机                          │
│   todo  ──→  ready  ──→  running  ──→  done                │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│               Kanban Enhancer（外围增强）                    │
│                                                              │
│   ① 创建任务时（triage/todo）                                │
│      → tool_affinity.py 检查分配是否合理                    │
│                                                              │
│   ② 任务完成时（done）                                       │
│      → result_standardizer.py 检查格式                      │
│      → verification_gate.py 生成验证子任务                  │
│                                                              │
│   ③ 任务失败时（blocked/failed）                             │
│      → failure_escalator.py 按链升级                        │
│                                                              │
│   ④ 任务超时时（running 超过4小时）                          │
│      → kanban_enhancer.py 标记为 stale                      │
└──────────────────────────────────────────────────────────────┘
```

## 核心原则

1. **不修改 Hermes 核心代码** — 所有操作通过 SQLite 只读 + Kanban CLI 完成
2. **状态文件驱动** — `~/.kanban-enhancer-state.json` 防重复处理
3. **渐进增强** — 先检测报警，再自动化操作
4. **Maker/Checker 分离** — 执行任务的人不验证，验证任务的人不执行

## 数据流

```
Kanban DB (SQLite)
  │ 只读查询
  ▼
Kanban Enhancer (Python)
  │ 分析结果
  ▼
标准输出 / 飞书推送 / 文件日志
  │
  ▼
你（default Profile）看到报告后决定操作
```

## 与现有系统的关系

| 组件 | 关系 |
|------|------|
| `orchestrator-loop` | Phase 3/4 使用 Kanban 调度，enhancer 作为补充监控层 |
| `Profile能力矩阵.md` | enhancer 读取此文件作为工具匹配的数据源 |
| `hermes-studio-ops` | 提供 Kanban 架构知识，enhancer 基于此设计 |
| cron job | 每5分钟运行一次 enhancer 脚本 |