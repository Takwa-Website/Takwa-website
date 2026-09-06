@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Takwa Website Editor - first-time setup. Windows.
REM
REM This is the only file that needs sending to a new editor. It downloads the
REM website, checks the two programs that are needed, and puts an icon on the
REM desktop. Run it once.
REM
REM It is safe to run again: if the folder is already there it updates it
REM instead of starting over.
REM ---------------------------------------------------------------------------
title Takwa Website Editor - Setup
color 0A

set "REPO=https://github.com/Takwa-Website/Takwa-website.git"
set "DEST=%USERPROFILE%\Documents\Takwa-Website"

echo.
echo   ============================================
echo      Takwa Website Editor - Setup
echo   ============================================
echo.

REM --- 1. Git ---------------------------------------------------------------
git --version >nul 2>&1
if errorlevel 1 (
    echo   [X] Git is not installed.
    echo.
    echo       Download it from:  https://git-scm.com/download/win
    echo       Run the installer and click Next on every screen.
    echo       Then run this setup again.
    echo.
    start "" https://git-scm.com/download/win
    pause
    exit /b 1
)
echo   [ok] Git is installed

REM --- 2. Python ------------------------------------------------------------
REM "where python" is not a real test: Windows ships a stub at that name that
REM only opens the Microsoft Store. Ask for a version instead.
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY ( python --version >nul 2>&1 && set "PY=python" )

if not defined PY (
    echo   [X] Python is not installed.
    echo.
    echo       Download it from:  https://www.python.org/downloads/
    echo.
    echo       IMPORTANT: on the FIRST screen of the installer, tick
    echo                  "Add python.exe to PATH" before clicking Install.
    echo                  Almost everyone misses this and setup then fails.
    echo.
    echo       Then run this setup again.
    echo.
    start "" https://www.python.org/downloads/
    pause
    exit /b 1
)
echo   [ok] Python is installed

REM --- 3. The website -------------------------------------------------------
if exist "%DEST%\start.py" (
    echo   [ok] Website folder already here - updating it
    pushd "%DEST%"
    git pull
    popd
) else (
    echo   [..] Downloading the website, this takes a minute
    git clone "%REPO%" "%DEST%"
    if errorlevel 1 (
        echo.
        echo   [X] Could not download it.
        echo       If it asked you to sign in, sign in to GitHub and run this again.
        echo.
        pause
        exit /b 1
    )
    echo   [ok] Downloaded to %DEST%
)

REM --- 4. Pillow ------------------------------------------------------------
%PY% -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo   [..] Installing the image library
    %PY% -m pip install --quiet Pillow
)
echo   [ok] Image library ready

REM --- 5. Desktop icon ------------------------------------------------------
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$d=[Environment]::GetFolderPath('Desktop');" ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'Takwa Website Editor.lnk'));" ^
  "$s.TargetPath='%DEST%\takwa-tools.bat';" ^
  "$s.WorkingDirectory='%DEST%';" ^
  "$s.Description='Edit the Takwa website';" ^
  "$s.Save();" >nul 2>&1
echo   [ok] Icon placed on the desktop

echo.
echo   ============================================
echo      Done.
echo   ============================================
echo.
echo   From now on, just double-click "Takwa Website Editor"
echo   on your desktop. You will not need this setup file again.
echo.
pause
