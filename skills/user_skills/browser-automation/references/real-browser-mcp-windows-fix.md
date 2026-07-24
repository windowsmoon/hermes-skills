# real-browser-mcp Windows Bug Fix (2026-07-08)

## Problem

`bridge.js`'s `killStaleProcess()` uses the Linux/macOS command `lsof -ti :<port> -sTCP:LISTEN` to find and kill stale processes. On Windows, `lsof` does not exist — the error silently catches, the stale process is never killed, and the server crashes in an infinite EADDRINUSE loop:

```
[Bridge] Server error: listen EADDRINUSE: address already in use 127.0.0.1:7225
[Bridge] Port 7225 in use — killing stale process
'lsof' 不是内部或外部命令...   ← Chinese Windows error: "lsof is not recognized"
[real-browser-mcp] Fatal: Error: listen EADDRINUSE: address already in use 127.0.0.1:7225
```

This blocks Hermes's MCP client from ever connecting to the real-browser-mcp server.

## Solution

Patch `bridge.js` to add a Windows-specific `netstat + taskkill /F` fallback after the `lsof` block.

**File:** `D:\SetupProgram\real-browser-mcp-main\mcp-server\dist\bridge.js`

**Method to replace:** `killStaleProcess()` (search for the exact function body in the source)

### Replacement Code

```javascript
killStaleProcess() {
    try {
        // Try lsof first (Linux/macOS)
        try {
            const output = execSync(`lsof -ti :${this.port} -sTCP:LISTEN`, { encoding: 'utf8' }).trim();
            if (output) {
                for (const pid of output.split('\n')) {
                    const p = parseInt(pid, 10);
                    if (p && p !== process.pid) {
                        console.error(`[Bridge] Killing stale PID ${p}`);
                        process.kill(p, 'SIGTERM');
                    }
                }
                return;
            }
        }
        catch {
            // lsof not found or failed - try Windows method
        }
        // Windows: use netstat + taskkill
        try {
            const output = execSync(`netstat -ano | findstr :${this.port} | findstr LISTENING`, { encoding: 'utf8', shell: true }).trim();
            const lines = output.split('\n');
            for (const line of lines) {
                const parts = line.trim().split(/\s+/);
                const pidStr = parts[parts.length - 1];
                const pid = parseInt(pidStr, 10);
                if (pid && pid !== process.pid && parts[1] && parts[1].endsWith(`:${this.port}`)) {
                    console.error(`[Bridge] Killing stale PID ${pid} (Windows taskkill)`);
                    execSync(`taskkill /PID ${pid} /F`, { encoding: 'utf8', shell: true });
                    return;
                }
            }
        }
        catch {
            // taskkill returns non-zero if no match - that's fine
        }
    }
    catch (err) {
        console.error('[Bridge] killStaleProcess error:', err.message);
    }
}
```

## Verification

After patching, start Hermes Desktop fresh and check `C:\Users\Admin\AppData\Local\hermes\logs\mcp-stderr.log` for:

```
[Bridge] Killing stale PID <N> (Windows taskkill)
[Bridge] Listening on ws://localhost:7225
[real-browser-mcp] WebSocket listening on ws://localhost:7225
[real-browser-mcp] Waiting for Chrome extension...
[real-browser-mcp] MCP server connected
[Bridge] Extension connected
```

If you see "Extension connected" — the fix worked.

## After Hermes restarts

Hermes Desktop spawns MCP server processes on startup. If the previous session left a stale process on port 7225, Hermes will retry — but now the Windows taskkill fix properly cleans up the stale process each time, allowing a fresh server to start. No more infinite crash loop.

## Source

- `D:\SetupProgram\real-browser-mcp-main\mcp-server\dist\bridge.js`
- Original issue: GitHub ofershap/real-browser-mcp (no Windows lsof compatibility)