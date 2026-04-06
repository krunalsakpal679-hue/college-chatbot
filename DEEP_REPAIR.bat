@echo off
title KPGU AI - DEEP REPAIR
echo ==========================================
echo       KPGU AI - DEEP REPAIR (PRO)
echo ==========================================
echo.
echo [1/5] Stopping existing processes...
taskkill /F /IM python.exe /T 2>nul

echo.
echo [2/5] Wiping old environment...
cd backend
if exist venv (
    echo Removing old folders...
    rmdir /s /q venv
)
if exist chroma_db (
    rmdir /s /q chroma_db
)

echo.
echo [3/5] Creating Fresh Environment...
python -m venv venv

echo.
echo [4/5] Installing Modern AI Stack (Python 3.14 Compatible)...
call venv\Scripts\activate
python -m pip install --upgrade pip
:: Force install absolute latest core fixes first
python -m pip install typing-extensions>=4.12.0 tenacity>=8.5.0 pydantic>=2.9.0 sqlalchemy>=2.0.30
:: Install Google specific parts explicitly
python -m pip install langchain-google-genai>=1.0.3 google-generativeai>=0.5.2
:: Install the rest
python -m pip install -r requirements.txt

echo.
echo [5/5] Final Verification...
python -c "import langchain; import sqlalchemy; print('SUCCESS: AI Engine & Database are ready!')"

echo.
echo ==========================================
echo ✅ DEEP REPAIR COMPLETED!
echo ==========================================
echo.
echo Starting Backend...
python -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
