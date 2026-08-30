# Person 3 — GPS, Timestamp & Event Engine

SIH26124 · AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet · Bharat Electronics Limited

## 1. Project purpose

This project turns public buses into mobile AI-powered urban sensing units: onboard cameras + AI detect potholes and vehicles, and every detection becomes a geotagged, timestamped "event" that lands on a live map for city authorities.

## 2. My role (Person 3)

I own the middle of the pipeline — everything between "AI detected something" and "the backend has a record of it":

```
BUS/ROAD VIDEO → OpenCV → YOLO (Person 1: vehicles, Person 2: potholes)
                                        │
                                        ▼
                              ┌─────────────────────┐
                              │   EVENT ENGINE       │  ← MY MODULE (this repo)
                              │  GPS + Timestamp      │
                              └─────────────────────┘
                                        │
                                        ▼
                              FastAPI (Person 4) → SQLite → React + Leaflet (Person 5)
```

I am responsible for: GPS simulation, timestamp handling, detection → location association, event generation, duplicate-event suppression, evidence-frame saving, and the client-side interface to Person 4's FastAPI backend.

I am **not** responsible for: YOLO pothole/vehicle detection, tracking, the React frontend, or the SQLite backend implementation itself — I only need to agree with Person 4 on the JSON shape I send them (Section 8).

## 3. Architecture — how a detection becomes an event

```
 detection {event_type, confidence, frame_id, bbox?}
        │
        ▼
 validate_detection()                 event_engine.py
        │
        ▼
 generate_timestamp(frame_id, fps)     timestamp.py    → ISO-8601 string
        │
        ▼
 get_gps_position(frame_id, fps)       gps_simulator.py → (lat, lon)
        │
        ▼
 DuplicateFilter.is_duplicate(...)     duplicate_filter.py
        │            │
        │ duplicate  │ new
        ▼            ▼
     return None   save_evidence(frame, event_id)   evidence.py → events/EVT-000N.jpg
                       │
                       ▼
                 build final event dict (exact shared schema)
                       │
                       ▼
                 send_event(event)     api_client.py → POST {BACKEND_URL}
```

`event_engine.process_detection(...)` is the single entry point that runs this whole chain.

## 4. Installation

```bash
cd event-engine
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 5. Folder structure

```
event-engine/
├── main.py              # demo entry point (mock mode + optional video mode)
├── config.py             # ALL tunable settings live here
├── gps_simulator.py       # simulated GPS trajectory + interpolation
├── timestamp.py           # frame_id/fps -> ISO-8601 timestamp
├── event_engine.py        # core: process_detection() — combines everything
├── duplicate_filter.py    # duplicate-event suppression
├── evidence.py            # saves the real (or mock) video frame to disk
├── api_client.py          # POSTs events to Person 4's FastAPI backend
├── stub_backend.py        # OPTIONAL local stand-in for Person 4's backend
├── test_engine.py         # the 9 tests from Section 12, runnable directly
├── requirements.txt
├── events/                # evidence images land here: EVT-0001.jpg, ...
└── output/                # local backup of every event ever generated
```

Every file's job is explained inline in its own docstring — read the top of each `.py` file for the "why", not just the "what".

## 6. How to run

```bash
# 1. Run the mock demo — no video, no Person 2 code needed
python main.py

# 2. Run the test suite
python test_engine.py

# 3. (Optional) Prove the FastAPI interface end-to-end with the included stub backend
pip install fastapi "uvicorn[standard]"
uvicorn stub_backend:app --port 8000        # terminal 1
python main.py --backend-url http://localhost:8000/events   # terminal 2
python test_engine.py                        # terminal 2 — TEST 8 now PASSes instead of SKIPping
curl http://localhost:8000/events            # confirm they actually arrived
```

## 7. Mock demonstration

`main.py`'s `MOCK_DETECTIONS` list simulates 5 detections, including one deliberate near-duplicate (frame 1420 then frame 1422 — same pothole, 2 frames later) to prove suppression. Running `python main.py` prints, for every detection:

```
AI DETECTION RECEIVED
    ↓
TIMESTAMP GENERATED
    ↓
GPS LOCATION FOUND
    ↓
DUPLICATE CHECK PASSED / SUPPRESSED
    ↓
EVIDENCE SAVED
    ↓
EVENT GENERATED
    ↓
