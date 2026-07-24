# Prompt Optimizer 优化工作流

## 标准三阶段流程

```
Phase 1: 优化
  User: "帮我优化提示词：XXX"
  Agent: 调用 optimize_user_prompt() → 输出优化版 + 优化说明
  User: 审阅

Phase 2: 迭代（按需循环）
  User: "第三段改一下，增加XX要求"
  Agent: 调用 iterate_prompt(当前版本, 反馈) → 输出新版
  User: "再改一下第二段的语气"
  Agent: 调用 iterate_prompt(当前版本, 反馈) → 输出新版
  ...直到用户满意

Phase 3: 执行
  User: "好了，执行吧"
  Agent: 使用最终确认的提示词执行任务
```

## 三种模式选择

| 模式 | 用途 | 命令 |
|------|------|------|
| `user` | 优化用户提示词（给最终用户的指令） | `prompt_optimizer.py user "..."` |
| `system` | 优化系统提示词（Agent的系统级指令） | `prompt_optimizer.py system "..."` |
| `iterate` | 根据反馈迭代已有版本 | `prompt_optimizer.py iterate "..." "反馈"` |

## 关键行为约束

- 优化引擎是 LLM API（custom:183399 + deepseek-v4-flash），不是独立 MCP 服务
- 每轮迭代保留原始意图，只增强结构/清晰度/可执行性
- 输出包含「优化后的提示词」和「优化说明」两部分
- 用户确认后才能执行，不能自动执行优化后的提示词
- 优化说明帮助用户理解改了什么、为什么改、预期效果
