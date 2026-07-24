---
name: cloudflare-tunnel-setup
description: >
  当用户需要将本地服务通过Cloudflare Tunnel暴露到公网时使用。
  覆盖：诊断、Windows服务配置、开机自启、子域名配置、常见坑点排查。
  不要用于：其他隧道工具（ngrok/frp/localhost.run）、CDN加速配置。
  触发词：Cloudflare Tunnel、内网穿透、暴露本地服务、配置域名、cloudflared
triggers:
  - "cloudflared"
  - "cloudflare tunnel"
  - "expose local service public"
  - "cloudflare access"
  - "tunnel to public internet"
  - "hermes.gzfuyaozhishang.com"
  - "no CMD window"
  - "silent background"
tags:
  - cloudflare-tunnel-se
  - cloudflare

---

# Cloudflare Tunnel Setup

Expose a local HTTP service to the public internet via Cloudflare Tunnel (cloudflared), routing through your own domain name.

## Quick Diagnosis Checklist

1. **Cloudflared installed?** `where cloudflared` → path exists
2. **Tunnel exists?** `cloudflared tunnel list`
3. **Tunnel credentials file exists?** `~/.cloudflared/<tunnel-uuid>.json`
4. **config.yml exists?** `~/.cloudflared/config.yml` with correct `ingress` rules
5. **Local target service running?** `curl localhost:<port>` → HTTP 200
6. **cloudflared process running?** `Get-Process -Name cloudflared`
7. **Tunnel has connections?** `cloudflared tunnel list` → CONNECTIONS column populated

## Standard Setup (Linux/macOS)

```bash
# 1. Install
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared

# 2. Create tunnel
cloudflared tunnel create my-tunnel
# → saves credentials to ~/.cloudflared/<uuid>.json

# 3. Configure DNS and ingress in ~/.cloudflared/config.yml
# cat > ~/.cloudflared/config.yml << 'EOF'
# tunnel: <uuid>
# credentials-file: /root/.cloudflared/<uuid>.json
# ingress:
#   - hostname: my.example.com
#     service: http://localhost:8748
#   - service: http_status:404
# EOF

# 4. Route DNS CNAME to tunnel
cloudflared tunnel route dns my-tunnel my.example.com

# 5. Run
cloudflared service install   # as systemd service (Linux)
# OR
cloudflared tunnel run my-tunnel  # foreground / in screen
```

## Windows Setup (where things get tricky)

### The Service Install Trap

`cloudflared service install` on Windows installs a **bare service** pointing only to `cloudflared.exe` with **no arguments** — it does NOT read `~/.cloudflared/config.yml` automatically, and it does NOT run a tunnel.

**Diagnosis:** Check the service PathName:
```powershell
(Get-WmiObject Win32_Service -Filter "Name='Cloudflared'").PathName
# Shows: "C:\Program Files (x86)\cloudflared\cloudflared.exe"
# Missing: --config and tunnel name → tunnel will NOT run
```

### Three Working Windows Startup Approaches

#### Option A: Task Scheduler with batch cascade (silent, no CMD window) [RECOMMENDED]

This approach avoids any CMD window popup. Uses two batch files in a cascade.

**Script files** (shipped with this skill at `skills/cloudflare-tunnel-setup/scripts/`):

**`~/.cloudflared/start_tunnel.bat`:**
```batch
@echo off
cd /d "%USERPROFILE%\.cloudflared"
"C:\Program Files (x86)\cloudflared\cloudflared.exe" --config "%USERPROFILE%\.cloudflared\config.yml" tunnel run YOUR-TUNNEL-NAME
```

**`~/.cloudflared/delayed_start.bat`:**
```batch
@echo off
ping 127.0.0.1 -n 11 > nul
call "%USERPROFILE%\.cloudflared\start_tunnel.bat"
```

