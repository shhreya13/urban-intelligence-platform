"""
Pothole detection module for the Urban Intelligence Platform.

Exposes:
    - PotholeDetector: loads the fine-tuned YOLOv8n model and runs detection
    - run_on_video: convenience function to process a full video file
"""

from .detector import PotholeDetector
from .inference import run_on_video

__all__ = ["PotholeDetector", "run_on_video"]