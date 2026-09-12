@echo off
title CAREVIBE Startup Utility
echo ==========================================
echo           CAREVIBE STARTUP UTILITY        
echo ==========================================
echo.

:: Check if virtual environment exists
if not exist "carevibe-backend\venv" (
    echo [ERROR] Virtual environment 'venv' not found.
    echo Please make sure you have python installed and run setup commands first.
    pause
    exit /b
)

echo [1/2] Starting Flask Backend Server in a new window...
start cmd /k "cd carevibe-backend && venv\Scripts\python app.py"

echo [2/2] Opening CAREVIBE UI in default browser...
timeout /t 2 >nul
start "" "smart_mha_ui_draft.html"

echo.
echo ==========================================
echo [SUCCESS] Backend starting and Frontend open!
echo Keep the new backend terminal open while using.
echo ==========================================
pause
