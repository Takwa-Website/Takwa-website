@echo off
setlocal
title Takwa Website Editor - Connection Fix
color 0B

echo.
echo   ============================================
echo      Takwa Website Editor - Connection Fix
echo   ============================================
echo.
echo   This makes Publish survive a slow or unstable internet connection.
echo   It fixes the errors:
echo       RPC failed; HTTP 408
echo       unexpected disconnect while reading sideband packet
echo       the remote end hung up unexpectedly
echo.
echo   You only need to run this once on this computer.
echo.
pause

REM 1. Force HTTP/1.1. GitHub over HTTP/2 drops the connection on some
REM    networks mid-upload -- this is the single biggest cause of the
REM    "sideband packet" disconnect.
git config --global http.version HTTP/1.1

REM 2. Send the whole upload in one piece instead of small chunks that a
REM    slow proxy can time out. 500 MB ceiling -- far more than any push needs.
git config --global http.postBuffer 524288000

REM 3. Never give up just because the line is slow. Without this, git aborts
REM    an upload that stalls briefly; here it waits it out.
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

echo.
echo   [ok] Applied. Settings now active for all Git on this computer:
echo.
git config --global --get http.version        > "%TEMP%\tk.txt" & set /p V=<"%TEMP%\tk.txt"
echo        http.version    = %V%
git config --global --get http.postBuffer      > "%TEMP%\tk.txt" & set /p B=<"%TEMP%\tk.txt"
echo        http.postBuffer = %B%
del "%TEMP%\tk.txt" 2>nul
echo.
echo   NEXT: open the editor and press Publish again.
echo         Your work is still saved on this computer -- nothing was lost.
echo.
pause
