@echo off
echo ==========================================
echo   🚀 KPGU BOT - BACKEND SERVER
echo ==========================================
cd backend
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment (venv) not found!
    echo Please make sure you are in the college-chatbot folder.
    pause
    exit /b
)
echo [1/1] Starting Backend on http://127.0.0.1:8000 ...
venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
