# 内容中台 Loop 示例

全自动内容中台设计方案，用 Loop Engine 实现的多角度分析 → 冲突检测 → 审批 → 执行流水线。

## 架构

```
load(读任务) → analyze(多角度分析+冲突检测) → resolve(冲突解决) → report(审批门禁) → execute(分派执行)
```

## 步骤

| Phase | Maker | Checker | Gate | 描述 |
|:------|:------|:--------|:----|:-----|
| load | 读任务输入文件 | 字符数>0 | — | 初始化 |
| analyze | 5角度分析+冲突检测 | 至少3个视角完成 | — | 产品/技术/质量/运营/数据 |
| resolve | 自动/群聊解决冲突 | — | — | 无冲突可跳过 |
| report | 生成最终报告 | — | ✅ human_gate | 等你审批 |
| execute | 分派便宜模型执行 | — | — | 5个模块并行 |

## 多角度分析 Maker 示例

```python
def maker_analyze(ctx):
    perspectives = ["产品", "技术", "质量", "运营", "数据"]
    results = {}
    for p in perspectives:
        # 直接分析（不派子Agent）
        result = ctx["tools"]["analyze"](task, perspective=p)
        results[p] = result
        # 立即写盘——不会丢
        import json
        with open(f"analysis_{p}.json", "w") as f:
            json.dump(result, f)
    
    # 检测冲突
    conflicts = detect_conflicts(results)
    
    return StepResult(data={
        "analysis": results,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
    })
```

## 冲突检测 Checker 示例

```python
def detect_conflicts(analysis):
    conflicts = []
    # 工时冲突
    if analysis.get("product", {}).get("days") and analysis.get("tech", {}).get("days"):
        ratio = analysis["tech"]["days"] / analysis["product"]["days"]
        if ratio > 2:
            conflicts.append({
                "type": "effort_estimate",
                "detail": f"Product estimates {analysis['product']['days']}d vs Tech {analysis['tech']['days']}d",
                "resolution": "Product is MVP, Tech is full scope. Use phased approach."
            })
    # 架构冲突
    # ... 更多冲突检测规则
    return conflicts
```

## 执行状态文件

运行后在 `C:\Users\Admin\AppData\Local\hermes\cache\content-pipeline-state.md`。
