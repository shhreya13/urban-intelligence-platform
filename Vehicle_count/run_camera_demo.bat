@echo off
title Urban Intelligence - Live Camera Demo
cd /d "%~dp0"

set "VC=%~dp0"
set "PY=%VC%.venv\Scripts\python.exe"
set "BACKEND=http://127.0.0.1:8000"

echo ================================================================
echo   LIVE CAMERA DEMO - Vehicle + Pothole Detection
echo   Built-in webcam  |  posts events to dashboard
echo ================================================================
echo.

REM ---- Make sure the backend is running ----
echo [1/2] Checking backend...
>nul 2>nul curl -s %BACKEND%/health
if errorlevel 1 (
    echo   Backend is DOWN - starting it...
    start "UIP-Backend" /min cmd /k "cd /d ""%~dp0..\..\Backend+Frontend\Backend+Frontend\backend"" && venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
    timeout /t 6 /nobreak >nul
) else (
    echo   Backend is OK.
)

echo.
echo [2/2] Starting live camera detector...
echo   A window will open showing your camera with detection boxes.
echo   Vehicles turn GREEN, potholes turn RED.
echo   Press Q or ESC in the camera window to stop.
echo.
pause
"%PY%" live_demo.py --camera 0
echo.
echo   Done. Check the dashboard at http://127.0.0.1:5173
pause
