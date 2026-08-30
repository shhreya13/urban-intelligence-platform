@echo off
setlocal EnableDelayedExpansion
title Urban Intelligence Platform - Demo Launcher
cd /d "%~dp0"

echo ================================================================
echo   URBAN INTELLIGENCE PLATFORM - DEMO LAUNCHER
echo ================================================================
echo.

REM ---- Paths (edit if you moved folders) ----
set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "EVENTENGINE_DIR=%ROOT%event-engine"
set "VEHICLE_DIR=%ROOT%Vehicle_count"
set "BACKEND_URL=http://127.0.0.1:8000"
set "FRONTEND_URL=http://127.0.0.1:5173"

REM ---- Locate executables ----
set "PY=%BACKEND_DIR%\venv\Scripts\python.exe"
set "EE_PY=%EVENTENGINE_DIR%\.venv\Scripts\python.exe"
set "VC_PY=%VEHICLE_DIR%\.venv\Scripts\python.exe"

echo [1/4] Checking prerequisites...
if not exist "%PY%" ( echo   ERROR: Backend venv not found: %PY% & goto :error )
if not exist "%VC_PY%" ( echo   WARNING: Vehicle/camera venv not found - camera demo needs it: %VC_PY% )
where node >nul 2>nul || ( echo   ERROR: Node.js not found. Install from nodejs.org & goto :error )

REM ---- Start Backend ----
echo [2/4] Starting Backend (FastAPI) on port 8000...
if exist "%ROOT%backend.log" del "%ROOT%backend.log" 2>nul
pushd "%BACKEND_DIR%"
start "UIP-Backend" /min "%PY%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >"%ROOT%backend.log" 2>&1
popd
echo   Backend launching in its own window... (logs: backend.log)

REM ---- Wait for backend ----
set /a attempt=0
:wait_backend
set /a attempt+=1
if %attempt% gtr 30 ( echo   WARNING: backend not responding yet, continuing anyway... & goto :backend_done )
>nul 2>nul curl -s http://127.0.0.1:8000/health
if errorlevel 1 ( timeout /t 1 /nobreak >nul & goto :wait_backend )
:backend_done
echo   Backend is UP.^^!

REM ---- Start Frontend ----
echo [3/4] Starting Frontend (Vite) on port 5173...
if exist "%ROOT%frontend.log" del "%ROOT%frontend.log" 2>nul
pushd "%FRONTEND_DIR%"
start "UIP-Frontend" /min npm run dev -- --host 127.0.0.1 --port 5173 >"%ROOT%frontend.log" 2>&1
popd
echo   Frontend launching in its own window... (logs: frontend.log)

REM ---- Wait for frontend ----
set /a attempt=0
:wait_front
set /a attempt+=1
if %attempt% gtr 40 ( echo   WARNING: frontend not responding yet, opening browser anyway... & goto :front_done )
>nul 2>nul curl -s http://127.0.0.1:5173
if errorlevel 1 ( timeout /t 1 /nobreak >nul & goto :wait_front )
:front_done
echo   Frontend is UP.^^!

echo [4/4] Opening browser...
start "" "%FRONTEND_URL%"
echo.
echo ================================================================
echo   READY!  Your dashboard is now live at:
echo   Dashboard  : %FRONTEND_URL%
echo   API docs   : %BACKEND_URL%/docs
echo.
echo   LIVE CAMERA DEMO: Click the CAMERA button in the top bar of the
echo   dashboard to start your webcam (potholes + congestion -> map).
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
if not exist "%VC_PY%" ( echo   ERROR: Camera venv not found: %VC_PY% & goto :done )
pushd "%VEHICLE_DIR%"
start "UIP-CameraDemo" /min "%VC_PY%" live_demo.py --camera 0
popd
echo   Camera demo launched! Events will appear on the dashboard.
echo   (You can also stop/start it anytime from the CAMERA button.)
goto :done

:run_ee
echo.
echo   Generating + posting events to the backend...
"%EE_PY%" "%EVENTENGINE_DIR%\main.py" --backend-url "%BACKEND_URL%/events"
echo.
echo   Events pushed. Refresh the dashboard to see new markers.
echo   NOTE: Re-running may hit '409 Conflict' for repeat event_ids - that just
echo   means the event already exists. Check %BACKEND_URL%/events to confirm.
goto :done

:error
echo.
echo   Setup error - see messages above.
pause
exit /b 1

:done
echo.
echo   Both servers are running. Close their windows to stop them.
pause
