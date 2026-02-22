@echo off
echo ==========================================
echo   🚀 KPGU BOT - 1-CLICK STARTUP
echo ==========================================
echo.

:: Start Backend
echo [1/2] Launching Backend Server...
start "KPGU_BACKEND" START_BACKEND.bat

:: Wait for backend
echo Waiting 5 seconds for backend to warm up...
timeout /t 5

:: Start Frontend
echo [2/2] Launching Frontend UI...
start "KPGU_FRONTEND" START_FRONTEND.bat

echo.
echo ==========================================
echo   ✅ SUCCESS: Check the two new windows!
echo   1. Backend: http://127.0.0.1:8000
echo   2. Frontend: http://127.0.0.1:5173 
echo   
echo   If you see "Refused to connect", 
echo   wait 5 more seconds and refresh.
echo.
echo   Happy Submission! 🎓✨
echo ==========================================
pause
