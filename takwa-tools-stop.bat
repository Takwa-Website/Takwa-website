@echo off
setlocal enabledelayedexpansion
REM ---------------------------------------------------------------------------
REM Stop the Takwa editing tools.
REM
REM Finds the server by the port it is holding rather than by killing anything
REM called python.exe -- that would also close any other Python the machine
REM happens to be running.
REM ---------------------------------------------------------------------------
title Takwa Website Editor - Stop

set "FOUND="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8099" ^| findstr "LISTENING"') do (
    set "FOUND=1"
    taskkill /F /PID %%a >nul 2>&1
)

if defined FOUND (
    echo   Stopped.
) else (
    echo   Not running.
)
timeout /t 3 /nobreak >nul
