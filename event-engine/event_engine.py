"""
Event Engine -- Person 3 module (the core of my role).

process_detection(...) is the ONE function everyone else needs to know
about:

    from event_engine import process_detection

    event = process_detection(detection, frame, bus_id="BUS-001",
                               camera_id="FRONT-01", fps=30)
    if event is not None:
        ...  # a new event was generated (and evidence saved)
    else:
        ...  # this detection was suppressed as a duplicate

It combines: AI detection + bus/camera info + timestamp + GPS + frame ID +
evidence path, and returns the EXACT shared event JSON format (see
README.md "Event JSON Format"). Internal duplicate suppression and ID
numbering are handled here so Person 2 never has to touch this file when
their YOLO model is ready -- they just start calling process_detection()
with real detections and real frames instead of mock ones.
"""

import glob
import os
import re

import config
from timestamp import generate_timestamp
from gps_simulator import get_gps_position
from duplicate_filter import DuplicateFilter
from evidence import save_evidence

REQUIRED_DETECTION_FIELDS = ("event_type", "confidence", "frame_id")

_dup_filter = DuplicateFilter()


def _next_event_id(evidence_dir: str = None) -> str:
    """Looks at what's already in events/ so re-running the demo doesn't
    reuse or overwrite previous IDs/evidence files, and returns the next
    EVT-XXXX id."""
    evidence_dir = evidence_dir or config.EVIDENCE_DIR
    os.makedirs(evidence_dir, exist_ok=True)
    existing = glob.glob(os.path.join(evidence_dir, "EVT-*.jpg"))
    max_n = 0
    for path in existing:
        match = re.search(r"EVT-(\d+)\.jpg$", os.path.basename(path))
        if match:
            max_n = max(max_n, int(match.group(1)))
    return f"EVT-{max_n + 1:04d}"


def validate_detection(detection: dict):
    missing = [f for f in REQUIRED_DETECTION_FIELDS if f not in detection]
    if missing:
        raise ValueError(f"Detection is missing required field(s): {missing}. Got: {detection}")
    if not (0.0 <= float(detection["confidence"]) <= 1.0):
        raise ValueError(f"confidence must be between 0.0 and 1.0, got {detection['confidence']}")
    if int(detection["frame_id"]) < 0:
        raise ValueError(f"frame_id must be >= 0, got {detection['frame_id']}")


def process_detection(detection: dict, frame=None, bus_id: str = None, camera_id: str = None,
                       fps: float = None, video_start_time=None):
    """
    detection: {"event_type": "POTHOLE", "confidence": 0.92, "frame_id": 1420,
                "bbox": [120, 200, 300, 350]}   # bbox is accepted but optional,
                                                  # and NOT included in the output event
    frame: an OpenCV frame (numpy array) for evidence saving, or None to use
           a mock/demo frame.

    Returns: event dict (matching the shared schema exactly), or None if
             this detection was suppressed as a duplicate.
    """
    validate_detection(detection)

    bus_id = bus_id or config.BUS_ID
    camera_id = camera_id or config.CAMERA_ID
    fps = fps or config.FPS
    frame_id = int(detection["frame_id"])
    event_type = detection["event_type"]
    confidence = round(float(detection["confidence"]), 4)

    timestamp = generate_timestamp(frame_id, fps, video_start_time or config.VIDEO_START_TIME)
    latitude, longitude = get_gps_position(frame_id, fps)

    if _dup_filter.is_duplicate(event_type, latitude, longitude, timestamp):
        return None

    event_id = _next_event_id()
    evidence_path = save_evidence(frame, event_id, event_type)

    event = {
        "event_id": event_id,
        "bus_id": bus_id,
        "camera_id": camera_id,
        "event_type": event_type,
        "confidence": confidence,
        "timestamp": timestamp,
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "frame_id": frame_id,
        "evidence_path": evidence_path,
    }
    return event


def reset():
    """Clears duplicate-suppression memory. Useful between independent
    test runs / demo runs so old state doesn't leak in."""
    _dup_filter.reset()
