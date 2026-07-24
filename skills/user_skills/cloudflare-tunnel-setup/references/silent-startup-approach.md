# Silent Cloudflare Tunnel Startup on Windows (2026-07 verified)

This document captures the exact approach used to run Cloudflare Tunnel silently on Windows 11 without any CMD window popup.

## Problem

When running `cloudflared.exe` directly from Task Scheduler, a CMD window pops up at login. The user wants zero visible window.

## Solution: Batch Cascade with Ping Delay

Two batch files in sequence:

### 1. `C:\Users\Admin\.cloudflared\start_tunnel.bat`
```batch
@echo off
cd /d "C:\Users\Admin\.cloudflared"
"C:\Program Files (x86)\cloudflared\cloudflared.exe" --config "C:\Users\Admin\.cloudflared\config.yml" tunnel run hermes-gateway-new
```

### 2. `C:\Users\Admin\.cloudflared\delayed_start.bat`
```batch
@echo off
ping 127.0.0.1 -n 11 > nul
call "C:\Users\Admin\.cloudflared\start_tunnel.bat"
```

### 3. Task Scheduler XML (import via `Register-ScheduledTask -Xml`)

Key settings:
- **Trigger:** `LogonTrigger` (NOT `BootTrigger`)
- **No `<Delay>` element** in XML — the batch handles delay via `ping`
- **RunLevel:** `LeastPrivilege` (NOT `Limited` — causes XML validation error)
- **No `LogonType` element** — omit entirely (Interactive is default)
- **Action:** `delayed_start.bat` directly (no `cmd /c` wrapper)

### Verification

```powershell
# After task runs, check:
Get-Process -Name cloudflared | Select-Object Id, MainWindowHandle
# MainWindowHandle = 0 means no window ✅
```

## Why This Works

- `ping 127.0.0.1 -n 11 > nul` — provides ~10 second delay without special XML characters
- `call start_tunnel.bat` — runs batch without spawning a new console window
- `delayed_start.bat` registered as Action directly — no `cmd /c` wrapper needed
- The batch file itself doesn't use `start /b` — it's called via `call` which inherits the parent's console (which is hidden by Task Scheduler)

## The 10-Second Delay Purpose

Hermes Studio takes ~5-10 seconds to start listening on port 8748 after login. If cloudflared connects before Hermes is ready, it shows `530 <none>` errors. The ping delay prevents this race condition.

## File Locations

| File | Path |
|------|------|
| Cloudflared EXE | `C:\Program Files (x86)\cloudflared\cloudflared.exe` |
| Config | `C:\Users\Admin\.cloudflared\config.yml` |
| Start script | `C:\Users\Admin\.cloudflared\start_tunnel.bat` |
| Delay script | `C:\Users\Admin\.cloudflared\delayed_start.bat` |
| Scheduled task | `HermesGatewayTunnel` (Task Scheduler root) |
