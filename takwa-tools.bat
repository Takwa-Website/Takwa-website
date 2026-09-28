@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Start the Takwa editing tools and open them in a browser. Windows.
REM
REM Double-click this file, or the "Takwa Website Editor" desktop icon that
REM setup.bat makes. It runs from its own folder (the website copy), wherever
REM that is, so it keeps working if the folder has spaces in its name.
REM
REM Paths are never echoed inside ( ) blocks: a ")" in a path - for example
REM "Program Files (x86)" - would silently end the block early.
REM ---------------------------------------------------------------------------
cd /d "%~dp0"
title Takwa Website Editor

REM --- already running? ------------------------------------------------------
netstat -aon | findstr ":8099" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 goto :find
echo   Tools are already running - opening them.
start "" http://localhost:8099/_home.html
timeout /t 3 /nobreak >nul
exit /b 0

REM --- find a Python that really runs (see :find_python below) ---------------
:find
echo   Looking for Python...
call :find_python
if not defined PYEXE goto :no_python

REM --- the one library that is not built in ---------------------------------
"%PYEXE%" -c "import PIL" <nul >nul 2>&1
if not errorlevel 1 goto :start
echo   Installing the Pillow image library - progress below...
"%PYEXE%" -m pip install --disable-pip-version-check Pillow <nul
"%PYEXE%" -c "import PIL" <nul >nul 2>&1
if not errorlevel 1 goto :start
echo.
echo   Could not install the Pillow image library - probably the connection.
echo   Check the internet and double-click the editor icon again.
echo   If it keeps failing, send George a photo of this window.
echo.
echo   [STOPPED] The editor did not start.
pause
exit /b 1

:start
echo   Starting the Takwa editing tools...
start "Takwa server" /min "%PYEXE%" start.py

REM wait for it to actually answer rather than guessing at a delay
set TRIES=0
:waitloop
timeout /t 1 /nobreak >nul
set /a TRIES+=1
netstat -aon | findstr ":8099" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 goto :ready
if %TRIES% LSS 20 goto :waitloop

echo.
echo   It did not start. Check the "Takwa server" window for the error,
echo   and send George a photo of it.
echo.
echo   [STOPPED] The editor did not start.
pause
exit /b 1

:ready
start "" http://localhost:8099/_home.html
echo.
echo   Running at http://localhost:8099
echo.
echo     Menu:         http://localhost:8099/_home.html
echo     Photos:       http://localhost:8099/_photo-index.html
echo     Arabic text:  http://localhost:8099/_text-index-ar.html
echo     Products:     http://localhost:8099/_add-product.html
echo     News:         http://localhost:8099/_add-news.html
echo     Positions:    http://localhost:8099/_add-position.html
echo.
echo   To stop, run takwa-tools-stop.bat in this folder.
echo.
echo   [OK] The editor is running.
timeout /t 8 /nobreak >nul
exit /b 0

:no_python
echo.
echo   [X] Python was not found on this computer.
echo       Double-click setup.bat - it checks Python and explains exactly
echo       what to install. Then open the editor again.
echo.
echo   [STOPPED] The editor did not start.
pause
exit /b 1

REM ===========================================================================
REM Finding a Python that really runs. Same routine as in setup.bat - keep the
REM two copies identical.
REM
REM Sets PYEXE (full path) and PYVER (e.g. 3.14), or leaves PYEXE empty.
REM python.org's default installer is now the "Python install manager". When
REM "python" or "py" is run with no Python version installed, it DOWNLOADS one
REM on the spot - with output hidden that looks like a frozen window. Windows
REM also ships a "python" placeholder that only opens the Microsoft Store. So:
REM automatic downloads are off for these checks, every check gets an empty
REM keyboard (<nul), every check has a hard 20-second limit, and each candidate
REM is actually run rather than judged by where it lives.
REM ===========================================================================
:find_python
set "PYEXE="
set "PYVER="
set "PYTHON_MANAGER_AUTOMATIC_INSTALL=false"
set "PYTHON_MANAGER_CONFIRM=false"
set "PROBE_ARGS=-c __import__('sys').stdout.write('.'.join(map(str,__import__('sys').version_info[:2])))"
for %%N in (py.exe python.exe python3.exe) do for /f "delims=" %%P in ('where %%N 2^>nul') do call :try_python "%%P" N
for /d %%D in ("%LOCALAPPDATA%\Python\pythoncore-3*" "%LOCALAPPDATA%\Programs\Python\Python3*" "%ProgramFiles%\Python3*") do call :try_python "%%~D\python.exe" N
for %%N in (py.exe python.exe python3.exe) do for /f "delims=" %%P in ('where %%N 2^>nul') do call :try_python "%%P" W
goto :eof

:try_python
if defined PYEXE goto :eof
if not exist "%~1" goto :eof
set "ISWA=N"
echo "%~1" | find /i "\WindowsApps\" >nul && set "ISWA=W"
if not "%ISWA%"=="%~2" goto :eof
call :probe_python "%~1" %ISWA%
goto :eof

:probe_python
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
