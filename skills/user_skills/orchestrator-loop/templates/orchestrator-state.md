# Loop: {task_name}
Status: **running**
Updated: {timestamp}

## Phase: task-trigger ⏳
> 审批模型做 Prompt Engineering + Sequential Thinking → 输出 /goal
- Status: **pending**
- Retries: 0/3
- Output:

## Phase: moa-analysis ⏳
> MOA Mind-Daily(4模型) + Sequential Thinking → 5份 COT
- Status: **pending**
- Retries: 0/3
- Output:

## Phase: cot-selection 🟡
> 比对 COT + 流程图 → 你选定执行路径
- Status: **pending** ⚠️ 需审批
- Retries: 0/3
- Output:

## Phase: prep-info ⏳
> tavily 采集信息 → 筛选 → 注入流程图
- Status: **pending**
- Retries: 0/3
- Output:

## Phase: prep-tools 🟡
> 工具匹配表 → 你确认
- Status: **pending** ⚠️ 需审批
- Retries: 0/3
- Output:

## Phase: execute ⏳
> Phase 4 内部 Loop Engineering 逐节点执行
- Status: **pending**
- Retries: 0/3
- Output:

## Phase: report ⏳
> matplotlib 实际执行路径流程图
- Status: **pending**
- Retries: 0/3
- Output:

## Phase: retrospective ⏳
> 7维打分 + 归因分析 + 预判决策点
- Status: **pending**
- Retries: 0/3
- Output:
