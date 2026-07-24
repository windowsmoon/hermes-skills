---
name: coze-workflow-api
description: >
  当用户说"用扣子运行/执行"时，调用 Coze 工作流 API。
  
  Coze 的定位是"外挂插件箱"：
  - 复杂且需要稳定执行的自动化流程，用户已预置在 Coze 中
  - Coze 插件有未知的 API 和底层数据库，Hermes 无法复刻
  - 跑 Coze 工作流比写复杂 skill 更省 token
  - 用户已在 Coze 中完成完整思考，Hermes 只需纯管道取结果
  
  不要用于：
  - 部署到服务器（走 Hermes terminal）
  - 写代码/造工具（走 OpenCode / dev-pipeline-cli）
  - 简单的查询分析（Hermes 自己处理）
  - 任何需要 Hermes 推理的场景
  
  触发词：用扣子运行、用扣子执行、coze工作流、扣子工作流
version: "5.0.0"
tags:
  - coze
  - workflow
  - pure-pipe
  - plugin-box
triggers:
  - 用扣子运行
  - 用扣子执行
  - coze工作流
  - 扣子工作流

---

# Coze 工作流/对话流 Skill (v5.0)

## Coze 的定位（为什么用 Coze，而不是 Hermes 自己做）

```
Hermes skill 的问题：
  - 调用有随机性，同 prompt 可能跑出不同结果
  - 复杂 skill 写一堆逻辑，浪费 token
  - 很多 skill 功能太复杂，token 成本高

Coze 的优势：
  - 工作流执行极其稳定，无随机性
  - 用户已经在 Coze 里完成了完整的思考设计
  - 扣子有大量插件，API 未知、数据库未知，Hermes 无法复刻
  - 省 token：复杂逻辑在 Coze 跑，比 Hermes 写 skill 便宜
```

**核心原则：Coze 是外挂插件箱，不是第二个大脑。调用时纯管道取数据，Hermes 不加任何推理。**

## 交互流程

```
用户: "用扣子运行..." 或 "用扣子执行..."
    ↓
【命中已配置工作流？】
    ↓
✅ 是（内置列表有匹配的 workflow_id）
   → 直接用已存 ID + 版本
   → 询问 input 参数（如果用户没提供）
   ↓
❌ 否（未匹配）
   → 通过 API 搜索工作流 ID + 获取最新版本
   → 告知用户 ID + 版本
   → 询问入参
    ↓
【执行工作流】→ stream_run
    ↓
【实时返回 Coze 响应】（纯管道，不分析不推理）
    ↓
遇到 Interrupt → 【暂停，询问用户回复】→ 【Resume】→ 继续
遇到 Done → 【直接输出结果，结束】
```

## 纯管道原则（严格禁止违反）

```
❌ 禁止做的事：
  1. 不要对 Coze 输出进行总结
  2. 不要解释 Coze 的回答
  3. 不要"思考"下一步该做什么
  4. 不要等待模型推理后再输出
  5. 不要加自己的分析或建议

✅ 正确做法：
  1. Coze 返回 → 立即打印给用户
  2. 遇到 Interrupt → 立即暂停问用户
  3. 用户回复 → 立即 Resume
  4. 遇到 Done → 立即结束
```

## 详细流程

### Step 1: 询问工作流名称

当用户说 "用扣子运行..." 或 "用扣子执行..." 时：

```
⏸️ 请告诉我要运行的工作流名称：
```

### Step 2: 搜索工作流

```python
import requests
import json

API_TOKEN = "sat_1PpkmE68m9HDTHdwilucRZXf7Hr0e7E9rb2VjQif2PcQPBWql0tSoM5NpY6chi1J"

def search_workflow(name):
    url = "https://api.coze.cn/v1/workflows"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, params={"page_size": 50})
    if response.status_code == 200:
        data = response.json()
        workflows = data.get("data", {}).get("items", [])
        matches = []
        for wf in workflows:
            if name.lower() in wf.get("workflow_name", "").lower():
                matches.append(wf)
        return matches
    return []
```

### Step 3: 获取最新版本

```python
def get_latest_version(workflow_id):
    url = f"https://api.coze.cn/v1/workflows/{workflow_id}/versions"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        versions = response.json().get("data", {}).get("items", [])
        if versions:
            latest = sorted(versions, key=lambda x: x.get("updated_at", 0), reverse=True)
            return latest[0].get("version")
    return "v0.0.1"
```

### Step 4: 询问入参

```
✅ 找到工作流：[名称]
📋 Workflow ID：[ID]
📦 最新版本：[版本号]

请提供入参数据：
```

### Step 5: 执行工作流（stream_run）

```python
def execute_workflow(workflow_id, version, params):
    url = "https://api.coze.cn/v1/workflow/stream_run"
    return requests.post(url,
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={
            "workflow_id": workflow_id,
            "workflow_version": version,
            "parameters": json.dumps(params)
        },
        stream=True)
```

### Step 6: 纯管道响应

```python
def parse_and_print(response):
    messages = []
    debug_url = None
    current_event = ""
    current_data = ""

    for line in response.iter_lines(decode_unicode=True):
        if not line:
            if current_event:
                flush_event(...)
            current_event = ""
            current_data = ""
            continue
        if line.startswith("event: "):
            current_event = line[7:]
        elif line.startswith("data: "):
            current_data = line[6:]

    # 直接输出，不分析不推理
    print("\n\n".join(messages))
    return None, None
```

### Step 7: Resume

```python
def resume_workflow(workflow_id, version, event_id, interrupt_type, resume_data):
    url = "https://api.coze.cn/v1/workflow/stream_resume"
    return requests.post(url,
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={
            "workflow_id": workflow_id,
            "event_id": event_id,
            "interrupt_type": interrupt_type,
            "resume_data": resume_data,
            "workflow_version": version
        },
        stream=True)
```

## 执行前自动同步

每次执行前必须调用 Coze API 获取该 workflow 的**最新版本号**，覆盖内置版本：

```python
latest_ver = get_latest_version(WORKFLOW_ID)
if latest_ver:
    WORKFLOW_VERSION = latest_ver
```

## SSE 解析常见陷阱

**事件名在 `event:` 行，数据在 `data:` 行，不要混在一起解析。**

```python
# ❌ 错误：在 data JSON 里找 event 字段（event 在上一行）
# ✅ 正确：跨行追踪 event 和 data
current_event = ""
current_data = ""
for line in resp.iter_lines(decode_unicode=True):
    if not line:
        flush_event()
        current_event = ""
        current_data = ""
        continue
    if line.startswith("event: "):
        current_event = line[7:]
    elif line.startswith("data: "):
        current_data = line[6:]
```

## 参考文件

- `references/api-quick-ref.md` — API 端点、请求格式、SSE 解析、已知工作流参数
- `references/standalone-script-pattern.md` — 零依赖 standalone 脚本模板
- `references/why-coze-not-hermes.md` — Coze 定位说明：为什么用 Coze 而不是 Hermes skill