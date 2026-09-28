@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Takwa Website Editor - first-time setup. Windows.
REM
REM Downloads the website, checks the two programs that are needed, and puts
REM an icon on the desktop. Run it once. Safe to run again: if the website is
REM already on this computer it updates it instead of starting over.
REM
REM Where the website goes: C:\TakwaWebsite, or %LOCALAPPDATA%\TakwaWebsite if
REM C:\ is not writable. Deliberately NOT Documents or the Desktop: on business
REM PCs those are synced by OneDrive, and OneDrive syncing a git folder damages
REM it and pushes thousands of files to the cloud.
REM
REM Written to work from any folder, including one with spaces in its name or
REM a OneDrive-synced Desktop. Paths are never echoed inside ( ) blocks: a ")"
REM in a path - "Program Files (x86)" - would silently end the block early.
REM ---------------------------------------------------------------------------
title Takwa Website Editor - Setup
color 0A

set "REPO=https://github.com/Takwa-Website/Takwa-website.git"

echo.
echo   ============================================
echo      Takwa Website Editor - Setup
echo   ============================================
echo.

REM --- 1. Git ---------------------------------------------------------------
git --version <nul >nul 2>&1
if errorlevel 1 goto :no_git
echo   [ok] Git is installed

REM Never open an editor. Git's default merge behaviour launches vim to ask for
REM a merge message, which strands anyone who does not know that ":wq" is the
REM way out. rebase avoids the merge commit entirely, and the editor settings
REM are a belt-and-braces guard for any other command that would prompt.
git config --global pull.rebase true          >nul 2>&1
git config --global core.editor "true"        >nul 2>&1
git config --global merge.ours.driver true    >nul 2>&1

REM Make pushing survive a slow or unstable connection (Syria -> GitHub).
REM Fixes RPC failed / HTTP 408 / sideband-packet disconnects.
git config --global http.version HTTP/1.1        >nul 2>&1
git config --global http.postBuffer 524288000    >nul 2>&1
git config --global http.lowSpeedLimit 0          >nul 2>&1
git config --global http.lowSpeedTime 999999      >nul 2>&1

REM --- 2. Python ------------------------------------------------------------
echo   [..] Looking for Python (a few seconds)
call :find_python
if not defined PYEXE call :install_python_runtime
if not defined PYEXE goto :no_python
echo   [ok] Python %PYVER% is installed

REM --- 3. The website -------------------------------------------------------
call :choose_dest
echo "%DEST%" | find /i "OneDrive" >nul
if not errorlevel 1 call :warn_onedrive

if exist "%DEST%\start.py" goto :update_existing
if exist "%DEST%\" goto :check_empty
goto :do_clone

:check_empty
set "HASFILES="
for /f "delims=" %%i in ('dir /b /a "%DEST%" 2^>nul') do set "HASFILES=1"
if not defined HASFILES goto :do_clone
echo.
echo   [X] This folder already exists but is not a complete copy of the website:
echo         %DEST%
echo       It is probably left over from a setup that was interrupted.
echo       Delete it (or rename it), then double-click setup.bat again.
echo.
echo   [STOPPED] Setup did not finish.
pause
exit /b 1

:do_clone
echo   [..] Downloading the website into:
echo         %DEST%
echo       This can take several minutes on a slow connection.
echo       Progress is shown below - please leave the window open.
echo.
git clone --progress "%REPO%" "%DEST%"
if errorlevel 1 goto :clone_failed
echo   [ok] Website downloaded
goto :pillow

:update_existing
echo   [ok] The website is already on this computer - updating it:
echo         %DEST%
pushd "%DEST%"
REM --rebase keeps any unsent work on top of the newer history instead of
REM opening a merge-message editor. --autostash covers unpublished edits.
git pull --rebase --autostash
set "PULLRC=%errorlevel%"
popd
if "%PULLRC%"=="0" goto :pillow
echo.
echo   [!] Could not update cleanly. Nothing was lost.
echo       Send George a photo of this window. Setup will carry on.
echo.

