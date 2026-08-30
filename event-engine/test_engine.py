"""
Simple test procedure for the Person 3 Event Engine -- no extra test
framework required (keeps dependencies minimal, per project rules). Run:

    python test_engine.py

Each TEST N below corresponds exactly to README.md's "Testing" section.
Prints PASS / FAIL / SKIP for each and exits with a non-zero code if
anything genuinely fails.
"""

import os
import shutil

import config
from timestamp import generate_timestamp
from gps_simulator import get_gps_position
from evidence import save_evidence
import event_engine
from api_client import send_event

FAILURES = []


def check(name, condition, detail=""):
    if condition:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}  {detail}")
        FAILURES.append(name)


def setup_clean_dirs():
    for d in (config.EVIDENCE_DIR, config.OUTPUT_DIR):
        if os.path.exists(d):
            shutil.rmtree(d)
    event_engine.reset()


def test_1_mock_detection_creates_event():
    detection = {"event_type": "POTHOLE", "confidence": 0.9, "frame_id": 100}
    event = event_engine.process_detection(detection, frame=None)
    check("TEST 1: mock detection creates an event",
          event is not None and event["event_type"] == "POTHOLE")


def test_2_gps_coordinates_generated():
    lat, lon = get_gps_position(frame_id=100, fps=30)
    ok = -90 <= lat <= 90 and -180 <= lon <= 180
    check("TEST 2: GPS coordinates are generated", ok, f"got ({lat}, {lon})")


def test_3_timestamp_generated_correctly():
    ts = generate_timestamp(frame_id=1420, fps=30)
    ok = "T" in ts and len(ts.split(".")[-1]) == 3  # ISO-8601 with milliseconds
    check("TEST 3: timestamp is ISO-8601 with milliseconds", ok, f"got {ts}")


def test_4_evidence_image_saved():
    path = save_evidence(None, "EVT-TESTIMG", "POTHOLE")
    ok = os.path.exists(path)
    check("TEST 4: evidence image is saved to disk", ok, f"expected a file at {path}")


def test_5_event_id_increments():
    a = event_engine.process_detection(
        {"event_type": "PEDESTRIAN", "confidence": 0.7, "frame_id": 9000}, frame=None)
    b = event_engine.process_detection(
        {"event_type": "PEDESTRIAN", "confidence": 0.7, "frame_id": 20000}, frame=None)
    check("TEST 5: event IDs increment",
          a is not None and b is not None and a["event_id"] != b["event_id"],
          f"got {a and a['event_id']} then {b and b['event_id']}")


def test_6_duplicates_suppressed():
    event_engine.reset()
    first = event_engine.process_detection(
        {"event_type": "POTHOLE", "confidence": 0.9, "frame_id": 500}, frame=None)
    second = event_engine.process_detection(
        {"event_type": "POTHOLE", "confidence": 0.9, "frame_id": 502}, frame=None)  # same spot, moments later
    check("TEST 6: near-identical detections are suppressed",
          first is not None and second is None)


def test_7_unique_detections_create_new_events():
    event_engine.reset()
    first = event_engine.process_detection(
        {"event_type": "POTHOLE", "confidence": 0.9, "frame_id": 100}, frame=None)
    far_later = event_engine.process_detection(
        {"event_type": "POTHOLE", "confidence": 0.9, "frame_id": 50000}, frame=None)  # far away in time
    check("TEST 7: distinct detections create separate events",
          first is not None and far_later is not None)


def test_8_backend_receives_event_if_running():
    detection = {"event_type": "INCIDENT", "confidence": 0.8, "frame_id": 12345}
    event = event_engine.process_detection(detection, frame=None)
    result = send_event(event)
    if result["status"] == "sent":
        check("TEST 8: FastAPI receives the event when backend is running", True)
    else:
        print(f"SKIP  TEST 8: no backend running at {config.BACKEND_URL} "
              f"(start the stub or Person 4's real backend to exercise this test)")


def test_9_works_when_backend_unavailable():
    detection = {"event_type": "INFRASTRUCTURE", "confidence": 0.6, "frame_id": 77777}
    event = event_engine.process_detection(detection, frame=None)
    result = send_event(event, backend_url="http://localhost:59999/events")  # nothing listens here
    check("TEST 9: program does not crash when backend is unavailable",
          result["status"] == "backend_unavailable")


def main():
    setup_clean_dirs()
    test_1_mock_detection_creates_event()
    test_2_gps_coordinates_generated()
    test_3_timestamp_generated_correctly()
    test_4_evidence_image_saved()
    test_5_event_id_increments()
    test_6_duplicates_suppressed()
    test_7_unique_detections_create_new_events()
    test_8_backend_receives_event_if_running()
    test_9_works_when_backend_unavailable()

    print()
    if FAILURES:
        print(f"{len(FAILURES)} test(s) FAILED: {FAILURES}")
        raise SystemExit(1)
    print("All tests passed.")


if __name__ == "__main__":
    main()
