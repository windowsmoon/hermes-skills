# Standalone Coze API Script Pattern (urllib-only, zero dependencies)

A self-contained Python script that calls the Coze `stream_run` endpoint using only stdlib (`urllib`, `json`, `ssl`). No `requests` needed. Runnable with `uv run python` in any environment.

## When to use

- You need a reusable script to extract workflow output (e.g., Douyin transcript)
- The environment may not have `requests` installed
- You want a copy-pasteable script the user can run independently

## Complete template

```python
#!/usr/bin/env python3
import json, urllib.request, urllib.error, ssl, sys, os

API_URL = "https://api.coze.cn/v1/workflow/stream_run"
API_TOKEN = "sat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OUTPUT_FILE = "output.txt"

PAYLOAD = {
    "workflow_id": "7639942330812055558",
    "parameters": {
        "input": "https://v.douyin.com/xxxxxx/"
    }
}

def main():
    body = json.dumps(PAYLOAD).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=body,
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
    )
    ctx = ssl.create_default_context()

    all_contents = []
    current_event = ""
    current_data = ""

    def flush_event():
        nonlocal current_event, current_data
        if not current_data:
            return
        try:
            data = json.loads(current_data)
        except json.JSONDecodeError:
            return

        # Extract content from the event
        content = data.get("content", "")
        if content:
            # The content is often a JSON string with {"output": "..."}
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    output = parsed.get("output") or parsed.get("text") or ""
                    if output:
                        all_contents.append(output)
                    else:
                        all_contents.append(json.dumps(parsed, ensure_ascii=False, indent=2))
                elif isinstance(parsed, str):
                    all_contents.append(parsed)
                else:
                    all_contents.append(str(parsed))
            except (json.JSONDecodeError, TypeError):
                all_contents.append(content)

    try:
        resp = urllib.request.urlopen(req, context=ctx)
        buf = b""
        while True:
            chunk = resp.read(1)
            if not chunk:
                flush_event()
                break
            if chunk == b"\n":
                line = buf.decode("utf-8", errors="replace").strip()
                buf = b""
                if not line:
                    flush_event()
                    current_event = ""
                    current_data = ""
                    continue
                if line.startswith("event: "):
                    current_event = line[7:]
                elif line.startswith("data: "):
                    current_data = line[6:]
            else:
                buf += chunk
        resp.close()
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        sys.exit(1)
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)

    combined = "\n\n".join(all_contents)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(combined)
    print(f"Saved {len(combined)} chars to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
```

## Key points

| Aspect | Detail |
|--------|--------|
| URL | China: `api.coze.cn`, International: `api.coze.com` — SAT tokens are region-specific |
| Parameters | Send as a JSON object (not stringified) — the API accepts both formats |
| Version | `workflow_version` is optional; omit to use latest published version |
| SSE format | `event: Message` line + `data: {...}` line, separated by blank lines |
| Content nesting | `data.content` is often a JSON string containing `{"output": "..."}` |
| Output | Always extract `output` from the nested JSON for transcript workflows |

## Running the script

```bash
# On Windows (via uv):
uv run python /path/to/script.py

# Note: use `python` not `python3` — python3 is not available on this Windows setup
```

## SSE event structure (raw wire format)

```
event: Message
data: {"node_is_finish":true,"node_title":"End","content":"{\"output\":\"transcript text here\"}"}

event: Done
data: {"debug_url":"https://..."}
```

The blank line (`\n\n`) separates one complete SSE event from the next.