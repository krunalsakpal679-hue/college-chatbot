@echo off
title KPGU AI - FULL REPAIR
echo ==========================================
echo       KPGU AI - ENVIRONMENT REPAIR
echo ==========================================
echo.
echo 1. Cleaning old environment...
cd backend
if exist venv (
    echo [OK] Found venv, upgrading libraries...
    call venv\Scripts\activate
) else (
    echo [!] venv not found. Creating new one...
    python -m venv venv
    call venv\Scripts\activate
)

echo.
echo 2. Installing ALL libraries (This may take 1-2 minutes)...
python -m pip install --upgrade pip
pip install --upgrade typing-extensions tenacity pydantic-core
pip install -r requirements.txt

echo.
echo 3. Repair Complete! 
echo.
echo STARTING BACKEND NOW...
python -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
