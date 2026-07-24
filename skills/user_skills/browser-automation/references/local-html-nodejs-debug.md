# Local HTML+Node.js Server Debugging Patterns

## Project Layout Reference

### D:\Program\coding本地程序
- **Purpose**: Coze plugin Python code generator (curl → Python handler)
- **Files**: `server.js` (Node.js proxy), `27c4217bd2358ad6.html` (frontend)
- **Port**: 5000
- **Model**: `deepseek-v4-flash` via `api.183399.xyz/v1`
- **API Key**: `sk-1a1bda2f842562ad7361cc24b2e24d16852577771da119592d93587018946d44`

### D:\Program\插件
- **Purpose**: Coze plugin code generator UI (React SPA)
- **Files**: `server.js` (Node.js proxy), `index.html` (React SPA), `start.bat`
- **Port**: 5001
- **Model**: `deepseek-v4-flash` via `api.183399.xyz/v1`
- **API Key**: Same as above

Both servers use the same upstream API (`api.183399.xyz`) and share the same model/key.

## Key Debugging Patterns

### Pattern 1: "Loading..." forever despite server running

Root cause: JS syntax error before the fetch call. The browser stops at the error and never makes the request.

Common causes:
1. `apiKey: ***` — invalid JS (Python Ellipsis leaked into JS)
2. CDN 404 — React/ReactDOM version doesn't exist on jsdelivr
3. `file://` protocol — fetch('/api/...') resolves to file:///api/...

Diagnosis checklist:
```
[ ] Is server responding? curl http://localhost:PORT/
[ ] Is the HTML served correctly? Check Content-Type header
[ ] Is CDN React accessible? urllib.request.urlopen("https://cdn.jsdelivr.net/...", timeout=5)
[ ] Does the JS have syntax errors? Open DevTools F12 → Console
[ ] Is it file:// protocol? window.location.protocol === 'file:'
[ ] Are API keys/keys valid JS? open('file.html','rb') → search for ***, {{, ${ 
```

### Pattern 2: API returns 401

The Node.js server's default LLM API key is not set or the upstream provider requires auth differently.

Fix: Add `LLM_API_KEY = 'sk-...'` in server.js and use it as fallback:
```javascript
const authKey = apiKey || LLM_API_KEY;
```

Also check: if the original provider (e.g., `api.basui.online`) was switched, update BOTH the hostname AND the key.

### Pattern 3: Two servers on same machine

Always assign different ports. Check with:
```python
import socket
def port_in_use(port):
    s = socket.socket()
    s.settimeout(1)
    r = s.connect_ex(('localhost', port))
    s.close()
    return r == 0
```

### Pattern 4: HTML auto-redirect for file:// → localhost

Add to `<head>` of any standalone HTML file that uses a Node.js backend:
```html
<script>
if (window.location.protocol === 'file:') {
  window.location.href = 'http://localhost:PORT/page.html';
}
</script>
```

### Pattern 5: Binary replacement for corrupted text

When string replacement fails (e.g., API keys look identical but don't match), use binary:
```python
with open(path, 'rb') as f:
    raw = f.read()
raw = raw.replace(b'old_value', b'new_value')
with open(path, 'wb') as f:
    f.write(raw)
```

## Startup Automation

Add to Windows Startup (Start Menu folder) for auto-start:
```bat
@echo off
cd /d "D:\Program\插件"
start /b node server.js > nul
```

Startup folder: `C:\Users\Admin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`

## API Update Checklist

When updating an API configuration in server.js:
- [ ] LLM_API_BASE (URL)
- [ ] LLM_API_HOSTNAME (extracted from base URL)
- [ ] LLM_API_KEY (default key for proxy)
- [ ] LLM_MODEL (model name)
- [ ] Test with curl/http request (stream mode)