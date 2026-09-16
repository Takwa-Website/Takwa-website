@echo off
setlocal
title Takwa Website Editor - Publish Now
color 0A
set "DEST=%USERPROFILE%\Documents\Takwa-Website"

echo.
echo   ============================================
echo      Publish Now
echo   ============================================
echo.
echo   Sends edits that were saved on this computer but did not reach GitHub
echo   (for example after a "could not reach GitHub" error).
echo.
pause

cd /d "%DEST%" 2>nul
if errorlevel 1 ( echo   [X] Could not find %DEST% & pause & exit /b 1 )

REM make sure the slow-connection settings are on (harmless if already set)
git config --global http.version HTTP/1.1        >nul 2>&1
git config --global http.postBuffer 524288000    >nul 2>&1
git config --global http.lowSpeedLimit 0          >nul 2>&1
git config --global http.lowSpeedTime 999999      >nul 2>&1

echo   [..] Catching up with anything published elsewhere
git pull --rebase --autostash
if errorlevel 1 (
    git rebase --abort >nul 2>&1
    echo.
    echo   [X] Could not combine with a change made elsewhere. Your work is
    echo       safe on this computer. Send George a photo of this window.
    echo.
    pause
    exit /b 1
)

echo   [..] Sending your work to GitHub (may take a moment on a slow line)
git push origin main
if errorlevel 1 (
    echo.
    echo   [X] Still could not reach GitHub. Your work is safe on this computer.
    echo       Check the internet and run this again, or tell George.
    echo.
    pause
    exit /b 1
)

echo.
echo   [ok] Done - your edits are on GitHub. Tell George so he can deploy.
echo.
pause
