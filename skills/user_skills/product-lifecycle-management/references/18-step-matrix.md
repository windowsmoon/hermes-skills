# 18步产品生命周期矩阵

## 四阶段结构

| 阶段 | # | 步骤 | ID | 技能 | 产出物 |
|------|---|------|----|------|--------|
| **1. 战略洞察期** | 1 | 产品愿景 | p1s1 | product-vision | Mission Statement |
| | 2 | SWOT分析 | p1s2 | swot-analysis | 优劣势威胁矩阵 |
| | 3 | 市场细分 | p1s3 | market-segments | 目标细分市场 |
| | 4 | 竞品分析 | p1s4 | competitor-analysis | 竞品定位空白点 |
| | 5 | 用户调研 | p1s5 | analyze-feature-requests | 未满足痛点清单 |
| | 6 | 用户画像 | p1s6 | user-personas | 典型Persona |
| **2. 定义聚焦期** | 7 | 战略画布 | p2s1 | (通用方法论) | 价值曲线图 |
| | 8 | 定位 | p2s2 | positioning-ideas | 核心差异化口号 |
| | 9 | 北极星指标 | p2s3 | north-star-metric | 长期健康指标 |
| | 10 | 机会树 | p2s4 | opportunity-solution-tree | 可拆解指标+杠杆 |
| | 11 | 功能优先级 | p2s5 | prioritize-features | MVP Backlog |
| **3. 落地执行期** | 12 | 写PRD | p3s1 | create-prd | 8段式PRD文档 |
| | 13 | 用户故事 | p3s2 | user-stories | 开发任务拆分 |
| | 14 | Sprint规划 | p3s3 | sprint-plan | 迭代计划 |
| | 15 | 测试场景 | p3s4 | test-scenarios | 验收用例集 |
| | 16 | NDA/隐私终审 | p3s5 | draft-nda | 合规文件 |
| **4. 上市增长期** | 17 | GTM策略 | p4s1 | gtm-strategy | 定价/渠道/推广计划 |
| | 18 | 增长飞轮 | p4s2 | growth-loops | 留存自传播正循环 |

## 状态机命令速查

| 命令 | 用途 | 示例 |
|------|------|------|
| `start <产品名>` | 初始化新产品 | `start 智能客服助手` |
| `next` | 推进到下一步 | `next` |
| `status` | 查看当前位置/进度 | `status` |
| `rollback` | 回退一步 | `rollback` |
| `step <step_id>` | 跳转到指定步骤 | `step p2s3` |
| `list` | 显示全部18步 | `list` |
| `reset` | 重置状态机 | `reset` |
| `set-output <k> <v>` | 记录产出物 | `set-output p1s1 愿景文档已完成` |

## 状态文件结构

路径: `~/.product-lifecycle-state.json`

```json
{
  "product_name": "智能客服助手",
  "status": "running",
  "current_phase": 0,
  "current_step": 1,
  "completed_steps": ["p1s1"],
  "outputs": {"p1s1": "愿景文档已完成"},
  "delegations": {}
}
```

## 多Agent委托触点

阶段3（落地执行期）完成后，状态机标记 `delegate_to: [engineering-director, qa-director]`：

1. `delegate_task(goal="评估PRD技术方案, 输出工时评估", context=<PRD内容>, role="orchestrator")` → engineering-director
2. `delegate_task(goal="评审测试场景, 补充边界用例", context=<测试场景>, role="orchestrator")` → qa-director
3. 等待返回 → 合并到 state["outputs"]
