# 全自动内容中台参考架构

本文件记录"全自动内容中台"技术方案的核心架构决策，作为同类内容管道系统的参考。

## 系统链路
巨量百应采集 → 飞书多维表格 → AI 分析 → Obsidian RAG 存储 → LibTV 知识图文 → Hermes Studio 审批

## 架构模式
- **事件驱动**：RabbitMQ 衔接所有服务，拒绝 HTTP 同步调用
- **Saga 模式**：长链路失败补偿，不追求分布式事务
- **扇出 (Fan-out)**：AI 分析完成后同时触发 RAG 入库和 LibTV 渲染

## 关键选型

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 消息队列 | RabbitMQ 3.13+ | 日均 < 1万条，AMQP 可靠性，运维简单 |
| 状态持久化 | PostgreSQL 16+ | 强事务 + JSONB，并发友好 |
| 向量索引 | FAISS → 后续 Milvus | 初期 < 10万条，避免额外运维 |
| 工作流编排 | Hermes Workflow | 已用 Hermes Studio，天然集成 LLM |
| 容器化 | Docker Compose → K3s | 小团队，K8s 成本 > 收益 |

## 服务划分 (8个独立服务)
1. **collector-srv** — 采集 + 反爬（占 35% 工作量）
2. **feishu-sync-srv** — 飞书维表读写 + 字段映射
3. **ai-analysis-srv** — Hermes Chat Run + 多 LLM Provider 主备
4. **rag-ingest-srv** — Obsidian MD + FAISS 索引
5. **libtv-render-srv** — LibTV API 渲染
6. **approval-srv** — Session 审批 + 超时降级
7. **orchestrator-srv** — 状态机 + Saga 重试
8. **cron-trigger** — 定时调度 + 巡检

## 三大技术难点
1. **反爬对抗**：real-browser-mcp + 代理池 + 账号池 + DOM checksum
2. **长链路一致性**：Saga 补偿 + PG 状态机 + 布隆过滤器去重
3. **LLM 不确定性**：三层防护（prompt engineering + 后处理校验 + 质量监控）
