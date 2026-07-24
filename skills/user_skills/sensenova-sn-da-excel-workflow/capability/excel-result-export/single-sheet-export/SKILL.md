---
name: excel-sheet-filter-export
description: 当用户需要将单Sheet Excel数据导出为文件时使用。 支持单Sheet导出、筛选后导出、指定列导出，处理大规模数据，输出结构化结果。 不要用于：多Sheet导出（走multi-sheet-export）、非Excel格式的数据处理。
  触发词：导出Excel、单Sheet导出、数据导出、指定列导出
triggers:
- 导出Excel
- 单Sheet导出
- 数据导出
- 指定列导出
tags:
- SKILL
- multi-sheet-export
- sheet
- excel
---

# Single Sheet Export

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

## Skill Steps

Step1 Receive filtered/cleaned DataFrame from upstream steps.

Step2 Export to Excel file with proper formatting (column width, headers, data types).

Step3 Provide download link to the generated file.
