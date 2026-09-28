@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Put a "Takwa Website Editor" icon on the desktop. Run this once, from inside
REM the website folder. (setup.bat already does this; this file is for when
REM the icon was deleted.)
REM
REM The folder is passed to PowerShell through an environment variable, never
REM pasted into its text, so a space or an apostrophe in a path cannot break
REM it. GetFolderPath('Desktop') follows a OneDrive-relocated desktop.
REM ---------------------------------------------------------------------------
cd /d "%~dp0"
set "HERE=%~dp0"
set "TK_DEST=%HERE:~0,-1%"

powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ^
  "$d = [Environment]::GetFolderPath('Desktop');" ^
  "$l = Join-Path $d 'Takwa Website Editor.lnk';" ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($l);" ^
  "$s.TargetPath = (Join-Path $env:TK_DEST 'takwa-tools.bat');" ^
  "$s.WorkingDirectory = $env:TK_DEST;" ^
  "$s.Description = 'Edit the Takwa website';" ^
  "$s.Save();" ^
  "if (Test-Path -LiteralPath $l) { exit 0 } else { exit 1 }" <nul
if errorlevel 1 goto :failed

echo.
echo   [DONE] "Takwa Website Editor" is on your desktop.
echo.
pause
exit /b 0

:failed
echo.
echo   [X] Could not create the shortcut. Make one by hand:
echo       right-click  takwa-tools.bat  in this folder, choose
echo       Show more options,  then  Send to,  then  Desktop (create shortcut).
echo.
echo   [STOPPED] No icon was made.
pause
exit /b 1
