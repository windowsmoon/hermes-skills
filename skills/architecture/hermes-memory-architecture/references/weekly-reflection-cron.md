# Weekly Memory Reflection Cron

> Configured: 2026-07-22
> Schedule: Every Sunday at 8 PM (0 20 * * * 0)
> Job ID: c9513d1d9d85

## Purpose

Automatically distill general rules from recent experience entries in MEMORY.md.

## Behavior

1. Read MEMORY.md
2. Find all entries tagged with `[experience]` from the past 7 days
3. For each experience, distill a general rule or principle
4. Write distilled rules under `[rule]` tag with date
5. Report new rules to user

## Example

Input (MEMORY.md):
```
§ [experience] delegate_task 子Agent 经常不返回 → 改用 Loop Engine
§ [experience] apikey-image-gen description 太短导致触发不了
```

Output (appended to MEMORY.md):
```
§ [rule] 2026-07-22: 关键任务不要用 delegate_task，改用 Loop Engine 状态文件驱动
§ [rule] 2026-07-22: Skill description 必须 >20 字符且包含明确触发词
```
