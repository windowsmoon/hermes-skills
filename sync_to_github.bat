@echo off
"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -NonInteractive -File "D:\hermes-data\task-maintenance\github-sync.ps1" %*
exit /b %errorlevel%
