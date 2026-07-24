@echo off
:: 停止所有 Hermes 相关进程
taskkill /f /im hermes.exe 2>nul
taskkill /fi "windowtitle eq HermesStudio*" /f 2>nul
taskkill /fi "windowtitle eq ArchiveMon*" /f 2>nul
echo 已停止。
