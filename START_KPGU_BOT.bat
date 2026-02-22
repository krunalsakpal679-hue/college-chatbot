@echo off
setlocal
echo ==========================================
echo   🚀 KPGU BOT - FINAL SUBMISSION READY
echo ==========================================
echo.

:: 1. Force close any old stuck servers
echo [1/3] Preparing clean environment...
taskkill /F /IM python.exe /T 2>nul
timeout /t 1 >nul

:: 2. Identify root directory
set "ROOT=%~dp0"
cd /d "%ROOT%backend"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment (venv) not found!
    pause
    exit /b
)

:: 3. Start the server on port 8000
echo [2/3] Starting Integrated Server on http://127.0.0.1:8000 ...
echo [INFO] Keeping window open for server logs.
echo [INFO] Opening browser in 3 seconds...

:: Start the browser automatically in 3 seconds
start /b cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8000"

:: Start Uvicorn
venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000

if %ERRORLEVEL% neq 0 (
    echo.
    echo [CRITICAL ERROR] Server failed to start. 
    echo Check if another app is using port 8000.
)
pause
