@echo off
title KPGU AI Assistant - Startup
echo ==========================================
echo    KPGU AI Assistant - Starting Up...
echo ==========================================

:: Start Backend
echo Initializing Backend...
:: This part forces a check for missing libraries every time it starts
start cmd /k "cd backend && if not exist venv (python -m venv venv) && venv\Scripts\activate && pip install --upgrade typing-extensions && pip install -r requirements.txt && python -m uvicorn main:app --host 127.0.0.1 --port 8000"

:: Start Frontend
echo Initializing Frontend...
start cmd /k "cd frontend && npm install && npm run dev -- --port 5175 --host"

echo ==========================================
echo Setup complete. Waiting for servers...
echo Frontend: http://localhost:5175
echo Backend:  http://127.0.0.1:8000
echo ==========================================
pause