REM --- 4. Pillow (the one image library that is not built in) ----------------
:pillow
"%PYEXE%" -c "import PIL" <nul >nul 2>&1
if not errorlevel 1 goto :pillow_ok
echo   [..] Installing the image library (Pillow) - progress below
"%PYEXE%" -m pip install --disable-pip-version-check Pillow <nul
"%PYEXE%" -c "import PIL" <nul >nul 2>&1
if not errorlevel 1 goto :pillow_ok
echo.
echo   [!] Could not install the image library right now - probably the
echo       connection. The editor will try again the first time it starts.
echo.
goto :shortcut
:pillow_ok
echo   [ok] Image library ready

REM --- 5. Desktop icon ------------------------------------------------------
REM GetFolderPath('Desktop') rather than %USERPROFILE%\Desktop because OneDrive
REM relocates the desktop. The folder is passed in through an environment
REM variable, never pasted into the PowerShell text, so a space or an
REM apostrophe in a path cannot break the command. Errors are NOT hidden: an
REM earlier version printed "[ok]" even when no icon was made.
:shortcut
set "TK_DEST=%DEST%"
powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ^
  "$d = [Environment]::GetFolderPath('Desktop');" ^
  "$l = Join-Path $d 'Takwa Website Editor.lnk';" ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($l);" ^
  "$s.TargetPath = (Join-Path $env:TK_DEST 'takwa-tools.bat');" ^
  "$s.WorkingDirectory = $env:TK_DEST;" ^
  "$s.Description = 'Edit the Takwa website';" ^
  "$s.Save();" ^
  "if (Test-Path -LiteralPath $l) { exit 0 } else { exit 1 }" <nul
if errorlevel 1 goto :shortcut_failed
echo   [ok] Icon placed on the desktop
goto :done

:shortcut_failed
echo.
echo   [!] Could not put an icon on the desktop. Do it by hand, it takes a moment:
echo         1. The website folder is opening now.
echo         2. Right-click  takwa-tools.bat
echo         3. Choose  Show more options,  then  Send to,  then  Desktop (create shortcut)
echo       The folder is:
echo         %DEST%
echo.
start "" "%DEST%"
goto :done

:done
echo.
echo   ============================================
echo      Done.
echo   ============================================
echo.
echo   From now on, double-click "Takwa Website Editor" on the desktop.
echo   You will not need this setup file again.
echo.
echo   The website is stored in:
echo     %DEST%
echo.
echo   [DONE] Setup finished successfully.
echo.
pause
exit /b 0

REM ===========================================================================
REM Stopping points
REM ===========================================================================
:no_git
echo   [X] Git is not installed.
echo.
echo       The download page is opening now:  https://git-scm.com/download/win
echo       Run the installer and click Next on every screen.
echo       Then close this window and double-click setup.bat again.
echo.
start "" https://git-scm.com/download/win
echo   [STOPPED] Setup did not finish - install Git first.
pause
exit /b 1

:no_python
echo.
echo   [X] Python is not installed on this computer.
echo       (Windows may have a "python" placeholder that only opens the
echo       Microsoft Store - that is not a real Python.)
echo.
echo       1. The Python download page is opening now:
echo            https://www.python.org/downloads/
echo          Click the yellow Download button.
echo       2. Run the file it downloads and accept the defaults.
echo          - If it is the "Python install manager": when it asks whether
echo            to install Python or finish setting up, answer Yes.
echo          - If it is the classic installer: tick "Add python.exe to PATH"
echo            on the first screen, then click Install Now.
echo       3. Close this window and double-click setup.bat again.
echo.
start "" https://www.python.org/downloads/
echo   [STOPPED] Setup did not finish - install Python first.
pause
exit /b 1

:clone_failed
echo.
echo   [X] Could not download the website.
echo       Check the internet connection and run setup.bat again.
echo       If it asked you to sign in, sign in to GitHub and run it again.
echo       If it keeps failing, send George a photo of this window.
echo.
echo   [STOPPED] Setup did not finish.
pause
exit /b 1

