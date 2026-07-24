@echo off
REM Obsidian RAG Indexer - Auto-run on Windows Startup
REM This script indexes your Obsidian vault on system startup

echo [%date% %time%] Starting Obsidian RAG Indexing...

REM Set Python path
set PYTHON=C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.19.0\win-x64\python\python.exe

REM Change to script directory
cd /d "C:\Users\Admin\AppData\Local\hermes\rag_obsidian"

REM Run the indexer
"%PYTHON%" index_obsidian.py

echo [%date% %time%] Indexing completed.
