"""
Evidence image saving -- Person 3 module.

When a detection becomes an event, save the actual video frame for it to
events/<event_id>.jpg using OpenCV. evidence_path is only ever set to a
path that was genuinely written to disk -- never a placeholder string.

If no real video frame is available (mock/demo mode, no --video given), a
clearly-labeled synthetic test frame is generated instead, so the whole
pipeline -- including "an image was really written to disk" -- can be
demonstrated without needing a video file. This is only for demo purposes;
once real frames from Person 1/2's video pipeline are wired in via the
`frame` argument, the real frame is what gets saved.
"""

import os

import cv2
import numpy as np

import config


def _make_mock_frame(event_id: str, event_type: str):
    """A simple, clearly-labeled synthetic image used only when no real
    video frame is supplied (e.g. running main.py without --video)."""
    frame = np.full((360, 640, 3), (40, 40, 40), dtype=np.uint8)
    cv2.putText(frame, "MOCK EVIDENCE FRAME", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    cv2.putText(frame, f"event_id: {event_id}", (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"event_type: {event_type}", (30, 170),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, "No real video frame was supplied for this run.", (30, 320),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
    return frame


def save_evidence(frame, event_id: str, event_type: str = "", evidence_dir: str = None) -> str:
    """
    frame: a real OpenCV frame (numpy array), or None for mock mode.
    Returns the RELATIVE path that was actually written, e.g.
    'events/EVT-0001.jpg'. Raises RuntimeError if the write genuinely
    fails (never returns a fake/placeholder path).
    """
    evidence_dir = evidence_dir or config.EVIDENCE_DIR
    os.makedirs(evidence_dir, exist_ok=True)

    if frame is None:
        frame = _make_mock_frame(event_id, event_type)

    out_path = os.path.join(evidence_dir, f"{event_id}.jpg")
    ok = cv2.imwrite(out_path, frame)
    if not ok:
        raise RuntimeError(f"Failed to write evidence image to {out_path}")

    return out_path.replace("\\", "/")  # keep forward slashes even on Windows


if __name__ == "__main__":
    path = save_evidence(None, "EVT-TEST", "POTHOLE")
    print(f"Saved mock evidence to: {path}")
