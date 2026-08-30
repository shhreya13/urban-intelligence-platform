"""
live_demo.py
Integrated LIVE WEBCAM demo for the Urban Intelligence Platform.

Runs on your built-in camera:
  - Vehicle detection + BoT-SORT tracking (Person 1) -> congestion counts
  - Pothole detection (Person 2 YOLO best.pt) on the same frames
  - Pushes events to the running FastAPI backend so they appear on the
    React + Leaflet dashboard map in real time.

Controls:
  - Q / ESC : quit
"""

import argparse
import time
import sys
import os
import uuid

import cv2
import requests

from ultralytics import YOLO

from ai.vehicle import VehicleDetector, VehicleTracker, ObjectCounter

# ----------------------------------------------------------------------
# CONFIG (paths are absolute so the script runs from anywhere)
# ----------------------------------------------------------------------
POTHOLE_MODEL = r"E:\urban intelligence\urban-intelligence-platform-main\urban-intelligence-platform-main\ai\pothole\weights\best.pt"
BACKEND_URL = "http://127.0.0.1:8000"

# Demo map coordinates (Chennai area - matches seeded buses)
LAT = 13.0827
LON = 80.2707

BUS_ID = "BUS-001"
CAMERA_ID = "FRONT-01"

# Throttle: at most one event of each kind every N seconds
POTHOLE_THROTTLE_S = 2.0
TRAFFIC_THROTTLE_S = 2.0

# Congestion thresholds
CONGESTED_VEHICLES = 3      # >= this many vehicles in frame -> congestion
TRAFFIC_DENSITY_LEVELS = [("LOW", 0), ("MODERATE", 2), ("HIGH", 5), ("VERY_HIGH", 8)]

WINDOW_NAME = "Urban Intelligence - Live Camera (Vehicle + Pothole)"

ALLOWED_TYPES = {
    "POTHOLE", "ROAD_DEFECT", "VEHICLE", "TRAFFIC_DENSITY",
    "CONGESTION", "INCIDENT", "PEDESTRIAN",
}


def post_event(event_type, confidence, latitude, longitude, details=None, backend_url=BACKEND_URL):
    """POST a single event to the backend. Returns True on success."""
    payload = {
        "event_id": f"LIVE-{uuid.uuid4().hex[:8].upper()}",
        "bus_id": BUS_ID,
        "camera_id": CAMERA_ID,
        "event_type": event_type,
        "confidence": round(float(confidence), 3),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "latitude": latitude,
        "longitude": longitude,
        "frame_id": details.get("frame_id") if details else None,
        "evidence_path": details.get("evidence") if details else None,
    }
    try:
        r = requests.post(f"{backend_url}/events", json=payload, timeout=3)
        return r.status_code in (200, 201)
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--no-show", action="store_true", help="hide camera window")
    ap.add_argument("--backend", type=str, default=BACKEND_URL)
    args = ap.parse_args()

    print("=" * 60)
    print("  URBAN INTELLIGENCE - LIVE CAMERA DEMO")
    print("  Vehicle detection + tracking | Pothole detection")
    print(f"  Backend: {BACKEND_URL}")
    print("  Press Q or ESC to stop")
    print("=" * 60)

    # --- Load models ---------------------------------------------------
    print("Loading vehicle detector (YOLOv8n)...")
    detector = VehicleDetector(model_name="yolov8n.pt", confidence=0.4)
    tracker = VehicleTracker(detector)
    counter = ObjectCounter()

    print("Loading pothole detector (best.pt)...")
    pothole = YOLO(POTHOLE_MODEL)

    # --- Open camera ----------------------------------------------------
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print("ERROR: cannot open camera", args.camera)
        sys.exit(1)

    last_pothole = 0.0
    last_traffic = 0.0
    last_vehicles = 0
    congested_now = False
    events_sent = 0
    frame_id = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break
            frame_id += 1
            now = time.time()

            # --- Vehicle tracking + count -----------------------------
            tracked = tracker.process_frame(frame)
            snap = counter.update(tracked)
            vehicle_count = snap.vehicle_current

            # --- Pothole detection -------------------------------------
            potholes = []
            try:
                res = pothole.predict(frame, conf=0.4, verbose=False)
                for r in res:
                    for box in r.boxes:
                        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                        potholes.append((float(box.conf[0]), (x1, y1, x2, y2)))
            except Exception as e:
                print("pothole err:", e)

            # --- Draw tracked vehicles ---------------------------------
            for obj in tracked:
                x1, y1, x2, y2 = obj.bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
                cv2.putText(frame, f"{obj.object_type} ID:{obj.track_id}",
                            (x1, max(0, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 200, 0), 2)

            # --- Draw potholes ------------------------------------------
            for conf, (x1, y1, x2, y2) in potholes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"POTHOLE {conf:.2f}", (x1, max(0, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # --- Info panel ---------------------------------------------
            cv2.putText(frame, f"Vehicles now: {snap.vehicle_current}  Session: {snap.vehicle_session}",
                        (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(frame, f"Potholes now: {len(potholes)}  Events sent: {events_sent}",
                        (10, 46), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # --- Post POTHOLE event (throttled) --------------------------
            if potholes and (now - last_pothole) >= POTHOLE_THROTTLE_S:
                best = max(potholes, key=lambda p: p[0])
                ok = post_event("POTHOLE", best[0], LAT, LON,
                                {"frame_id": frame_id}, backend_url=args.backend)
                if ok:
                    events_sent += 1
                    print(f"[{events_sent}] POTHOLE conf={best[0]:.2f} -> backend")
                last_pothole = now

            # --- Post congestion / traffic event (throttled) -------------
            if vehicle_count != last_vehicles:
                level = "LOW"
                for lvl, thresh in [("LOW", 0), ("MODERATE", 2), ("HIGH", 5), ("VERY_HIGH", 8)]:
                    if vehicle_count >= thresh:
                        level = lvl
                congested_now = vehicle_count >= CONGESTED_VEHICLES

                if (now - last_traffic) >= TRAFFIC_THROTTLE_S:
                    etype = "CONGESTION" if congested_now else "TRAFFIC_DENSITY"
                    ok = post_event(etype, min(0.95, 0.4 + vehicle_count * 0.1),
                                    LAT, LON, {"frame_id": frame_id},
                                    backend_url=args.backend)
                    if ok:
                        events_sent += 1
                        print(f"[{events_sent}] {etype} vehicles={vehicle_count} level={level} -> backend")
                    last_traffic = now
                last_vehicles = vehicle_count

            # --- Show ----------------------------------------------------
            if not args.no_show:
                cv2.imshow(WINDOW_NAME, frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nDemo stopped. {events_sent} events sent to backend.")
        print("Check the dashboard at http://127.0.0.1:5173")


if __name__ == "__main__":
    main()
