---
name: sprint-plan
description: >
  当用户需要进行产品管理中的sprintplan工作时使用。
  提供结构化模板和分析框架，帮助产品经理完成专业输出。
  不要用于：非产品管理场景、技术实现细节、代码编写。
  触发词：Sprint规划、迭代计划、冲刺计划、任务分配
tags:
  - pm-execution
  - pm-skills
  - product-management
triggers:
  - Sprint规划
  - 迭代计划
  - 冲刺计划
  - 任务分配

---

# Sprint Plan

## Sprint Planning

Plan a sprint by estimating team capacity, selecting and sequencing stories, and identifying risks.

### Context

You are helping plan a sprint for **$ARGUMENTS**.

If the user provides files (backlogs, velocity data, team rosters, or previous sprint reports), read them first.

### Instructions

1. **Estimate team capacity**:
   - Number of team members and their availability (PTO, meetings, on-call)
   - Historical velocity (average story points per sprint from last 3 sprints)
   - Capacity buffer: reserve 15-20% for unexpected work, bugs, and tech debt
   - Calculate available capacity in story points or ideal hours

2. **Review and select stories**:
   - Pull from the prioritized backlog (highest priority first)
   - Verify each story meets the Definition of Ready (clear AC, estimated, no blockers)
   - Flag stories that need refinement before committing
   - Stop adding stories when capacity is reached

3. **Map dependencies**:
   - Identify stories that depend on other stories or external teams
   - Sequence dependent stories appropriately
   - Flag external dependencies and owners
   - Identify the critical path

4. **Identify risks and mitigations**:
   - Stories with high uncertainty or complexity
   - External dependencies that could slip
   - Knowledge concentration (only one person can do it)
   - Suggest mitigations for each risk

5. **Create the sprint plan summary**:

   ```
   Sprint Goal: [One sentence describing what success looks like]
   Duration: [2 weeks / 1 week / etc.]
   Team Capacity: [X story points]
   Committed Stories: [Y story points across Z stories]
   Buffer: [remaining capacity]

   Stories:
   1. [Story title] — [points] — [owner] — [dependencies]
   ...

   Risks:
   - [Risk] → [Mitigation]
   ```

6. **Define the sprint goal**: A single, clear sentence that captures the sprint's primary value delivery.

Think step by step. Save as markdown.

---

### Further Reading

- [Product Owner vs Product Manager: What's the difference?](https://www.productcompass.pm/p/product-manager-vs-product-owner)
