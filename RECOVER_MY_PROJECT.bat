@echo off
setlocal
echo ==========================================
echo   🛠️ KPGU BOT - EMERGENCY RECOVERY 
echo ==========================================
echo.
echo [1/3] Closing any hanging servers...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul

echo [2/3] Running Diagnostics...
set "ROOT=%~dp0"
"%ROOT%backend\venv\Scripts\python.exe" "%ROOT%DIAGNOSTIC_TOOL.py"

echo.
echo [3/3] Attempting Clean Startup...
echo If diagnostics were green, starting now on http://127.0.0.1:8080
echo.
cd /d "%ROOT%backend"
venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8080

if %ERRORLEVEL% neq 0 (
    echo [CRITICAL ERROR] Server failed to start.
    echo Please see the log above and send it to me.
)
pause
