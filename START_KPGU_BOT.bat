@echo off
setlocal
echo ==========================================
echo   🚀 KPGU BOT - INTEGRATED LOCAL SERVER
echo ==========================================
echo.
set "ROOT=%~dp0"
cd /d "%ROOT%backend"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment (venv) not found!
    echo Please make sure you are in the college-chatbot folder.
    pause
    exit /b
)

echo [1/1] Starting KPGU Assistant on http://127.0.0.1:8080 ...
echo [INFO] UI is now hosted on the SAME server as the AI.
echo [INFO] AI initialization is running in the background.
echo.
:: Starting on port 8080 to avoid common Windows conflicts on 8000
venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8080

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Server failed to start.
    echo Please check if port 8080 is already in use.
    pause
)
pause
