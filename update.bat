@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Takwa Website Editor - force the update through.
REM
REM Use this when setup.bat says something like:
REM
REM   error: Your local changes to the following files would be overwritten
REM   Aborting
REM
REM That happens because running the editing tools rewrites generated files --
REM the Arabic pages are rebuilt every time -- and git will not pull on top of
REM changes it did not make.
REM
REM Nothing is thrown away. Local changes are put in a git stash first, so if
REM any of them turn out to matter they can be brought back with:
REM
REM   git stash list
REM   git stash pop
REM ---------------------------------------------------------------------------
title Takwa Website Editor - Update
color 0A

set "DEST=%USERPROFILE%\Documents\Takwa-Website"

echo.
echo   ============================================
echo      Takwa Website Editor - Update
echo   ============================================
echo.

if not exist "%DEST%\start.py" (
    echo   [X] Cannot find the website in:
    echo       %DEST%
    echo.
    echo       Run setup.bat first.
    echo.
    pause
    exit /b 1
)

pushd "%DEST%"

REM Stop git ever opening an editor. Doing it here as well as in setup.bat
REM because this file may be run on a machine that never got the newer setup.
git config --global pull.rebase true    >nul 2>&1
git config --global core.editor "true"  >nul 2>&1

echo   Version now:
git log -1 --format="     %%h  %%s"
echo.

echo   Unsent changes on this computer:
git status --porcelain
echo.

echo   [..] Setting them aside (not deleted - kept in a stash)
git stash push -u -m "set aside by update.bat" >nul 2>&1

echo   [..] Downloading the update
git pull --rebase --autostash
if errorlevel 1 (
    echo.
    echo   [X] The update failed. Nothing was lost.
    echo       Send George a photo of this window.
    echo.
    popd
    pause
    exit /b 1
)

echo.
echo   New version:
git log -1 --format="     %%h  %%s"

popd

echo.
echo   ============================================
echo      Updated.
echo   ============================================
echo.
echo   IMPORTANT - the tools must be restarted:
echo.
echo     1. Double-click  takwa-tools-stop.bat
echo     2. Double-click  Takwa Website Editor
echo.
echo   Until you do, the old version keeps running and
echo   nothing will look any different.
echo.
pause
