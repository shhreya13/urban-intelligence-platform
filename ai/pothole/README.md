Fine-tuned YOLOv8n model for detecting potholes from bus/road camera footage.
Built for SIH26124 — AI-Powered Mobile Urban Intelligence Platform.

ai/pothole/
├── __init__.py
├── weights/
│   └── best.pt          ← trained pothole model (fine-tuned YOLOv8n)
├── detector.py           ← loads best.pt + detects potholes on a single frame
├── inference.py          ← runs the detector on a full video, outputs shared JSON events
└── README.md             ← this file


Base model:YOLOv8n (nano), pretrained on COCO, fine-tuned on a custom pothole dataset
Classes:single class — pothole
Training:50 epochs, batch size 16, image size 640
Validation results:
Precision: 0.831
Recall: 0.753
mAP50: 0.824
mAP50-95: 0.517

Setup

Install dependencies:


pip install ultralytics opencv-python


Make sure you've pulled the latest repo so `models/best.pt` is present:


git pull


Usage

Option 1 — Process a full video file

python
from ai.pothole.inference import run_on_video

events = run_on_video("path/to/bus_footage.mp4")

for event in events:
    print(event)
{'event_type': 'POTHOLE', 'confidence': 0.92, 'bbox': [120.0, 340.0, 210.0, 400.0], 'frame_id': 1420}


Option 2 — Process a single frame (if you already have a video loop, e.g. alongside vehicle detection)

python
import cv2
from ai.pothole.inference import run_on_frame

cap = cv2.VideoCapture("path/to/bus_footage.mp4")
frame_id = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    events = run_on_frame(frame, frame_id)
    for event in events:
        print(event)

    frame_id += 1

cap.release()


Option 3 — Lower-level access (if you need raw detections, not the event format)

python
from ai.pothole.detector import PotholeDetector

detector = PotholeDetector()
detections = detector.detect(frame)
 [{'confidence': 0.92, 'bbox': [120.0, 340.0, 210.0, 400.0]}, ...]

Output format

Every event matches the team's shared schema (GPS/timestamp are added
downstream by the event engine, not by this module):

json
{
  "event_type": "POTHOLE",
  "confidence": 0.92,
  "bbox": [120.0, 340.0, 210.0, 400.0],
  "frame_id": 1420
}

Command-line quick test

bash
python inference.py path/to/video.mp4


Prints the total number of detections and a preview of the first 5 events.

Known limitations (for the demo/judge Q&A)

Trained on ~10,000 images from a public Roboflow dataset; real-world
  performance on bus-camera footage specifically (different height/angle)
  has not been separately validated with a large labeled test set.

Single class only — does not distinguish pothole severity or size.

Not yet optimized for edge deployment (ONNX/TensorRT conversion is a
  planned next step for running on NVIDIA Jetson Orin Nano hardware).