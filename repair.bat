@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Takwa Website Editor - clear a stuck update.
REM
REM Finds the website copy the same way as setup.bat: this file's own folder
REM first, then C:\TakwaWebsite, %LOCALAPPDATA%\TakwaWebsite, and finally the
REM old Documents\Takwa-Website location from earlier setups.
REM
REM The safety backup goes NEXT TO the website folder, never into Documents:
REM on business PCs Documents is synced by OneDrive, which would upload a full
REM copy of the site (and its git history) to the cloud.
REM ---------------------------------------------------------------------------
title Takwa Website Editor - Repair
color 0E

set "HERE=%~dp0"
set "DEST="
if exist "%HERE%start.py" set "DEST=%HERE:~0,-1%"
if not defined DEST if exist "C:\TakwaWebsite\start.py" set "DEST=C:\TakwaWebsite"
if not defined DEST if exist "%LOCALAPPDATA%\TakwaWebsite\start.py" set "DEST=%LOCALAPPDATA%\TakwaWebsite"
if not defined DEST if exist "%USERPROFILE%\Documents\Takwa-Website\start.py" set "DEST=%USERPROFILE%\Documents\Takwa-Website"

echo.
echo   ============================================
echo      Takwa Website Editor - Repair
echo   ============================================
echo.
echo   This clears a stuck update and returns you to the latest published
echo   version. Your ENTIRE folder is copied to a backup first, so nothing
echo   can be lost -- if you had unpublished edits, they will be in the backup.
echo.
if not defined DEST goto :no_site
echo   Website copy:  %DEST%
echo.
pause

cd /d "%DEST%"

REM 1. Full safety backup, next to the site folder.
set "BK=%DEST%-backup-%RANDOM%"
echo.
echo   [..] Backing up the whole folder to:
echo        %BK%
xcopy "%DEST%" "%BK%\" /E /I /H /Q >nul
if errorlevel 1 goto :backup_failed
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
echo   [DONE] Repair finished successfully.
echo.
pause
exit /b 0

:backup_failed
echo   [X] Backup failed - stopping so nothing is risked.
echo.
echo   [STOPPED] Nothing was changed.
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
echo   [STOPPED] Nothing was changed.
pause
exit /b 1
