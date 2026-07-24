---
name: prioritize-assumptions
description: >
  当用户需要进行产品管理中的prioritizeassumptions工作时使用。
  提供结构化模板和分析框架，帮助产品经理完成专业输出。
  不要用于：非产品管理场景、技术实现细节、代码编写。
  触发词：假设优先级、假设排序、风险×影响矩阵
tags:
  - pm-product-discovery
  - pm-skills
  - product-management
triggers:
  - 假设优先级
  - 假设排序
  - 风险×影响矩阵

---

# Prioritize Assumptions

## Prioritize Assumptions

Triage assumptions using an Impact × Risk matrix and suggest targeted experiments.

### Context

You are helping prioritize assumptions for **$ARGUMENTS**.

If the user provides files with assumptions or research data, read them first.

### Domain Context

**ICE** works well for assumption prioritization: Impact (Opportunity Score × # Customers) × Confidence (1–10) × Ease (1–10). Opportunity Score = Importance × (1 − Satisfaction), normalized to 0–1 (Dan Olsen). **RICE** splits Impact into Reach × Impact separately: (R × I × C) / E. See the `prioritization-frameworks` skill for full formulas and templates.

### Instructions

The user will provide a list of assumptions to prioritize. Apply the following framework:

1. **For each assumption**, evaluate two dimensions:
   - **Impact**: The value created by validating this assumption AND the number of customers affected (in ICE: Impact = Opportunity Score × # Customers)
   - **Risk**: Defined as (1 - Confidence) × Effort

2. **Categorize each assumption** using the Impact × Risk matrix:
   - **Low Impact, Low Risk** → Defer testing until higher-priority assumptions are addressed
   - **High Impact, Low Risk** → Proceed to implementation (low risk, high reward)
   - **Low Impact, High Risk** → Reject the idea (not worth the investment)
   - **High Impact, High Risk** → Design an experiment to test it

3. **For each assumption requiring testing**, suggest an experiment that:
   - Maximizes validated learning with minimal effort
   - Measures actual behavior, not opinions
   - Has a clear success metric and threshold

4. **Present results** as a prioritized matrix or table.

Think step by step. Save as markdown if the output is substantial.

---

### Further Reading

- [Assumption Prioritization Canvas: How to Identify And Test The Right Assumptions](https://www.productcompass.pm/p/assumption-prioritization-canvas)
- [Continuous Product Discovery Masterclass (CPDM)](https://www.productcompass.pm/p/cpdm) (video course)
