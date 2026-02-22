@echo off
setlocal
echo ==========================================
echo   🚀 KPGU BOT - BACKEND SERVER
echo ==========================================
:: Get absolute path to this folder
set "ROOT=%~dp0"
cd /d "%ROOT%backend"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment (venv) not found in:
    echo %cd%\venv
    echo Please make sure you are in the college-chatbot folder.
    pause
    exit /b
)

echo [DEBUG] Using Python: %cd%\venv\Scripts\python.exe
echo [1/1] Starting Backend on http://127.0.0.1:8000 ...
venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Backend failed to start.
    pause
)
pause