REM ===========================================================================
REM Subroutines
REM ===========================================================================

REM --- where the website lives -----------------------------------------------
REM An existing copy wins wherever an earlier setup put it (including the old
REM Documents location), so running setup again never makes a second copy.
:choose_dest
set "DEST="
if exist "C:\TakwaWebsite\start.py" set "DEST=C:\TakwaWebsite"
if not defined DEST if exist "%LOCALAPPDATA%\TakwaWebsite\start.py" set "DEST=%LOCALAPPDATA%\TakwaWebsite"
if not defined DEST if exist "%USERPROFILE%\Documents\Takwa-Website\start.py" set "DEST=%USERPROFILE%\Documents\Takwa-Website"
if defined DEST goto :eof
REM Fresh install. Use C:\TakwaWebsite if this account can create it; the test
REM folder is removed again so that git clone creates it itself (and cleans up
REM after itself if the download fails).
if exist "C:\TakwaWebsite\" set "DEST=C:\TakwaWebsite"
if defined DEST goto :eof
mkdir "C:\TakwaWebsite" >nul 2>&1
if not exist "C:\TakwaWebsite\" goto :dest_fallback
rmdir "C:\TakwaWebsite" >nul 2>&1
set "DEST=C:\TakwaWebsite"
goto :eof
:dest_fallback
set "DEST=%LOCALAPPDATA%\TakwaWebsite"
goto :eof

:warn_onedrive
echo.
echo   [!] Warning: the website folder is inside OneDrive:
echo         %DEST%
echo       OneDrive syncing it can damage it. Ask George to help move it.
echo       Setup will carry on for now.
echo.
goto :eof

REM --- finding a Python that really runs ---------------------------------------
REM Sets PYEXE (full path) and PYVER (e.g. 3.14), or leaves PYEXE empty.
REM
REM Why this is careful: python.org's default installer is now the "Python
REM install manager". When "python" or "py" is run and no Python version is
REM installed yet, it DOWNLOADS one on the spot - and with the output hidden
REM that looks exactly like a frozen window. Separately, Windows ships a
REM "python" placeholder that only opens the Microsoft Store. So:
REM   - automatic downloads are switched off for these checks,
REM   - every check gets an empty keyboard (<nul) so nothing can wait for a key,
REM   - every check has a hard 20-second time limit,
REM   - each candidate is actually run, so a placeholder is never mistaken for
REM     a real Python and a real one is never rejected for where it lives.
:find_python
set "PYEXE="
set "PYVER="
set "PYTHON_MANAGER_AUTOMATIC_INSTALL=false"
set "PYTHON_MANAGER_CONFIRM=false"
set "PROBE_ARGS=-c __import__('sys').stdout.write('.'.join(map(str,__import__('sys').version_info[:2])))"
REM Pass 1: ordinary installs - classic installer, py launcher, install-manager
REM runtimes found directly in their folders.
for %%N in (py.exe python.exe python3.exe) do for /f "delims=" %%P in ('where %%N 2^>nul') do call :try_python "%%P" N
for /d %%D in ("%LOCALAPPDATA%\Python\pythoncore-3*" "%LOCALAPPDATA%\Programs\Python\Python3*" "%ProgramFiles%\Python3*") do call :try_python "%%~D\python.exe" N
REM Pass 2: app-execution aliases in WindowsApps. Either the install manager
REM (works) or the Store placeholder (does not); only the timed check can tell
REM them apart safely.
for %%N in (py.exe python.exe python3.exe) do for /f "delims=" %%P in ('where %%N 2^>nul') do call :try_python "%%P" W
goto :eof

:try_python
REM %1 = candidate path, %2 = which pass (N or W)
if defined PYEXE goto :eof
if not exist "%~1" goto :eof
set "ISWA=N"
echo "%~1" | find /i "\WindowsApps\" >nul && set "ISWA=W"
if not "%ISWA%"=="%~2" goto :eof
call :probe_python "%~1" %ISWA%
goto :eof