EVENT SENT TO FASTAPI / BACKEND UNAVAILABLE
```

and ends with `output/demo_events.json` (all generated events) and real `.jpg` files in `events/`. This works with **zero** dependency on Person 2's model — real detections just replace `MOCK_DETECTIONS` later (Section 11).

## 8. Event JSON format (the shared contract — field names never change)

```json
{
  "event_id": "EVT-0001",
  "bus_id": "BUS-001",
  "camera_id": "FRONT-01",
  "event_type": "POTHOLE",
  "confidence": 0.92,
  "timestamp": "2026-08-30T10:32:14.630",
  "latitude": 13.0827,
  "longitude": 80.2707,
  "frame_id": 1420,
  "evidence_path": "events/EVT-0001.jpg"
}
```

No extra fields are ever added (`bbox` is accepted as an *input* on the detection, per Section 9, but never appears in the output event).

## 9. Person 2 integration (pothole/vehicle detector → my module)

Person 2's detector calls exactly one function, passing a raw detection plus the current video frame:

```python
from event_engine import process_detection

detection = {
    "event_type": "POTHOLE",
    "confidence": 0.92,
    "frame_id": 1420,
    "bbox": [120, 200, 300, 350],   # optional — ignored for the output event, fine to include
}

event = process_detection(detection, frame=current_cv2_frame, fps=30)

if event is not None:
    # a new event was created, evidence frame saved, ready to send
    ...
else:
    # this detection was a duplicate of something already reported — nothing to do
    ...
