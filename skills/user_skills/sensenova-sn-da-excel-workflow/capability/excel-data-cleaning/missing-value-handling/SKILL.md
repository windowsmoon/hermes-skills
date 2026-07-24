---
name: excel-smart-analysis-and-cleaning
description: 当用户需要进行Excel数据清洗中的缺失值处理时使用。 支持缺失值检测、填充、删除、插值处理，处理大规模数据，输出结构化结果。 不要用于：非Excel格式的数据处理、图片处理、文本编辑。 触发词：缺失值处理、空值填充、缺失数据、Null值处理
triggers:
- 缺失值处理
- 空值填充
- 缺失数据
- Null值处理
tags:
- SKILL
- 'null'
- excel
---

# Missing Value Handling

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

## Skill Steps

Step1 Scan all sheets and detect missing values in target columns.

Step2 Apply appropriate handling strategy (fill with mean/median/mode, drop rows, or interpolate).

Step3 Export cleaned results with highlighted changes.
