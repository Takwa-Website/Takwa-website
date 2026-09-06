@echo off
REM ---------------------------------------------------------------------------
REM Start the editing tools and open them in a browser. Windows version.
REM
REM Double-click this file. No terminal, no commands to remember.
REM Right-click it once and "Send to > Desktop (create shortcut)" to get an
REM icon you can keep.
REM ---------------------------------------------------------------------------
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python is not installed, or it was installed without "Add Python to PATH".
    echo Reinstall from python.org and tick that box on the first screen.
    pause
    exit /b 1
)

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo The Pillow library is missing. Installing it now...
    python -m pip install Pillow
)

echo Starting the Takwa editing tools...
start "" /min python start.py

REM give the server a moment before the browser asks for a page
timeout /t 4 /nobreak >nul
start "" http://localhost:8099/_photo-index.html

echo.
echo   Tools are running at http://localhost:8099
echo.
echo   Photos:       http://localhost:8099/_photo-index.html
echo   Arabic text:  http://localhost:8099/_text-index-ar.html
echo   Add product:  http://localhost:8099/_add-product.html
echo   Add news:     http://localhost:8099/_add-news.html
echo.
echo   Close the minimised Python window to stop the server.
echo.
timeout /t 8 /nobreak >nul