```

Nothing inside `event_engine.py` needs to change when Person 2's real YOLO model is ready — they just start passing real detections/frames instead of the ones in `MOCK_DETECTIONS`.

## 10. Person 4 integration (my module → FastAPI backend)

1. Person 4 builds `POST /events` accepting exactly the JSON shape in Section 8.
2. From my code, after getting an `event` back from `process_detection`:
   ```python
   from api_client import send_event
   result = send_event(event, backend_url="http://<person4-host>:8000/events")
   ```
3. `send_event()` never crashes the program. If the backend is unreachable or returns an error, it prints a clear warning, appends the event to `output/events.jsonl` so nothing is lost, and returns `{"status": "backend_unavailable", "reason": "..."}` instead of pretending the send worked.
4. Before Person 4's real backend exists, test the exact same code path against the included `stub_backend.py` (Section 6, step 3) — since it's a real FastAPI app accepting the same JSON shape, proving `send_event()` works against it proves it will work against the real backend once the URL is swapped.

## 11. Video support (optional — mock mode works first and is the primary demo path)

Once a real video and a JSON file of `{frame_id: detection}` exist (e.g. from Person 2's model running once and dumping its detections), run:

```bash
python main.py --video road.mp4 --detections detections.json
```

`detections.json` example:
```json
{
  "1420": {"event_type": "POTHOLE", "confidence": 0.92, "bbox": [120, 200, 300, 350]},
  "3000": {"event_type": "VEHICLE_COUNT", "confidence": 0.85}
}
```

`main.py` reads the video frame by frame with OpenCV; for every frame number present in `detections.json`, it runs that frame through the exact same `process_detection()` pipeline used in mock mode — including saving the **real** video frame as evidence this time, not a synthetic mock frame.

## 12. Testing

`python test_engine.py` runs all 9 tests below and prints PASS/FAIL for each (TEST 8 prints SKIP instead of FAIL if no backend is running — that's expected, not an error):

| # | What it checks | How |
|---|---|---|
| 1 | Mock detection creates an event | `process_detection()` returns a non-`None` `POTHOLE` event |
| 2 | GPS coordinates are generated | `get_gps_position()` returns valid lat/lon ranges |
| 3 | Timestamp is generated correctly | ISO-8601 string with milliseconds |
| 4 | Evidence image is saved | `save_evidence()` writes a real file to disk |
| 5 | Event ID increments | Two events get two different `EVT-XXXX` IDs |
| 6 | Duplicate detections are suppressed | Same type, same spot, 2 frames apart → second one is `None` |
| 7 | Unique detections create new events | Same type, far apart in time → both succeed |
| 8 | FastAPI receives the event when backend is running | Real POST to a live backend, checked via its response |
| 9 | Program still works when backend is unavailable | POST to a dead port doesn't crash, returns a clear status |

Run them all: `python test_engine.py`. Run the live-backend one specifically by first starting `stub_backend.py` (Section 6, step 3).

## 13. GPS simulation — how and why

No physical GPS hardware exists for the 5-day prototype. `gps_simulator.py` instead:

1. Reads the fixed route from `config.ROUTE` (5 waypoints, as given in the brief).
2. Computes the great-circle (haversine) distance between consecutive waypoints, giving the total route length.
3. For a given frame: `elapsed_seconds = frame_id / fps`, then `distance_travelled = elapsed_seconds × speed`.
4. Walks the route to find which segment that distance falls in, and **linearly interpolates** between that segment's two waypoints.
5. Adds a little random jitter (±2m default) so positions look like a real, slightly-noisy GPS fix rather than a mathematically perfect line.
6. Loops back to the start if the video "drives" past the end of the route.

Every consumer only calls `get_gps_position(frame_id, fps)` — nobody downstream needs to know the fix is simulated.

## 14. Duplicate suppression — exact rule

Two detections of the **same `event_type`** are treated as the same real-world event if **both**:
- they occur within `DUPLICATE_TIME_WINDOW` seconds of each other (default **5s**), and
- their simulated GPS positions are within `DUPLICATE_DISTANCE_METERS` of each other (default **15m**).

Only the module remembers the *last accepted* event per `event_type` and compares each new detection against it — no tracking algorithm, no history buffer. That's enough for one bus with one camera per event type, which is exactly this MVP's scope, and both numbers are one-line changes in `config.py`.

## 15. Handling a 90 km/h bus

90 km/h = 25 m/s — fast enough that naive handling could misplace events by tens of metres. This module handles it as follows:

- **Camera / frame timestamps**: every timestamp is derived purely from `frame_id / fps`, never from wall-clock time. Frame 1420 always represents the same instant in the video regardless of how fast/slow the machine actually processes it.
- **GNSS timestamp synchronization**: in the real-GNSS version (Section 16), each GPS fix carries its own hardware timestamp; the event engine matches a detection's frame-time to the two nearest GPS fixes by *time*, not by frame count, so camera clock drift doesn't silently offset every location.
- **GPS interpolation**: real GNSS units typically update at ~1 Hz, far slower than 25–30 fps video. `get_gps_position()` interpolates linearly between waypoints (or, with real GNSS, between the two nearest real fixes) using elapsed time × speed, so the estimated position moves smoothly between updates instead of "snapping" once a second.
- **Estimating location at the exact detection timestamp**: the event's recorded position is the bus's interpolated position *at the detection frame*, accurate to within the interpolation/jitter error (a few metres) — good enough for road-maintenance triage, and explicitly an MVP-level approximation rather than survey-grade positioning.
- **Duplicate suppression stays valid at speed**: `DUPLICATE_TIME_WINDOW=5s` and `DUPLICATE_DISTANCE_METERS=15m` together assume the bus can't leave and re-enter a 15m circle within 5 seconds even at 90 km/h (25 m/s × 5s = 125m of travel — well outside a 15m circle in one pass), so a single pothole flying past the camera is still recognized as one event without retuning.

## 16. Future: real GNSS integration

```
SIMULATED GPS (this MVP)              REAL GNSS RECEIVER (future)
──────────────────────                ────────────────────────────
config.ROUTE (fixed waypoints)   →    live NMEA/serial feed or a GPS log file
get_gps_position(frame_id, fps)  →    same function name, same signature
    (interpolates along ROUTE)            (interpolates between the two nearest real fixes)
```

What changes: replace the body of `gps_simulator.get_gps_position()` (or swap in a new module with the same function signature) so it reads real `(timestamp, lat, lon)` fixes from a GNSS receiver instead of `config.ROUTE`, and interpolates between the two real fixes nearest the detection's frame-time instead of between two CSV waypoints.

What does **not** change: `event_engine.py`, `duplicate_filter.py`, `evidence.py`, `api_client.py`, `main.py`, and the event schema itself — they only ever call `get_gps_position(frame_id, fps)` and have no idea whether the answer came from a route file or a real receiver. This is why the MVP stays simulation-based without creating any future rework for the rest of the team.

## 17. Dependencies

Deliberately minimal, per project constraints: `opencv-python`, `requests`, `numpy` (a transitive dependency of OpenCV, listed explicitly since `evidence.py` uses it directly). `fastapi` + `uvicorn` are OPTIONAL and only needed to run `stub_backend.py` for local testing — the core MVP (`main.py`, `test_engine.py`) never imports them. No Kafka, Redis, PostgreSQL, MongoDB, MQTT, Docker, Kubernetes, Celery, or RabbitMQ — not needed for a 5-day single-bus prototype.
