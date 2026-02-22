@echo off
echo ==========================================
echo   🚀 KPGU BOT - 1-CLICK STARTUP
echo ==========================================
echo.

:: Start Backend
echo [1/2] Starting Backend Server...
cd backend
start cmd /k "echo BACKEND STARTING... && venv\Scripts\activate && python -m uvicorn main:app --reload --port 8000"
timeout /t 5

:: Start Frontend
echo [2/2] Starting Frontend UI...
cd ..\frontend
start cmd /k "echo FRONTEND STARTING... && npm run dev"

echo.
echo ==========================================
echo   ✅ SUCCESS: Both servers are starting!
echo   1. Backend: http://127.0.0.1:8000
echo   2. Frontend: http://localhost:5173 
echo   (Wait for Vite to show the link)
echo.
echo   Happy Submission! 🎓✨
echo ==========================================
pause