**Task Scheduler XML (silent, 10s delay after login):**
```powershell
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Cloudflare Tunnel - silent background</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$user</UserId>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <RestartOnFailure><Interval>PT1M</Interval><Count>5</Count></RestartOnFailure>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>C:\Users\<USER>\.cloudflared\delayed_start.bat</Command>
      <Arguments></Arguments>
      <WorkingDirectory>C:\Users\<USER>\.cloudflared</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

$xml | Out-File -FilePath "$env:TEMP\cf-silent.xml" -Encoding Unicode
Register-ScheduledTask -Xml (Get-Content "$env:TEMP\cf-silent.xml" -Raw) -TaskName "YOUR-TASK-NAME" -Force

# Verify
Get-ScheduledTask -TaskName "YOUR-TASK-NAME"
Start-ScheduledTask -TaskName "YOUR-TASK-NAME"

# Confirm no window: MainWindowHandle should be 0
Start-Sleep 15
Get-Process -Name cloudflared | Select-Object Id, MainWindowHandle
# If MainWindowHandle = 0 → silent ✅
```

**Why this works without a CMD window:**
- `ping 127.0.0.1 -n 11 > nul` — delay without special XML characters
- `call start_tunnel.bat` — batch runs without spawning a visible console
- `delayed_start.bat` is registered as the Action target directly — no `cmd /c` wrapper needed
- `RunLevel: LeastPrivilege` (NOT `Limited` — `Limited` causes XML validation error on some Windows 11 builds)
- The batch file itself uses `start /b` or is called via `call` so no new window spawns

**Known Windows XML pitfalls:**
- `RunLevel: Limited` → "invalid value" error on some Win11 builds → use `LeastPrivilege`
- `LogonType: InteractiveToken` → causes "invalid value" on XML import → omit the element entirely (Interactive is the default)
- `Delay: PT10S` format → causes "invalid value" on XML import → handle delay inside the batch via `ping` instead, omit `<Delay>` from XML
- `Arguments` with `&` or `>` characters → causes "malformed" error → move logic into separate batch files
- PowerShell `New-ScheduledTaskPrincipal -LogonType Interactive` → parameter name changes across PS versions → use XML import instead

**Tested verification commands:**
```powershell
# Confirm silent (MainWindowHandle=0 means no window)
Get-Process -Name cloudflared | Select-Object Id, MainWindowHandle
# Expected: PID listed, MainWindowHandle = 0

# Confirm connections
cloudflared tunnel list
# CONNECTIONS column populated

# Confirm public access
curl -sI -k https://your-domain.com
# Expected: HTTP/1.1 200 OK
```

#### Option B: Task Scheduler (direct, no batch) [alternative]

If you don't mind a brief CMD window, run cloudflared directly:
```powershell
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers>
  <Principals><Principal id="Author"><UserId>$user</UserId><LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals>
  <Settings><StartWhenAvailable>true</StartWhenAvailable><RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable><RestartOnFailure><Interval>PT1M</Interval><Count>5</Count></RestartOnFailure></Settings>
  <Actions Context="Author"><Exec><Command>C:\Program Files (x86)\cloudflared\cloudflared.exe</Command><Arguments>--config "C:\Users\<USER>\.cloudflared\config.yml" tunnel run TUNNEL-NAME</Arguments><WorkingDirectory>C:\Users\<USER>\.cloudflared</WorkingDirectory></Exec></Actions>
</Task>
"@

$xml | Out-File -FilePath "$env:TEMP\cf-task.xml" -Encoding Unicode
Register-ScheduledTask -Xml (Get-Content "$env:TEMP\cf-task.xml" -Raw) -TaskName "YOUR-TASK-NAME" -Force
```

