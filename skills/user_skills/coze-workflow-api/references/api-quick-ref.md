# Coze Workflow API Quick Reference (Updated v4)

## Endpoints

| Purpose | Method | URL |
|---------|--------|-----|
| Execute workflow (streaming) | POST | `https://api.coze.cn/v1/workflow/stream_run` |
| Resume workflow | POST | `https://api.coze.cn/v1/workflow/stream_resume` |
| Get workflow info | GET | `https://api.coze.cn/v1/workflows/{workflow_id}` |
| Get versions | GET | `https://api.coze.cn/v1/workflows/{workflow_id}/versions` |

## Authentication

```
Authorization: Bearer {sat_xxx token}
Content-Type: application/json
```

## Execute Request Body

```json
{
  "workflow_id": "7657002468341006336",
  "workflow_version": "v0.0.8",
  "parameters": "{\"input\":\"雨水\",\"pics\":[],\"Voice\":\"\",\"check\":false,\"pre_WF\":{}}"
}
```

**⚠️ CRITICAL: `workflow_version` must be specified!**
Without it, Coze caches the old version. User wasted hours on v0.0.6 vs current v0.0.8.

## Resume Request Body

```json
{
  "workflow_id": "7657002468341006336",
  "event_id": "123/456",
  "interrupt_type": 2,
  "resume_data": "user reply",
  "workflow_version": "v0.0.8"
}
```

## SSE Event Types

| Event | Meaning | Action |
|-------|---------|--------|
| `Message` | Node output | Print `data.content` |
| `Interrupt` | Need user input | Extract question, wait for user |
| `Done` | Complete | End |
| `Error` | Failed | Report error |

## Interrupt Data Structure

```json
{
  "node_title": "问答",
  "interrupt_data": {
    "type": 2,
    "event_id": "765xxx/123",
    "data": "{\"content_type\":\"text\",\"content\":\"问题内容\"}"
  }
}
```

Extract question:
```python
interrupt_info = data.get("interrupt_data", {})
data_str = interrupt_info.get("data", "{}")
question = json.loads(data_str).get("content", data_str)
```

## Known Workflows

### 7657002468341006336 (test)

| Param | Type | Correct | Wrong |
|-------|------|---------|-------|
| input | string | `"雨水"` | - |
| pics | array | `[]` | `null`, missing |
| Voice | string | `""` | - |
| check | bool | `false` | `""` (causes `"can't convert to bool"`) |
| pre_WF | object | `{}` | - |

**⚠️ Common errors:**
- `value '' can't convert to bool` → check must be `false` (bool), not `""` (string)
- `Missing parameter: pics` → pics must be `[]` (array), not null

## Streaming Parse Template

```python
response = requests.post(url, headers=headers, json=payload, stream=True)
for line in response.iter_lines(decode_unicode=True):
    if line.startswith("event:"):
        current_event = line[6:].strip()
    elif line.startswith("data:"):
        data = json.loads(line[5:])
        if current_event == "Message":
            print(data.get("content", ""))
        elif current_event == "Interrupt":
            # ... wait for user
        elif current_event == "Done":
            print("\n✅ Done")
```

**⚠️ NO LLM PROCESSING of content. Direct passthrough only.**