@echo off
setlocal EnableDelayedExpansion
title Urban Intelligence Platform - Demo Launcher
cd /d "%~dp0"

echo ================================================================
echo   URBAN INTELLIGENCE PLATFORM - DEMO LAUNCHER
echo   (first run sets up all dependencies automatically)
echo ================================================================
echo.

REM ---- Paths (repo root = folder containing this script) ----
set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "EVENTENGINE_DIR=%ROOT%event-engine"
set "VEHICLE_DIR=%ROOT%Vehicle_count"
set "BACKEND_URL=http://127.0.0.1:8000"
set "FRONTEND_URL=http://127.0.0.1:5173"

REM ---- Find Python ----
set "PY=%BACKEND_DIR%\venv\Scripts\python.exe"
set "VC_PY=%VEHICLE_DIR%\.venv\Scripts\python.exe"
set "EE_PY=%EVENTENGINE_DIR%\.venv\Scripts\python.exe"

echo ------------------------------------------------
echo  STEP 1/5  - Check prerequisites
echo ------------------------------------------------
where python >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo   ERROR: Python is not installed.
        echo   Install it from https://www.python.org/downloads/ and check
        echo   "Add Python to PATH", then run this again.
        pause
        exit /b 1
    )
)
where node >nul 2>nul || (
    echo   ERROR: Node.js is not installed.
    echo   Install it from https://nodejs.org and run this again.
    pause
    exit /b 1
)
echo   Python and Node.js found.
echo.

echo ------------------------------------------------
echo  STEP 2/5  - Set up Backend (FastAPI)
echo ------------------------------------------------
if not exist "%BACKEND_DIR%\venv" (
    echo   Creating backend virtual environment ^(first run, ~1 min^)...
    python -m venv "%BACKEND_DIR%\venv"
    if errorlevel 1 ( echo   ERROR creating backend venv. & pause & exit /b 1 )
)
echo   Installing backend requirements (first run only)...
"%PY%" -m pip install --quiet --disable-pip-version-check -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 ( echo   ERROR installing backend requirements. & pause & exit /b 1 )
echo   Backend ready.
echo.

echo ------------------------------------------------
echo  STEP 3/5  - Set up Vehicle/Camera AI (ultralytics)
echo ------------------------------------------------
if not exist "%VEHICLE_DIR%\.venv" (
    echo   Creating vehicle virtual environment ^(first run, ~1-2 min^)...
    python -m venv "%VEHICLE_DIR%\.venv"
    if errorlevel 1 ( echo   ERROR creating vehicle venv. & pause & exit /b 1 )
)
echo   Installing vehicle/ultralytics requirements (first run only, ~2-3 min)...
"%VC_PY%" -m pip install --quiet --disable-pip-version-check -r "%VEHICLE_DIR%\ai\requirements.txt"
if errorlevel 1 ( echo   ERROR installing vehicle requirements. & pause & exit /b 1 )
echo   Vehicle/Camera AI ready.
echo.

echo ------------------------------------------------
echo  STEP 4/5  - Set up event-engine + Frontend
echo ------------------------------------------------
if not exist "%EVENTENGINE_DIR%\.venv" (
    echo   Creating event-engine virtual environment...
    python -m venv "%EVENTENGINE_DIR%\.venv"
    if errorlevel 1 ( echo   ERROR creating event-engine venv. & pause & exit /b 1 )
)
"%EE_PY%" -m pip install --quiet --disable-pip-version-check -r "%EVENTENGINE_DIR%\requirements.txt"
if not exist "%FRONTEND_DIR%\node_modules" (
    echo   Installing frontend packages ^(npm install, first run only^)...
    pushd "%FRONTEND_DIR%"
    call npm install
    popd
)
if not exist "%FRONTEND_DIR%\.env" if exist "%FRONTEND_DIR%\.env.example" (
    copy /y "%FRONTEND_DIR%\.env.example" "%FRONTEND_DIR%\.env" >nul
)
echo   Frontend + event-engine ready.
echo.

echo ------------------------------------------------
echo  STEP 5/5  - Start Backend + Frontend
echo ------------------------------------------------
echo   Starting Backend (FastAPI) on port 8000...
if exist "%ROOT%backend.log" del "%ROOT%backend.log" 2>nul
pushd "%BACKEND_DIR%"
start "UIP-Backend" /min "%PY%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >"%ROOT%backend.log" 2>&1
popd

REM ---- Wait for backend ----
set /a attempt=0
:wait_backend
set /a attempt+=1
if %attempt% gtr 30 goto :backend_done
>nul 2>nul curl -s http://127.0.0.1:8000/health
if errorlevel 1 ( timeout /t 1 /nobreak >nul & goto :wait_backend )
:backend_done
echo   Backend is UP.
echo   Starting Frontend (Vite) on port 5173...
if exist "%ROOT%frontend.log" del "%ROOT%frontend.log" 2>nul
pushd "%FRONTEND_DIR%"
start "UIP-Frontend" /min npm run dev -- --host 127.0.0.1 --port 5173 >"%ROOT%frontend.log" 2>&1
popd

REM ---- Wait for frontend ----
set /a attempt=0
:wait_front
set /a attempt+=1
if %attempt% gtr 40 goto :front_done
>nul 2>nul curl -s http://127.0.0.1:5173
if errorlevel 1 ( timeout /t 1 /nobreak >nul & goto :wait_front )
:front_done
echo   Frontend is UP.

echo   Opening browser...
start "" "%FRONTEND_URL%"
echo.
echo ================================================================
echo   READY!  Your dashboard is now live at:
echo   Dashboard  : %FRONTEND_URL%
echo   API docs   : %BACKEND_URL%/docs
echo.
echo   LIVE CAMERA DEMO: Click the CAMERA button in the top bar of the
echo   dashboard (potholes + congestion -> map).
echo   Or choose an option below right now:
echo ================================================================
echo.
echo   [1] Start the LIVE CAMERA demo now (webcam window opens)
echo   [2] Run the event-engine (push synthetic events to the map)
echo   [3] Skip - just open the dashboard as-is
echo.

:ask_menu
set "choice="
set /p "choice=Select 1, 2 or 3: "
if "%choice%"=="1" goto :run_camera
if "%choice%"=="2" goto :run_ee
if "%choice%"=="3" goto :done
echo   Invalid choice - try again.
goto :ask_menu

:run_camera
echo.
echo   Starting LIVE camera demo (webcam index 0)...
echo   A camera window will open - vehicles GREEN, potholes RED.
echo   Press Q or ESC in the camera window to stop it.
pushd "%VEHICLE_DIR%"
start "UIP-CameraDemo" /min "%VC_PY%" live_demo.py --camera 0
popd
echo   Camera demo launched! Events will appear on the dashboard.
echo   (You can also stop/start it anytime from the CAMERA button.)
goto :done

:run_ee
echo.
echo   Generating + posting events to the backend...
pushd "%EVENTENGINE_DIR%"
"%EE_PY%" main.py --backend-url "%BACKEND_URL%/events"
popd
echo.
echo   Events pushed. Refresh the dashboard to see new markers.
echo   NOTE: Re-running may hit '409 Conflict' for repeat event_ids - that just
echo   means the event already exists. Check %BACKEND_URL%/events to confirm.
goto :done

:done
echo.
echo   Both servers are running. Close their windows to stop them.
pause
