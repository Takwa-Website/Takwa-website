@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Takwa Website Editor - send saved edits that did not reach GitHub.
REM
REM Finds the website copy the same way as setup.bat: this file's own folder
REM first, then C:\TakwaWebsite, %LOCALAPPDATA%\TakwaWebsite, and finally the
REM old Documents\Takwa-Website location from earlier setups.
REM ---------------------------------------------------------------------------
title Takwa Website Editor - Publish Now
color 0A

set "HERE=%~dp0"
set "DEST="
if exist "%HERE%start.py" set "DEST=%HERE:~0,-1%"
if not defined DEST if exist "C:\TakwaWebsite\start.py" set "DEST=C:\TakwaWebsite"
if not defined DEST if exist "%LOCALAPPDATA%\TakwaWebsite\start.py" set "DEST=%LOCALAPPDATA%\TakwaWebsite"
if not defined DEST if exist "%USERPROFILE%\Documents\Takwa-Website\start.py" set "DEST=%USERPROFILE%\Documents\Takwa-Website"

echo.
echo   ============================================
echo      Publish Now
echo   ============================================
echo.
echo   Sends edits that were saved on this computer but did not reach GitHub
echo   (for example after a "could not reach GitHub" error).
echo.
if not defined DEST goto :no_site
echo   Website copy:  %DEST%
echo.
pause

cd /d "%DEST%"

REM make sure the slow-connection settings are on (harmless if already set)
git config --global http.version HTTP/1.1        >nul 2>&1
git config --global http.postBuffer 524288000    >nul 2>&1
git config --global http.lowSpeedLimit 0          >nul 2>&1
git config --global http.lowSpeedTime 999999      >nul 2>&1

echo   [..] Catching up with anything published elsewhere
git pull --rebase --autostash
if errorlevel 1 goto :pull_failed

echo   [..] Sending your work to GitHub (may take a moment on a slow line)
git push origin main
if errorlevel 1 goto :push_failed

echo.
echo   [DONE] Your edits are on GitHub. Tell George so he can deploy.
echo.
pause
exit /b 0

:pull_failed
git rebase --abort >nul 2>&1
echo.
echo   [X] Could not combine with a change made elsewhere. Your work is
echo       safe on this computer. Send George a photo of this window.
echo.
echo   [STOPPED] Nothing was sent.
pause
exit /b 1

:push_failed
echo.
echo   [X] Still could not reach GitHub. Your work is safe on this computer.
echo       Check the internet and run this again, or tell George.
echo.
echo   [STOPPED] Nothing was sent.
pause
exit /b 1

:no_site
echo   [X] Cannot find the website on this computer. Looked in:
echo         this file's own folder
echo         C:\TakwaWebsite
echo         %LOCALAPPDATA%\TakwaWebsite
echo         %USERPROFILE%\Documents\Takwa-Website
echo       Run setup.bat first.
echo.
echo   [STOPPED] Nothing was sent.
pause
exit /b 1
