# Cloudflare Tunnel Session Reference

Working configuration from `hermes.gzfuyaozhishang.com` setup (Windows 11, cloudflared 2026.6.1, 2026-07).

## Tunnels Available

| ID | NAME | Status |
|----|------|--------|
| `00f863c2-...` | hermes-gateway | No connections — do NOT use |
| `75be4c46-...` | hermes-gateway-new | **Active with 2-4 edges** ← USE THIS |

## config.yml (working)

```yaml
tunnel: 75be4c46-c4bd-4cf0-8a36-43535b0a440c
credentials-file: C:/Users/Admin/.cloudflared/75be4c46-c4bd-4cf0-8a36-43535b0a440c.json
protocol: http2
ingress:
  - hostname: hermes.gzfuyaozhishang.com
    service: http://localhost:8748
    originRequest:
      noTLSVerify: true
  - service: http_status:404
```

## Silent Startup Files (verified working, no CMD window)

### C:\Users\Admin\.cloudflared\start_tunnel.bat
```batch
@echo off
cd /d "C:\Users\Admin\.cloudflared"
"C:\Program Files (x86)\cloudflared\cloudflared.exe" --config "C:\Users\Admin\.cloudflared\config.yml" tunnel run hermes-gateway-new
```

### C:\Users\Admin\.cloudflared\delayed_start.bat
```batch
@echo off
ping 127.0.0.1 -n 11 > nul
call "C:\Users\Admin\.cloudflared\start_tunnel.bat"
```

### Task Scheduler: HermesGatewayTunnel (verified 2026-07)
- **Trigger:** LogonTrigger (fires after user login)
- **Action:** C:\Users\Admin\.cloudflared\delayed_start.bat
- **No `<Delay>` in XML** — batch handles the 10s delay via `ping`
- **MainWindowHandle = 0** — confirmed no CMD window appears

## Key Commands

```bash
# Run tunnel manually (works, foreground)
cloudflared --config ~/.cloudflared/config.yml tunnel run hermes-gateway-new

# Background run (Windows, Python subprocess)
subprocess.Popen(
    [cloudflared, '--config', config, 'tunnel', 'run', 'hermes-gateway-new'],
    cwd=r"C:\Users\Admin\.cloudflared",
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
)

# Check connections
cloudflared tunnel list
# CONNECTIONS column populated = success

# Test public access
curl -sI -k https://hermes.gzfuyaozhishang.com
# Expected: HTTP/1.1 200 OK, Server: cloudflare

# Tunnel detail
cloudflared tunnel info hermes-gateway-new
# Shows CONNECTOR IDs with ORIGIN IP (machine's public IP) and EDGE servers
```

## Hermes Studio Ports

- **Web UI:** `0.0.0.0:8748` (owned by `Hermes Studio.exe`, PID 4148)
- **Local health check:** `Invoke-WebRequest -Uri "http://localhost:8748"` → 200 OK
- cloudflared tunnel: `localhost:8748` → Cloudflare edge → public HTTPS

## File Paths

| File | Path |
|------|------|
| Cloudflared EXE | `C:\Program Files (x86)\cloudflared\cloudflared.exe` |
| Config | `C:\Users\Admin\.cloudflared\config.yml` |
| Credentials | `C:\Users\Admin\.cloudflared\75be4c46-c4bd-4cf0-8a36-43535b0a440c.json` |
| Old creds (don't use) | `C:\Users\Admin\.cloudflared\00f863c2-...json` |
| Scheduled task | `HermesGatewayTunnel` (in Task Scheduler root) |
| Cloudflared logs | Windows Event Log → Source: Cloudflared |

## What NOT to Use

- **JWT token (eyJh...):** This is NOT a credentials file. It contains a hex-encoded tunnel secret that needs conversion. Use the JSON credentials from Dashboard instead.
- **API token (cfut_...):** This is for Cloudflare API access, not `cloudflared tunnel run`. Cannot be used as tunnel credentials.
- **BootTrigger:** Fails silently with InteractiveToken — user hasn't logged in yet at boot time.
- **hermes-gateway tunnel (00f863c2):** No active connections, does not work.
- **cloudflared.exe directly in Task Scheduler Action:** Pops up a brief CMD window at login. Use the batch cascade instead.