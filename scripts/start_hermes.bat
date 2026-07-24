@echo off
:: Hermes Studio 启动器
:: 同时启动 Hermes Desktop 和归档监控脚本
:: Hermes 关闭后监控脚本会自动停止

set "SCRIPT_DIR=%~dp0"
set "LOG=%SCRIPT_DIR%hermes_start.log"

echo [%date% %time%] 启动 Hermes Studio...
start "HermesStudio" cmd /c "hermes studio"
timeout /t 2 /nobreak >nul

echo [%date% %time%] 启动归档监控...
start "ArchiveMon" cmd /c "python \"%SCRIPT_DIR%archive_sessions.py\" >> \"%SCRIPT_DIR%archive_sessions.log\" 2>&1"

echo 启动完成。两个进程将在 Hermes 关闭时一起停止。
echo 日志: %SCRIPT_DIR%archive_sessions.log
pause
