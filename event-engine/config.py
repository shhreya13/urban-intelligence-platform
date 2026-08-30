"""
Central configuration for the Person 3 Event Engine module.
Change values here -- nothing else in the codebase should hardcode these.
"""

# --- Identity --------------------------------------------------------------
BUS_ID = "BUS-001"
CAMERA_ID = "FRONT-01"

# --- Video / timing ----------------------------------------------------------
FPS = 30                       # frames per second of the source video
VIDEO_START_TIME = None        # None -> "now" the first time it's needed (see timestamp.py)

# --- Simulated GPS route -----------------------------------------------------
# Ordered list of (latitude, longitude) waypoints the bus drives through.
# This is the exact route given in the Person 3 brief. Replace it with a
# longer real route CSV/list for a bigger demo area if you want.
ROUTE = [
    (13.0827, 80.2707),
    (13.0830, 80.2710),
    (13.0835, 80.2715),
    (13.0840, 80.2720),
    (13.0845, 80.2725),
]
BUS_SPEED_KMPH = 30.0            # constant simulated speed along ROUTE
GPS_JITTER_METERS = 2.0          # small random noise, like a real GPS fix has

# --- Duplicate-event suppression ---------------------------------------------
# Two detections of the SAME event_type are treated as the SAME real-world
# event if they happen within DUPLICATE_TIME_WINDOW seconds of each other
# AND within DUPLICATE_DISTANCE_METERS of each other. See duplicate_filter.py
# for the exact rule.
DUPLICATE_TIME_WINDOW = 5.0        # seconds
DUPLICATE_DISTANCE_METERS = 15.0   # meters

# --- Evidence frames -----------------------------------------------------------
EVIDENCE_DIR = "events"

# --- Local output (backup of everything generated, always written) -------------
OUTPUT_DIR = "output"
OUTPUT_FILE = "output/events.jsonl"

# --- Backend (Person 4's FastAPI) -----------------------------------------------
BACKEND_URL = "http://localhost:8000/events"
BACKEND_TIMEOUT_SECONDS = 3
