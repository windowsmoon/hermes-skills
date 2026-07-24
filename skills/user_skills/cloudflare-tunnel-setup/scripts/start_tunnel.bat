@echo off
cd /d "C:\Users\Admin\.cloudflared"
"C:\Program Files (x86)\cloudflared\cloudflared.exe" --config "C:\Users\Admin\.cloudflared\config.yml" tunnel run hermes-gateway-new