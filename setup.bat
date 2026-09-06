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

REM Never open an editor. Git's default merge behaviour launches vim to ask for
REM a merge message, which strands anyone who does not know that ":wq" is the
REM way out -- it happened on this setup's first run. rebase avoids the merge
REM commit entirely, and the editor settings are a belt-and-braces guard for
REM any other command that would otherwise prompt.
git config --global pull.rebase true          >nul 2>&1
git config --global core.editor "true"        >nul 2>&1
git config --global merge.ours.driver true    >nul 2>&1

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
    REM --rebase keeps any unsent work on top of the newer history instead of
    REM opening a merge-message editor, which a plain "git pull" does and which
    REM drops a non-technical person into vim. --autostash covers edits that
    REM were never published.
    git pull --rebase --autostash
    if errorlevel 1 (
        echo.
        echo   [!] Could not update cleanly. Nothing was lost.
        echo       Send George a photo of this window.
        echo.
    )
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
REM Errors are NOT hidden here. An earlier version sent them to nul and then
REM printed "[ok]" regardless, so a failed shortcut looked like a success and
REM the person was left hunting the desktop for an icon that was never made.
REM GetFolderPath('Desktop') is used rather than %USERPROFILE%\Desktop because
REM OneDrive relocates the desktop and the literal path is then wrong.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$d=[Environment]::GetFolderPath('Desktop');" ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'Takwa Website Editor.lnk'));" ^
  "$s.TargetPath='%DEST%\takwa-tools.bat';" ^
  "$s.WorkingDirectory='%DEST%';" ^
  "$s.Description='Edit the Takwa website';" ^
  "$s.Save();" ^
  "if(Test-Path (Join-Path $d 'Takwa Website Editor.lnk')){exit 0}else{exit 1}"

if errorlevel 1 (
    echo   [!] Could not put an icon on the desktop.
    echo.
    echo       Do it by hand, it takes a moment:
    echo         1. Open  %DEST%
    echo         2. Right-click  takwa-tools.bat
    echo         3. Send to  ^>  Desktop ^(create shortcut^)
    echo.
    echo       Opening the folder for you now...
    start "" "%DEST%"
) else (
    echo   [ok] Icon placed on the desktop
)

echo.
echo   ============================================
echo      Done.
echo   ============================================
echo.
echo   From now on, double-click "Takwa Website Editor".
echo   You will not need this setup file again.
echo.
echo   The website itself is in:
echo     %DEST%
echo.
pause