:probe_python
REM Runs the candidate under PowerShell with no keyboard and a 20 s limit.
REM Exit codes: 0 real Python 3, 1 not Python 3, 2 timed out (killed),
REM 3 could not start it, 4 PowerShell restricted on this PC.
set "PROBE_EXE=%~1"
set "PROBE_FILE=%TEMP%\takwa-pyprobe-%RANDOM%%RANDOM%.txt"
if exist "%PROBE_FILE%" del "%PROBE_FILE%" >nul 2>&1
powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ^
  "if ($ExecutionContext.SessionState.LanguageMode -ne 'FullLanguage') { exit 4 };" ^
  "try {" ^
  " $i = New-Object System.Diagnostics.ProcessStartInfo;" ^
  " $i.FileName = $env:PROBE_EXE; $i.Arguments = $env:PROBE_ARGS;" ^
  " $i.UseShellExecute = $false; $i.CreateNoWindow = $true;" ^
  " $i.RedirectStandardInput = $true; $i.RedirectStandardOutput = $true; $i.RedirectStandardError = $true;" ^
  " $p = [System.Diagnostics.Process]::Start($i)" ^
  "} catch { exit 3 };" ^
  "$p.StandardInput.Close();" ^
  "$o = $p.StandardOutput.ReadToEndAsync(); $e = $p.StandardError.ReadToEndAsync();" ^
  "if (-not $p.WaitForExit(20000)) { taskkill /T /F /PID $p.Id 2>&1 | Out-Null; exit 2 };" ^
  "$v = $o.Result.Trim();" ^
  "if ($p.ExitCode -eq 0 -and $v -match '^3\.[0-9]+$') { [IO.File]::WriteAllText($env:PROBE_FILE, $v); exit 0 };" ^
  "exit 1" <nul
set "RC=%errorlevel%"
if "%RC%"=="0" goto :probe_read
if "%RC%"=="1" goto :probe_end
if "%RC%"=="2" goto :probe_end
REM PowerShell could not run the timed check on this PC (3, 4 or not found).
REM Fall back to a direct check - but only for ordinary installs. A WindowsApps
REM placeholder is exactly the thing that could hang without a time limit.
if /i "%~2"=="W" goto :probe_end
"%~1" %PROBE_ARGS% <nul >"%PROBE_FILE%" 2>nul
if errorlevel 1 goto :probe_end
:probe_read
set "PYVER="
set /p PYVER=<"%PROBE_FILE%"
if not defined PYVER goto :probe_end
if not "%PYVER:~0,2%"=="3." goto :probe_end
set "PYEXE=%~1"
:probe_end
if exist "%PROBE_FILE%" del "%PROBE_FILE%" >nul 2>&1
goto :eof

REM --- install manager present, but no Python version installed yet -------------
REM Installs one in plain view (progress visible) rather than letting a hidden
REM check do it silently, then looks again.
:install_python_runtime
set "PYMGR="
for /f "delims=" %%P in ('where pymanager.exe 2^>nul') do if not defined PYMGR set "PYMGR=%%P"
if defined PYMGR goto :install_python_runtime_run
for /f "delims=" %%P in ('where py.exe 2^>nul') do call :pick_manager_py "%%P"
if not defined PYMGR goto :eof
:install_python_runtime_run
echo.
echo   [..] The Python install manager is here, but no Python version is
echo       installed yet. Installing the latest Python now - a download of a
echo       few tens of megabytes, which can take several minutes on a slow
echo       connection. Progress is shown below; please leave the window open.
echo.
"%PYMGR%" install default <nul
echo.
echo   [..] Checking Python again
call :find_python
goto :eof

:pick_manager_py
REM Only the install manager's own py.exe (a WindowsApps alias) understands
REM "install"; the classic py launcher in C:\Windows does not.
if defined PYMGR goto :eof
echo "%~1" | find /i "\WindowsApps\" >nul && set "PYMGR=%~1"
goto :eof
