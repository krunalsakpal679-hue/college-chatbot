@echo off
title KPGU AI - CREATE ZIP
echo ==========================================
echo       KPGU AI - PROJECT PACKAGER
echo ==========================================
echo.
echo Creating a clean zip file (excluding venv and node_modules)...
echo.

powershell -Command "Compress-Archive -Path 'backend', 'frontend', 'HOW_TO_START.md', 'START_KPGU_BOT.bat', 'REPAIR_ME.bat', 'DEEP_REPAIR.bat', 'ULTRA_REPAIR.bat', '.gitignore' -DestinationPath 'KPGU_AI_Assistant.zip' -Force"

echo.
echo ==========================================
echo ✅ ZIP CREATED: KPGU_AI_Assistant.zip
echo ==========================================
echo.
pause
