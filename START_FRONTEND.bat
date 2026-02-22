@echo off
echo ==========================================
echo   🚀 KPGU BOT - FRONTEND UI
echo ==========================================
cd frontend
if not exist "node_modules" (
    echo [ERROR] node_modules not found! 
    echo Please run 'npm install' in the frontend folder first.
    pause
    exit /b
)
echo [1/1] Starting Frontend on http://127.0.0.1:5173 ...
npx vite --host 127.0.0.1 --port 5173
pause
