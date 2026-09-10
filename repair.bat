@echo off
setlocal
title Takwa Website Editor - Repair
color 0E
set "DEST=%USERPROFILE%\Documents\Takwa-Website"

echo.
echo   ============================================
echo      Takwa Website Editor - Repair
echo   ============================================
echo.
echo   This clears a stuck update and returns you to the latest published
echo   version. Your ENTIRE folder is copied to a backup first, so nothing
echo   can be lost -- if you had unpublished edits, they will be in the backup.
echo.
pause

cd /d "%DEST%" 2>nul
if errorlevel 1 (
    echo   [X] Could not find %DEST%
    pause
    exit /b 1
)

REM 1. Full safety backup, timestamped, next to the site folder.
for /f "tokens=1-4 delims=/-. " %%a in ("%DATE%") do set "D=%%d%%c%%b"
set "T=%TIME::=%"
set "T=%T: =0%"
set "BK=%USERPROFILE%\Documents\Takwa-backup-%RANDOM%"
echo.
echo   [..] Backing up the whole folder to:
echo        %BK%
xcopy "%DEST%" "%BK%\" /E /I /H /Q >nul
if errorlevel 1 (
    echo   [X] Backup failed - stopping so nothing is risked.
    pause
    exit /b 1
)
echo   [ok] Backup done

REM 2. Cancel any half-finished merge or rebase (ignore if none in progress).
echo   [..] Cancelling the stuck operation
git merge --abort  >nul 2>&1
git rebase --abort >nul 2>&1

REM 3. Return every tracked file to the last published version. Untracked,
REM    gitignored files (the saved password) are left alone.
echo   [..] Restoring the latest published version
git fetch origin
git reset --hard origin/main
git clean -fd >nul 2>&1

echo.
echo   [ok] Repaired. You are back to the latest published version.
echo.
git log -1 --format="     Now at: %%h  %%s"
echo.
echo   If you had edits that were not yet published, they are in the backup
echo   folder shown above -- re-do them in the tools and press Publish.
echo.
echo   NEXT: close this window, run takwa-tools-stop.bat, then open the editor.
echo.
pause
