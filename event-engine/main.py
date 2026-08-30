"""
Main demo -- Person 3 module.

Run with no arguments for the MOCK demo (no video file, no Person 2 model
required):

    python main.py

Optional real-video mode (once you have a video and a JSON file mapping
frame numbers to detections -- see README.md "Video Support"):

    python main.py --video road.mp4 --detections detections.json

For every detection this prints the full pipeline:

    AI DETECTION RECEIVED
        -> TIMESTAMP GENERATED
        -> GPS LOCATION FOUND
        -> DUPLICATE CHECK PASSED (or SUPPRESSED)
        -> EVIDENCE SAVED
        -> EVENT GENERATED
        -> EVENT SENT TO FASTAPI / BACKEND UNAVAILABLE
"""

import argparse
import json
import os

import cv2

import config
from event_engine import process_detection
from api_client import send_event

# Mock detections used when no real video / Person 2 model is available
# yet. Frames 1420 and 1422 are the SAME pothole two frames apart -- the
# second one is EXPECTED to be suppressed as a duplicate, on purpose, to
# prove the duplicate filter works. Frame 1421 is a different pothole far
# enough away that it is NOT suppressed.
MOCK_DETECTIONS = [
    {"event_type": "POTHOLE", "confidence": 0.92, "frame_id": 1420, "bbox": [120, 200, 300, 350]},
    {"event_type": "POTHOLE", "confidence": 0.90, "frame_id": 1422, "bbox": [118, 205, 298, 348]},
    {"event_type": "VEHICLE", "confidence": 0.85, "frame_id": 1800},
    {"event_type": "POTHOLE", "confidence": 0.88, "frame_id": 4000, "bbox": [90, 180, 260, 330]},
    {"event_type": "PEDESTRIAN", "confidence": 0.77, "frame_id": 5200},
]


def parse_args():
    p = argparse.ArgumentParser(description="Person 3 Event Engine -- main demo")
    p.add_argument("--video", type=str, default=None,
                    help="Optional path to a real video. Omit for mock mode.")
    p.add_argument("--detections", type=str, default=None,
                    help="JSON file: {\"<frame_id>\": detection}. Required if --video is given.")
    p.add_argument("--backend-url", type=str, default=config.BACKEND_URL)
    return p.parse_args()


def run_pipeline_step(detection, frame):
    print(f"\nAI DETECTION RECEIVED     : {detection}")

    event = process_detection(detection, frame, fps=config.FPS, bus_id=config.BUS_ID,
                               camera_id=config.CAMERA_ID)

    if event is None:
        print("DUPLICATE CHECK           : SUPPRESSED (same event already reported nearby/recently)")
        return None

    print(f"TIMESTAMP GENERATED       : {event['timestamp']}")
    print(f"GPS LOCATION FOUND        : lat={event['latitude']}, lon={event['longitude']}")
    print("DUPLICATE CHECK PASSED    : new event")
    print(f"EVIDENCE SAVED            : {event['evidence_path']}")
    print(f"EVENT GENERATED           : {event['event_id']}")

    result = send_event(event, backend_url=config.BACKEND_URL)
    if result["status"] == "sent":
        print("EVENT SENT TO FASTAPI     : success")
    else:
        print("EVENT SENT TO FASTAPI     : BACKEND UNAVAILABLE (saved locally to output/events.jsonl instead)")

    return event


def run_mock_demo():
    print("=" * 72)
    print("PERSON 3 EVENT ENGINE -- MOCK DEMO (no video, no Person 2 needed)")
    print("=" * 72)

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    generated = []

    for detection in MOCK_DETECTIONS:
        event = run_pipeline_step(detection, frame=None)
        if event:
            generated.append(event)

    with open(os.path.join(config.OUTPUT_DIR, "demo_events.json"), "w") as f:
        json.dump(generated, f, indent=2)

    print("\n" + "=" * 72)
    print(f"DONE. {len(generated)} event(s) generated out of {len(MOCK_DETECTIONS)} detections.")
    print(f"Full event list written to {config.OUTPUT_DIR}/demo_events.json")
    print(f"Evidence images written to {config.EVIDENCE_DIR}/")
    print("=" * 72)


def run_video_mode(video_path, detections_path):
    print("=" * 72)
    print(f"PERSON 3 EVENT ENGINE -- VIDEO MODE ({video_path})")
    print("=" * 72)

    with open(detections_path) as f:
        detections_by_frame = {int(k): v for k, v in json.load(f).items()}

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or config.FPS
    generated = []
    frame_id = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_id in detections_by_frame:
            detection = dict(detections_by_frame[frame_id])
            detection["frame_id"] = frame_id
            event = run_pipeline_step(detection, frame)
            if event:
                generated.append(event)
        frame_id += 1

    cap.release()

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(config.OUTPUT_DIR, "video_events.json"), "w") as f:
        json.dump(generated, f, indent=2)

    print(f"\nDONE. {len(generated)} event(s) generated from {frame_id} frames read.")


def main():
    args = parse_args()
    config.BACKEND_URL = args.backend_url  # allow overriding at the command line

    if args.video:
        if not args.detections:
            raise SystemExit("--video requires --detections <file.json>")
        run_video_mode(args.video, args.detections)
    else:
        run_mock_demo()


if __name__ == "__main__":
    main()
