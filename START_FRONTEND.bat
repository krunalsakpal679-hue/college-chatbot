@echo off
setlocal
echo ==========================================
echo   🚀 KPGU BOT - FRONTEND UI
echo ==========================================
:: Get absolute path to this folder
set "ROOT=%~dp0"
cd /d "%ROOT%frontend"

if not exist "node_modules\.bin\vite.cmd" (
    echo [ERROR] Vite binary not found in:
    echo %cd%\node_modules\.bin\vite.cmd
    echo Please run 'npm install' in the frontend folder first.
    pause
    exit /b
)

echo [DEBUG] Using Vite: %cd%\node_modules\.bin\vite.cmd
echo [1/1] Starting Frontend on http://127.0.0.1:5173 ...
node_modules\.bin\vite.cmd --host 127.0.0.1 --port 5173
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Frontend failed to start.
    pause
)
pause