Key settings:
- `LogonTrigger` — fires after user login (NOT `BootTrigger`, which silently fails because there's no user session at boot time)
- `InteractiveToken` — requires user to be logged in
- `StartWhenAvailable: true` — catch up if task was missed
- `RestartOnFailure` with `Count: 5, Interval: PT1M` — auto-retry on failure

#### Option C: batch wrapper + sc create

Create `~/.cloudflared/run-tunnel.bat`:
```batch
@echo off
cd /d "%USERPROFILE%\.cloudflared"
"C:\Program Files (x86)\cloudflared\cloudflared.exe" --config config.yml
```

Then create service (NOTE: path must NOT be quoted in `binpath=`):
```cmd
sc create CloudflaredTunnel binpath= C:\Users\<USER>\.cloudflared\run-tunnel.bat displayname= "Cloudflare Tunnel" start= auto type= own
net start CloudflaredTunnel
```

### Verify Cloudflared Is Connected

```powershell
# Check process running
Get-Process -Name cloudflared | Select-Object Id, Path

# Check tunnel has connections
cloudflared tunnel list
# CONNECTIONS column should show edge IPs, not blank

# Check domain accessible
curl -sI -k https://your-domain.com
# Expected: HTTP/1.1 200 OK  Server: cloudflare
```

## Emergency Fix: Tunnel Down / Not Running

**Diagnosis (2026-07-08):**
```powershell
# 1. Check if tunnel process is running
Get-Process -Name cloudflared
# → Empty = tunnel is NOT running

# 2. Check public URL
curl -sI -k https://your-domain.com
# → 530 = tunnel has no connections (process dead or never started)

# 3. Check config
type $HOME\.cloudflared\config.yml
```

**Quick Fix (foreground start):**
```powershell
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" --config "$HOME\.cloudflared\config.yml" tunnel run YOUR-TUNNEL-NAME
# This starts the tunnel in the foreground — verify with: curl -sI -k https://your-domain.com
# Expected: HTTP/1.1 200 OK
```

**Auto-start on login (Task Scheduler, silent, 10s delay):**
```powershell
# Create XML task (see full Option A in Windows Setup section above)
# Key: use delayed_start.bat (ping 127.0.0.1 -n 11) as the Action target
# This gives Hermes Studio time to start on port 8748 before the tunnel connects
```

**Why the delay matters:** Hermes Studio takes ~5-10 seconds to start on port 8748. If the tunnel connects before Hermes is ready, it shows `530 <none>` errors. The 10-second ping delay in `delayed_start.bat` prevents this race condition.

## Credentials File Formats

### Standard Credentials JSON (from Dashboard download)
```json
{
  "AccountTag": "4261db388a646ea3179f84c75a839a5b",
  "TunnelSecret": "SfxpfC7FT67sYYWMdnYzJ2nC8Q3yN79YKzfeVthnblk=",
  "TunnelID": "75be4c46-c4bd-4cf0-8a36-43535b0a440c",
  "Endpoint": ""
}
```
`TunnelSecret` is raw base64-encoded bytes (32 bytes ≈ 44 base64 chars). Download this directly from the Cloudflare Dashboard → Networks → Tunnels → Access Tunnel → grab the `.json` file.

### JWT-Style Credentials Token (alternative Dashboard export)
The token is a base64-encoded JSON: `{"a":"<account-id>","t":"<tunnel-id>","s":"<hex-secret>"}`
- `s` is a hyphenated hex string (e.g. `086b5031-7cff-43fd-b42b-c9a71628b3a5`). Convert it:
  1. Remove hyphens → 64-char hex string → 32 raw bytes
  2. `bytes.fromhex(hex_clean)` → base64.b64encode → use as `TunnelSecret`

### API Token (cfut_...) — NOT tunnel credentials
The `cfut_...` API token is for Cloudflare API access, NOT for `cloudflared tunnel run`. It cannot be used directly as tunnel credentials. Use the credentials `.json` file from the Dashboard instead.

## Hermes Studio-Specific Notes

**Port:** Hermes Studio listens on `0.0.0.0:8748` (owned by `Hermes Studio.exe` process). Confirm with:
```powershell
Get-NetTCPConnection -State Listen | Where-Object {$_.LocalPort -eq 8748}
```

**Working config.yml (hermes-gateway-new):**
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

**Test local backend:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8748" -Method HEAD -TimeoutSec 5
# Expected: StatusCode 200
```

**Test public access:**
```bash
curl -sI -k https://hermes.gzfuyaozhishang.com
# Expected: HTTP/1.1 200 OK, Server: cloudflare
```

## Windows Startup Verification (Post-Reboot Checklist)

After every reboot, verify the tunnel is connected:

```powershell
# 1. Task should be Running or Ready
Get-ScheduledTask -TaskName "YOUR-TASK-NAME" | Select-Object State

# 2. cloudflared process should exist
Get-Process -Name cloudflared | Select-Object Id, Path

# 3. Tunnel must show CONNECTIONS (not blank)
cloudflared tunnel list

# 4. Public domain must return 200
curl -sI -k https://your-domain.com

# If any step fails, check Windows Event Log > Application > Cloudflared for errors
```

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| Tunnel shows 0 connections | cloudflared process not connected | Re-run with `--overwrite-dns`; check credentials file |
| Service won't start | Quotes in `binpath=` not handled by sc.exe | Use batch wrapper or **Task Scheduler** (simplest on Windows) |
| `net::ERR_CONNECTION_REFUSED` | Local target not running | Ensure Hermes Studio is running on the expected port |
| DNS resolves but 404 | Ingress rule missing or wrong hostname | Check config.yml ingress rules |
| `config flag not defined` | `--config` flag order wrong | `--config` must be a **global flag** BEFORE subcommand: `cloudflared --config config.yml tunnel run ...` |
| `service install --config` unsupported | `cloudflared service install` on v2026.6.1 does NOT accept `--config` | Run `cloudflared service install` from `.cloudflared` directory (auto-reads config.yml), or use Task Scheduler |
| `530 <none>` (empty error) | Tunnel has NO active connections | Check `cloudflared tunnel list` → CONNECTIONS column must be populated |
| `error code: 1033` (530 Cloudflare) | Tunnel connected but ingress hostname mismatch | Verify CNAME target matches `ingress.hostname` in config.yml exactly |
| Tunnel has 0 connections but process running | Wrong credentials file or stale tunnel | Use the credentials JSON from Dashboard (not JWT token or API token) |
| `error code: 1010` (Cloudflare Bot) | Bot Management拦截非浏览器请求 | Tunnel功能正常（CONNECTIONS有值），但curl/Python等脚本请求被拦截；自动化脚本**必须使用本地地址** `http://localhost:8748`，不要用公网域名 |
| `service install` with API token | "Provided tunnel token is not valid (illegal base64 data at input byte 4)" | API tokens (`cfut_...`) are NOT tunnel credentials. Use the JSON credentials file from Dashboard |
| CMD window pops up at login | Task runs `cloudflared.exe` directly | Use Option A (batch cascade) instead — two batch files + ping delay = zero window |
| Task XML `Register-ScheduledTask` fails | Various parameter/encoding issues | Use the XML approach described in Option A — write UTF-16, omit `<Delay>` from XML, use batch for delay |

## Hermes Studio API 认证实操结论

> 以下结论来自 2026-07 对 `localhost:8748` 所有端点的系统测试：

| 请求方式 | 目标端点 | 结果 | 说明 |
|---------|---------|------|------|
| 任何客户端 | `GET /health` | ✅ 200 | 无需认证 |
| 任何客户端 | `POST /webhook` | ✅ 200 `{"ok":true}` | 无需认证（但无 session_id 返回）|
| 任何客户端 | `GET /` | ✅ 200 HTML | Web UI 页面 |
| curl / Python | `GET /api/hermes/sessions` | ❌ 401 | 需要 Bearer JWT |
| curl / Python | `POST /api/auth/login` | ❌ 400 | 只接受浏览器 cookie/session |
| curl / Python | `POST /api/chat-run/run` | ❌ 401 | 需要认证 |

**推荐自动化方案**：直接写入 `hermes-web-ui.db`（绕过所有 API 认证）。见 `hermes-email-auto-reply` skill。

## Local vs Public: Critical Access Pattern

**关键发现（2026-07）**：

| 请求来源 | 目标 URL | 结果 |
|---------|---------|------|
| curl / Python / 脚本 | `https://hermes.gzfuyaozhishang.com/webhook` | ❌ 1010 Bot 拦截 |
| curl / Python / 脚本 | `http://localhost:8748/webhook` | ✅ 200 OK，`{"ok": true}` |
| 浏览器直接访问公网域名 | `https://hermes.gzfuyaozhishang.com` | 需要 Cloudflare Access 认证 |

**结论**：所有自动化脚本和 API 调用使用 `http://localhost:8748` 本地直连。公网域名仅用于浏览器访问 Hermes Studio Web UI。

## Scripts

- `scripts/start_tunnel.bat` — starts cloudflared tunnel (call from `delayed_start.bat`)
- `scripts/delayed_start.bat` — 10s ping delay then calls `start_tunnel.bat` (registered as scheduled task Action)
- `references/hermes-gateway-setup.md` — production working config, tunnel IDs, verified batch files, file paths
- `references/silent-startup-approach.md` — why batch cascade works for silent startup, verified 2026-07