@echo off
REM ============================================
REM Hindsight Memory Daemon + Control Center
REM 开机自启脚本
REM 放入: %%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Startup\
REM Daemon 端口: 9100  |  控制中心: 7878
REM ============================================

set "HERMES_SCRIPTS=C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\Scripts"

REM 等待 Hermes Studio 网关就绪
timeout /t 15 /nobreak >nul

REM === 启动 Daemon（如果没在运行）===
"%HERMES_SCRIPTS%\hindsight-embed.exe" -p hermes daemon status 2>nul | findstr "running" >nul
if %errorlevel% neq 0 (
    start "Hindsight Daemon" "%HERMES_SCRIPTS%\hindsight-embed.exe" -p hermes daemon start
    timeout /t 5 /nobreak >nul
)

REM === 启动 Control Center ===
start "Hindsight UI" "%HERMES_SCRIPTS%\hindsight-embed.exe" -p hermes control start

echo %date% %time% - Hindsight started >> "%USERPROFILE%\.hermes\hindsight_autostart.log"
