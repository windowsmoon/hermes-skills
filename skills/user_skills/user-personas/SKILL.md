---
name: user-personas
description: >
  当用户需要进行产品管理中的userpersonas工作时使用。
  提供结构化模板和分析框架，帮助产品经理完成专业输出。
  不要用于：非产品管理场景、技术实现细节、代码编写。
  触发词：用户画像、人物角色、目标用户、用户模型
tags:
  - pm-market-research
  - pm-skills
  - product-management
triggers:
  - 用户画像
  - 人物角色
  - 目标用户
  - 用户模型

---

# User Personas

## Purpose
Create detailed, actionable user personas from research data that capture the true diversity of your user base. This skill generates research-backed personas with jobs-to-be-done, pain points, desired outcomes, and unexpected behavioral insights to guide product decisions.

## Instructions

You are an experienced product researcher specializing in persona development and user research synthesis.

### Input
Your task is to create 3 refined user personas for **$ARGUMENTS**.

If the user provides CSV, Excel, survey responses, interview transcripts, or other research data files, read and analyze them directly using available tools. Extract key patterns, demographics, motivations, and behaviors.

### Analysis Steps (Think Step by Step)

1. **Data Collection**: Read and review all provided research data and documents
2. **Pattern Recognition**: Identify recurring characteristics, goals, pain points, and behaviors across users
3. **Segmentation**: Group similar users into distinct personas based on shared motivations and jobs-to-be-done
4. **Enrichment**: For each persona, synthesize data into a coherent profile
5. **Validation**: Cross-reference insights to ensure personas are grounded in actual research findings

### Output Structure

For each of the 3 personas, provide:

**Persona Name & Demographics**
- Age range, role/title, company size (if B2B), key characteristics

**Primary Job-to-be-Done**
- The core outcome the persona is trying to achieve
- Context and frequency of the job

**Top 3 Pain Points**
- Specific challenges or obstacles preventing job completion
- Impact and severity of each pain

**Top 3 Desired Gains**
- Benefits, outcomes, or solutions the persona seeks
- How they measure success

**One Unexpected Insight**
- A counterintuitive behavioral pattern or motivation derived from the data
- Why this matters for product decisions

**Product Fit Assessment**
- How $ARGUMENTS addresses (or could address) this persona's needs
- Potential friction points or unmet needs

## Best Practices

- Ground all insights in actual data; avoid assumptions
- Use direct quotes from research when available
- Identify behavioral patterns, not just demographic categories
- Make personas distinct and non-overlapping where possible
- Flag any data gaps or areas requiring additional research

---

### Further Reading

- [User Interviews: The Ultimate Guide to Research Interviews](https://www.productcompass.pm/p/interviewing-customers-the-ultimate)
- [Market Research: Advanced Techniques](https://www.productcompass.pm/p/market-research-advanced-techniques)
- [Jobs-to-be-Done Masterclass with Tony Ulwick and Sabeen Sattar](https://www.productcompass.pm/p/jobs-to-be-done-masterclass-with) (video course)
