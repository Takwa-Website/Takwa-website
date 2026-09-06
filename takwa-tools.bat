@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Start the Takwa editing tools and open them in a browser. Windows.
REM
REM Double-click this file. No terminal, nothing to remember.
REM To get an icon on the desktop, run create-desktop-shortcut.bat once.
REM ---------------------------------------------------------------------------
cd /d "%~dp0"
title Takwa Website Editor

REM --- find a Python that actually works ------------------------------------
REM "where python" is not enough. Windows ships a stub at that name which only
REM opens the Microsoft Store, so it is found but cannot run anything. The py
REM launcher is tried first because it is the one that comes with the real
REM python.org installer.
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY ( python --version >nul 2>&1 && set "PY=python" )
if not defined PY ( python3 --version >nul 2>&1 && set "PY=python3" )

if not defined PY (
    echo.
    echo   Python was not found.
    echo.
    echo   Install it from python.org, and on the FIRST screen of the installer
    echo   tick "Add Python to PATH". That tick box is the usual reason this
    echo   message appears.
    echo.
    pause
    exit /b 1
)

REM --- the one library that is not built in ---------------------------------
%PY% -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo   Installing the Pillow image library, one moment...
    %PY% -m pip install --quiet Pillow
    %PY% -c "import PIL" >nul 2>&1
    if errorlevel 1 (
        echo.
        echo   Could not install Pillow. Try running this by hand:
        echo       %PY% -m pip install Pillow
        echo.
        pause
        exit /b 1
    )
)

REM --- already running? ------------------------------------------------------
netstat -aon | findstr ":8099" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo   Tools are already running.
    start "" http://localhost:8099/_photo-index.html
    timeout /t 3 /nobreak >nul
    exit /b 0
)

echo   Starting the Takwa editing tools...
start "Takwa server" /min %PY% start.py

REM wait for it to actually answer rather than guessing at a delay
set TRIES=0
:waitloop
timeout /t 1 /nobreak >nul
set /a TRIES+=1
netstat -aon | findstr ":8099" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 goto ready
if %TRIES% LSS 20 goto waitloop

echo.
echo   It did not start. Check the "Takwa server" window for the error.
echo.
pause
exit /b 1

:ready
start "" http://localhost:8099/_photo-index.html
echo.
echo   Running at http://localhost:8099
echo.
echo     Photos:       http://localhost:8099/_photo-index.html
echo     Arabic text:  http://localhost:8099/_text-index-ar.html
echo     Add product:  http://localhost:8099/_add-product.html
echo     Add news:     http://localhost:8099/_add-news.html
echo.
echo   To stop, run takwa-tools-stop.bat
echo.
timeout /t 8 /nobreak >nul
