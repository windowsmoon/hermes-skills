---
name: tech-architecture-doc
description: >
  当用户需要tech-architecture-doc时使用。
  不要用于：无关场景。
  触发词：技术方案、架构设计、系统设计、技术文档
version: 1.0.0
author: Hermes Agent
platforms: [windows, linux, macos]
triggers:
  - user asks for '技术方案' or '架构设计文档'
  - user asks for '技术选型对比' or '架构评估'
  - user says '从技术负责人视角分析' or '从研发总监角度'
  - user provides a system design task and wants a formal document
  - user asks for '技术难点' + '风险评估' + '工时估算' together
tags: [architecture, design-doc, technical-writing, chinese, system-design, tech-lead]
---

# Technical Architecture Document (技术方案/架构设计文档)

Use this skill when the user asks you to write a formal technical architecture/design document, especially in Chinese and from a senior engineer/tech lead/director perspective.

## Core Document Structure

A comprehensive technical architecture document MUST cover these **6 dimensions**. The user may specify exactly these six; if they don't, include them proactively.

### 1. 技术架构图 (Architecture Diagram)
Describe the system architecture in text-based diagram form. Use:
- Layered architecture view: 编排层/业务逻辑层/基础设施层 (Orchestration/Core Services/Infrastructure)
- Component placement within each layer
- Data flow arrows between components
- External dependency boundaries
- Architecture principles table (e.g. 事件驱动/幂等设计/失败隔离/可观测)

Format: Use ASCII art box-drawing in code fences. Show clear top-to-bottom or left-to-right flow.

### 2. 组件拆分 (Component Breakdown)
Split the system into **independent deployable services/modules**. Each component needs:
- Name + responsibility (one clear sentence)
- Run mode (常驻/事件驱动/Cron任务)
- Dependencies on other components
- Design rationale for why it's standalone

Include a dependency graph showing inter-service relationships.

### 3. 技术选型 (Technology Stack Selection)
For each module, provide:
- **Technology** chosen (specific version)
- **Why** this choice over alternatives (对比论证)
- Key trade-offs called out explicitly

Include **ADR (Architecture Decision Records)** as an appendix for the most important decisions (e.g., RabbitMQ vs Kafka, FAISS vs Milvus, Hermes Workflow vs Airflow).

Format: Use a comparison table (对比维度 | RabbitMQ | Kafka) when doing head-to-head evaluations.

### 4. 技术难点 (Technical Challenges)
List the **top 3 hardest technical problems**, ordered by difficulty. For each:
- **问题描述**: Concrete scenario of the difficulty
- **应对方案**: Multi-layer mitigation strategy (layered defense)
- **工作量占比**: Estimate as % of total effort (e.g., "占 35%")

Common hard problems in content pipeline systems:
- Anti-crawling / WAF bypass for target platforms
- Long-chain eventual consistency across 5+ steps
- LLM output nondeterminism and quality control

### 5. 架构风险 (Architecture Risks)
Two required sub-sections:

**风险矩阵 (Risk Matrix)**: Table with columns: # | 风险 | 概率 | 影响 | 等级 | 应对措施. Classify as P0 (critical), P1 (high), P2 (medium).

**单点故障分析 (SPOF Analysis)**: List each component, note if it's an SPOF, and describe mitigation (e.g., single node dev → cluster production).

**数据一致性保障**: Cover dedup strategy, Saga compensation, periodic reconciliation, optimistic locking.

### 6. 工时估算 (Effort Estimation)
Two required tables:

**分模块估算**: Per-module breakdown: 模块 | 开发(人天) | 测试(人天) | 说明

**排期建议**: Phased timeline: 阶段 | 人天合计 | 建议人力 | 日历时间. Include:
- V1 MVP (core path)
- V1.1 (hardening)
- V1.2 (monitoring/CI/CD/docs)

Also include: 人力资源建议, 关键里程碑 (week-by-week breakdown).

## Additional Sections (Recommended)

### 可加可不加但推荐的内容
- **数据流设计**: Step-by-step flow of one complete transaction through the system
- **消息协议**: JSON schema for event/message payloads
- **失败重试策略**: Table of error types × retry mechanism × max retries × fallback
- **飞书维表数据模型**: If Feishu Bitable is used, show the field mapping table
- **ADR 附录**: Architecture Decision Records for the 3-5 most important decisions
- **时序图 (Sequence Diagram)**: ASCII or PlantUML showing cross-component interaction

## Writing Style for Chinese Technical Documents

- Use a professional, authoritative tone (技术负责人视角)
- Be precise and concrete: use specific numbers, versions, thresholds (e.g., "日均 < 1万条", "P99延迟", "> 50 个出口 IP")
- Contrast alternatives explicitly: not just "we chose X" but "why X over Y with evidence"
- Include explicit trade-offs (consequences of each decision)
- Use tables for comparison data, code blocks for schemas/protocols
- Section numbering (1, 1.1, 1.2) for easy reference in meetings

## Pitfalls to Avoid

- ❌ **Superficial tech selection**: Don't just list tech names — always justify with comparison
- ❌ **No numbers in risk/timeline**: Risk without probability/impact is not actionable; timeline without module breakdown is not credible
- ❌ **Ignoring failure modes**: Every step can fail — document retry/compensation/dead-letter for each
- ❌ **Missing SPOF analysis**: Always explicitly call out which components are single points of failure
- ❌ **Generic architecture**: Match the architecture style to the specific problem (event-driven for content pipeline, not REST synchronous)
- ❌ **Skipping ADRs**: Without decision records, the doc is just an essay with no traceability
- ❌ **Tool/environment dependency claims**: Don't claim "tool X doesn't work" as a persistent constraint — capture the fix, not the refusal

## Delivery

When delivering the document:
1. Write to a file with the user's preferred filename (Chinese or ASCII)
2. Tell the user which sections were included and any assumptions made
3. Offer to present the document to the team or refine specific sections
4. For file storage, use an ASCII-safe filename with a note about the Chinese document name

## References

The `references/` directory contains:
- `references/template-6section.md` — Standard 6-section architecture document template in Chinese

See these for renderer-specific help when diagrams are needed:
- `markdown-viewer` skill for PlantUML/Vega/architecture diagrams
- `hermes-studio-ops` skill for Hermes-specific operations
