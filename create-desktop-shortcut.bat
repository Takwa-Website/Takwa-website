@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Put a "Takwa Website Editor" icon on the desktop. Run this once.
REM
REM Windows has no equivalent of a .desktop file you can just drop in, so the
REM shortcut is created through PowerShell's WScript.Shell.
REM ---------------------------------------------------------------------------
cd /d "%~dp0"
set "TARGET=%~dp0takwa-tools.bat"
set "ICON=%~dp0Takwafoods web\takwaweb.designersidhost.com\frontend\css\images\takwafoods.png"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$desktop = [Environment]::GetFolderPath('Desktop');" ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desktop 'Takwa Website Editor.lnk'));" ^
  "$s.TargetPath = '%TARGET%';" ^
  "$s.WorkingDirectory = '%~dp0';" ^
  "$s.Description = 'Edit photos, text, products and news on the Takwa website';" ^
  "$s.Save();"

if errorlevel 1 (
    echo.
    echo   Could not create the shortcut.
    echo   You can make one by hand: right-click takwa-tools.bat,
    echo   then "Send to" ^> "Desktop (create shortcut)".
    echo.
) else (
    echo.
    echo   Done. "Takwa Website Editor" is on your desktop.
    echo.
    echo   Windows will not use a .png as a shortcut icon. To set it:
    echo   right-click the shortcut ^> Properties ^> Change Icon,
    echo   and pick any .ico you like. Purely cosmetic.
    echo.
)
pause
