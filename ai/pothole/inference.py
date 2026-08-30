"""
inference.py

Runs the pothole detector on a video file (or webcam/live stream) and
converts raw detections into the shared event JSON format used across
the whole team's pipeline:

    {
        "event_type": "POTHOLE",
        "confidence": 0.92,
        "bbox": [x1, y1, x2, y2],
        "frame_id": 1420
    }

This is the main file other team members (especially Person 3's event
engine and Person 6's integration layer) should use. It hides all the
YOLO-specific details behind one simple function call.
"""

import cv2
from .detector import PotholeDetector


def run_on_video(video_path: str, conf_threshold: float = 0.4, model_path: str = None):
    """
    Process an entire video file and return a list of pothole events
    in the shared JSON format.

    Args:
        video_path: path to the video file to process.
        conf_threshold: minimum confidence to report a detection.
        model_path: optional override for the model weights path.
                    Defaults to ai/pothole/models/best.pt.

    Returns:
        A list of event dicts, one per detected pothole per frame:
            [
                {
                    "event_type": "POTHOLE",
                    "confidence": 0.92,
                    "bbox": [120.0, 340.0, 210.0, 400.0],
                    "frame_id": 1420
                },
                ...
            ]

    Raises:
        FileNotFoundError: if the video or model file can't be found.
    """
    if model_path:
        detector = PotholeDetector(model_path=model_path, conf_threshold=conf_threshold)
    else:
        detector = PotholeDetector(conf_threshold=conf_threshold)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(
            f"Could not open video at '{video_path}'. "
            f"The file may be missing, corrupted, or in an unsupported format."
        )

    events = []
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = detector.detect(frame)

        for det in detections:
            events.append({
                "event_type": "POTHOLE",
                "confidence": det["confidence"],
                "bbox": det["bbox"],
                "frame_id": frame_id,
            })

        frame_id += 1

    cap.release()
    return events


def run_on_frame(frame, frame_id: int, conf_threshold: float = 0.4, model_path: str = None):
    """
    Process a single already-loaded frame (useful if another module,
    e.g. Person 1's vehicle pipeline, is already looping over video
    frames and wants pothole detection on the same loop instead of
    opening the video twice).

    Args:
        frame: a numpy array (e.g. from cv2.VideoCapture().read()).
        frame_id: the frame number/index, supplied by the caller.
        conf_threshold: minimum confidence to report a detection.
        model_path: optional override for the model weights path.

    Returns:
        A list of event dicts (same format as run_on_video), for
        detections found in this single frame only.
    """
    if model_path:
        detector = PotholeDetector(model_path=model_path, conf_threshold=conf_threshold)
    else:
        detector = PotholeDetector(conf_threshold=conf_threshold)

    detections = detector.detect(frame)

    return [
        {
            "event_type": "POTHOLE",
            "confidence": det["confidence"],
            "bbox": det["bbox"],
            "frame_id": frame_id,
        }
        for det in detections
    ]


if __name__ == "__main__":
    # Quick manual test: python inference.py path/to/video.mp4
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python inference.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    events = run_on_video(video_path)
    print(f"Found {len(events)} pothole detections across the video.")
    print(json.dumps(events[:5], indent=2))  # preview first 5 events