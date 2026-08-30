"""
api/camera.py
Purpose: HTTP layer to start/stop the LIVE CAMERA demo (Person 1 + Person 2
modules fused in Vehicle_count/live_demo.py). The React frontend's Camera
button calls these endpoints so the demo can be triggered from the dashboard.

Endpoints:
- POST /camera/start -> launch live_demo.py (opens webcam, posts events)
- POST /camera/stop  -> terminate the running camera demo
- GET  /camera/status-> whether the demo is currently running

Connects to:
- frontend/src/components/Navbar.jsx -> Camera button
- Vehicle_count/live_demo.py        -> the script being launched
"""

import os
import signal
import subprocess
import sys
import threading

from fastapi import APIRouter

router = APIRouter(prefix="/camera", tags=["camera"])

# camera.py is at:  <root>\Backend+Frontend\Backend+Frontend\backend\app\api\camera.py
# Going up 4 levels lands on <root>\Backend+Frontend\Backend+Frontend\backend
# Going up 6 levels lands on <root> = E:\urban intelligence
_HERE = os.path.dirname(os.path.abspath(__file__))
UIP_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", "..", ".."))
# We want: <root>\Vehicle_count\Vehicle_count  (a sibling of Backend+Frontend)
VEHICLE_DIR = os.path.join(UIP_ROOT, "Vehicle_count", "Vehicle_count")
VENV_PY = os.path.join(VEHICLE_DIR, ".venv", "Scripts", "python.exe")
LIVE_DEMO = os.path.join(VEHICLE_DIR, "live_demo.py")

# Process handle for the currently-running demo (guard with a lock)
_lock = threading.Lock()
_demo_proc: subprocess.Popen | None = None


@router.post("/start")
def camera_start():
    global _demo_proc
    with _lock:
        if _demo_proc is not None and _demo_proc.poll() is None:
            return {"status": "running", "already_running": True}
        if not os.path.exists(VENV_PY) or not os.path.exists(LIVE_DEMO):
            return {"status": "error", "detail": "demo not found on server"}
        try:
            kwargs = {}
            if sys.platform == "win32":
                # Keep the GUI window visible on Windows so the user sees the feed
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            _demo_proc = subprocess.Popen(
                [VENV_PY, LIVE_DEMO, "--camera", "0"],
                cwd=VEHICLE_DIR,
                **kwargs,
            )
            return {"status": "started", "pid": _demo_proc.pid}
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}


@router.post("/stop")
def camera_stop():
    global _demo_proc
    with _lock:
        if _demo_proc is None or _demo_proc.poll() is not None:
            return {"status": "stopped", "already_stopped": True}
        try:
            if sys.platform == "win32":
                _demo_proc.terminate()
                try:
                    _demo_proc.wait(timeout=3)
                except Exception:
                    _demo_proc.kill()
            else:
                os.killpg(os.getpgid(_demo_proc.pid), signal.SIGTERM)
            _demo_proc = None
            return {"status": "stopped"}
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}


@router.get("/status")
def camera_status():
    global _demo_proc
    with _lock:
        running = _demo_proc is not None and _demo_proc.poll() is None
        return {"running": running, "pid": _demo_proc.pid if running else None}


def shutdown():
    global _demo_proc
    with _lock:
        if _demo_proc is not None and _demo_proc.poll() is None:
            try:
                _demo_proc.terminate()
            except Exception:
                pass
