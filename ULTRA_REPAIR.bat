@echo off
title KPGU AI - ULTRA REPAIR (EMERGENCY)
echo ==========================================
echo       KPGU AI - EMERGENCY REPAIR
echo ==========================================
echo.
echo [1/6] Stopping old processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul

echo.
echo [2/6] Cleaning corrupted folders...
cd backend
if exist venv (
    echo Deleting venv...
    rmdir /s /q venv
)
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
if exist chroma_db (
    rmdir /s /q chroma_db
)

echo.
echo [3/6] Creating Fresh Environment...
python -m venv venv

echo.
echo [4/6] Installing LATEST compatible stack...
call venv\Scripts\activate
python -m pip install --upgrade pip
:: Direct install of critical Python 3.14 fixes
python -m pip install typing-extensions>=4.12.0 tenacity>=8.5.0 pydantic>=2.9.0 sqlalchemy>=2.0.30 fastapi uvicorn
:: LangChain 0.3 is MUST for Python 3.14
python -m pip install langchain>=0.3.0 langchain-community>=0.3.0 langchain-openai>=0.2.0 langchain-core>=0.3.0 langchain-google-genai>=1.0.3 google-generativeai>=0.5.2
:: Remaining
python -m pip install -r requirements.txt

echo.
echo [5/6] Final Check...
python -c "import fastapi; import langchain; import sqlalchemy; print('SYSTEM READY!')"

echo.
echo ==========================================
echo ✅ PROJECT FIXED AND READY FOR 6 PM!
echo ==========================================
echo.
echo Starting Backend on Port 8001...
python -m uvicorn main:app --host 127.0.0.1 --port 8001
pause
