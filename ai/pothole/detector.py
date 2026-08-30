"""
detector.py

Loads the fine-tuned YOLOv8n pothole model and provides a simple
interface for running detection on a single frame/image.

This is the low-level building block. Other team members should
usually use inference.py's run_on_video() instead of calling this
directly, unless they're integrating frame-by-frame with their own
video loop (e.g. Person 1's vehicle detection pipeline).
"""

import os
from ultralytics import YOLO

# Default path to the trained model, relative to this file's location.
DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "models", "best.pt"
)


class PotholeDetector:
    """
    Wraps the fine-tuned YOLOv8n pothole model.

    Usage:
        detector = PotholeDetector()
        detections = detector.detect(frame)
        # detections is a list of dicts:
        # [{"confidence": 0.92, "bbox": [x1, y1, x2, y2]}, ...]
    """

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH, conf_threshold: float = 0.4):
        """
        Args:
            model_path: path to the trained best.pt weights file.
            conf_threshold: minimum confidence to count as a real detection.
                            0.4 worked well during validation/testing.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Pothole model not found at '{model_path}'. "
                f"Make sure you've pulled the latest repo (git pull) "
                f"and that best.pt is in ai/pothole/models/."
            )

        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self, frame):
        """
        Run pothole detection on a single frame/image.

        Args:
            frame: a single image. Can be:
                   - a file path (str)
                   - a numpy array (e.g. a frame read via OpenCV)

        Returns:
            List of detections, each a dict:
                {
                    "confidence": float,
                    "bbox": [x1, y1, x2, y2]   # pixel coordinates
                }
            Empty list if no potholes were detected above the threshold.
        """
        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            verbose=False,
        )

        detections = []
        for result in results:
            for box in result.boxes:
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "confidence": round(confidence, 4),
                    "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                })

        return detections