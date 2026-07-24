---
name: prioritize-features
description: >
  当用户需要进行产品管理中的prioritizefeatures工作时使用。
  提供结构化模板和分析框架，帮助产品经理完成专业输出。
  不要用于：非产品管理场景、技术实现细节、代码编写。
  触发词：功能优先级、需求排序、版本规划、Backlog优先级
tags:
  - pm-product-discovery
  - pm-skills
  - product-management
triggers:
  - 功能优先级
  - 需求排序
  - 版本规划
  - Backlog优先级

---

# Prioritize Features

## Prioritize Feature Backlog

Evaluate and rank a backlog of feature ideas to identify the top 5 to pursue.

### Context

You are helping prioritize features for **$ARGUMENTS**.

If the user provides files (spreadsheets, backlogs, opportunity assessments), read and analyze them directly.

### Domain Context

For framework selection guidance, see the `prioritization-frameworks` skill. Key recommendations:

**Opportunity Score** (Dan Olsen, *The Lean Product Playbook*) is recommended for evaluating customer problems: Opportunity Score = Importance × (1 − Satisfaction), normalized to 0–1. High Importance + low Satisfaction = best opportunities. Prioritize **problems (opportunities)**, not solutions.

**ICE** is recommended for quick scoring of initiatives: Impact (Opportunity Score × # Customers) × Confidence × Ease. **RICE** adds Reach as a separate factor for larger teams.

### Instructions

The user will describe their product objective, desired outcomes, and provide feature ideas. Work through these steps:

1. **Understand priorities**: Confirm the product objective and success metrics.

2. **Evaluate each feature** against:
   - **Impact**: How much does it move the needle on desired outcomes? Consider Opportunity Score if customer data is available.
   - **Effort**: How much development, design, and coordination is required?
   - **Risk**: How much uncertainty exists? What assumptions need testing?
   - **Strategic alignment**: How well does it fit the product vision and current goals?

3. **Recommend the top 5 features** with:
   - Clear ranking (1-5)
   - Brief rationale for each selection
   - Key trade-offs considered
   - What was deprioritized and why

4. **Present as a prioritization table** if helpful.

Think step by step. Save as markdown if the output is substantial.

---

### Further Reading

- [Kano Model: How to Delight Your Customers Without Becoming a Feature Factory](https://www.productcompass.pm/p/kano-model-how-to-delight-your-customers)
- [The Product Management Frameworks Compendium + Templates](https://www.productcompass.pm/p/the-product-frameworks-compendium)
- [Continuous Product Discovery Masterclass (CPDM)](https://www.productcompass.pm/p/cpdm) (video course)
