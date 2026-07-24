@echo off
ping 127.0.0.1 -n 11 > nul
call "C:\Users\Admin\.cloudflared\start_tunnel.bat"