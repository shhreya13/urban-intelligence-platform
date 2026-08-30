# Person 1 — Vehicle Detection + BoT-SORT Tracking + Counting

**SIH26124 — AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet**
Module owner: Person 1 (Vehicle Detection + Tracking Engineer)

## 1. Purpose

Turns a live bus-mounted camera feed into structured, per-object tracking
data: what was seen (car / motorcycle / bus / truck / person), where
(bounding box), how confidently, and which stable track ID BoT-SORT
assigned it — ready for Person 3's Event Engine to consume.

## 2. Architecture

```
LIVE CAMERA (cv2.VideoCapture(0))
        ↓
OpenCV frame capture
        ↓
YOLOv8n detection (filtered to 5 COCO classes)
        ↓
BoT-SORT tracking (never ByteTrack)
        ↓
Current-visible + line-crossing counting
        ↓
Structured output (object_type, track_id, confidence, bbox, frame_id, timestamp)
        ↓
Person 3 — Event Engine
```

Each stage is a separate file with one responsibility:

| File | Responsibility |
|---|---|
| `classes.py` | Single source of truth for the 5 supported COCO classes |
| `detector.py` | Loads YOLO, resolves CPU/GPU, plain per-frame detection |
| `tracker.py` | Runs BoT-SORT on the shared YOLO model, returns `TrackedObject`s |
| `counter.py` | Current-visible counts + line-crossing counts, YOLO-independent |
| `inference.py` | Live camera loop, drawing, FPS, keyboard controls (the only file touching OpenCV UI) |

## 3. Model selection — YOLOv8n

**Selected:** `yolov8n.pt` (Ultralytics YOLOv8 "nano").

**Why:**
1. **Real-time on CPU** — the nano variant is the fastest/smallest Ultralytics checkpoint, giving usable FPS on a plain laptop CPU, which matters since we can't assume every team member's laptop has a GPU.
2. **Auto-downloads and just works** — one line, `YOLO("yolov8n.pt")`, no manual weight files, no custom training pipeline (explicitly out of scope for a 5-day MVP).
3. **Native BoT-SORT support** — Ultralytics ships BoT-SORT tracking built into `model.track()`; no separate tracker library to wire up ourselves.
4. **COCO-pretrained** — already knows `car`, `motorcycle`, `bus`, `truck`, `person` out of the box; we only need to *filter* classes, not train new ones.

**Accuracy vs. speed:** Nano trades some accuracy for speed compared to `yolov8s/m/l/x.pt`. For a hackathon demo of vehicles/people at typical traffic-camera distances, nano's accuracy is sufficient; if the demo later needs higher accuracy and a GPU is available, swap in `yolov8s.pt` with **zero code changes** — just `--model yolov8s.pt`.

## 4. BoT-SORT tracking

**What it is:** BoT-SORT ("Robust Associations Multi-Pedestrian Tracking") extends the classic SORT/Kalman-filter tracker with camera-motion compensation and an optional appearance (ReID) matching stage — both useful on a moving bus.

**How detections flow into it:** `tracker.py` calls `self.detector.model.track(frame, tracker="botsort_custom.yaml", persist=True, ...)`. Ultralytics runs YOLO detection internally on the frame, then feeds those boxes straight into its BoT-SORT implementation for the same call — one call does detection + tracking together.

**How IDs are assigned/maintained:** BoT-SORT predicts each existing track's next position with a Kalman filter, matches new detections to predictions by IoU (+ optional appearance), and only assigns a *new* ID when a detection can't be matched to anything existing and clears `new_track_thresh`.

**Handling temporary disappearance:** A track that's briefly unmatched (occlusion, motion blur) isn't deleted immediately — it's kept "alive" for `track_buffer` frames (30, ≈1s @ 30 FPS) so it can reclaim its *original* ID if it reappears in that window.

**Why BoT-SORT fits our traffic-camera scenario:** the bus camera itself moves, so BoT-SORT's `gmc_method: sparseOptFlow` camera-motion compensation directly helps — plain SORT/ByteTrack has no equivalent, and would be more prone to ID switches every time the bus turns or brakes.

**Limitations (does not claim perfect tracking):** a `track_id` is **not** a permanent real-world identity. IDs can change or be reused because of occlusion, objects leaving/re-entering frame, heavy crowding, motion blur, camera shake, poor lighting, low resolution, or visually similar vehicles.

### BoT-SORT parameters used (`botsort_custom.yaml`)

| Parameter | Value | What it does |
|---|---|---|
| `track_high_thresh` | 0.5 | Confidence cutoff for first-pass (high-confidence) matching |
| `track_low_thresh` | 0.1 | Second-pass matching for low-confidence boxes (helps partial occlusion) |
| `new_track_thresh` | 0.6 | Minimum confidence to spawn a brand-new track ID |
| `track_buffer` | 30 | Frames a lost track stays "alive" before deletion (~1s @ 30 FPS) |
| `match_thresh` | 0.8 | IoU/motion matching threshold |
| `gmc_method` | sparseOptFlow | Compensates for the bus camera's own motion |
| `proximity_thresh` | 0.5 | Spatial gate before appearance matching |
| `appearance_thresh` | 0.25 | Appearance similarity threshold (only used if `with_reid: True`) |
| `with_reid` | **False** | Disabled for the MVP — ReID adds a second CNN pass per box, too slow for real-time CPU video. Motion+IoU BoT-SORT is already a strict upgrade over ByteTrack without it. |

We started from BoT-SORT's stable defaults and only changed `with_reid` — everything else is the well-tested baseline, per the "simplest stable configuration first" principle.

## 5. Detection classes

Only 5 COCO classes are detected: `car`, `motorcycle`, `bus`, `truck`, `person` (COCO IDs `2, 3, 5, 7, 0`). Everything else (bicycle, dog, cat, traffic light, stop sign, bench, ...) is filtered out at the YOLO call itself via `classes=SUPPORTED_CLASS_IDS`, not just in post-processing. Centralized in `classes.py`.

## 6. Counting — two distinct numbers

- **Current visible count** — how many tracked objects are in frame *right now*, keyed by `track_id` and recomputed every frame. An object visible for 100 frames counts once, not 100 times.
- **Line-crossing count** — a virtual horizontal line across the frame; when a track's bounding-box centroid flips from one side to the other, that `track_id` is counted **once, ever** for that line (never double-counted, even if it wobbles back over the line).

These are deliberately different from raw **detection count** (every YOLO box every frame) and from the **tracking ID** itself (an identifier, not a count).

## 7. Live camera setup

Default input is always the live webcam, camera index `0`, via `cv2.VideoCapture(0)`. No video file is required or expected for the main demo.

```bash
python -m ai.vehicle.inference
```

## 8. Output format

Every tracked object is emitted in one consistent schema (`object_type`, not `vehicle_type`, since `person` is also detected):

```json
{
  "object_type": "car",
  "track_id": 17,
  "confidence": 0.91,
  "bbox": [120, 80, 300, 250],
  "frame_id": 1234,
  "timestamp": "2026-08-30T11:20:15.230+05:30"
}
```

## 9. Integration interface (for Person 3)

```python
from ai.vehicle import VehicleDetector, VehicleTracker, ObjectCounter

detector = VehicleDetector()                 # loads YOLOv8n once
tracker = VehicleTracker(detector)           # BoT-SORT on top of it
counter = ObjectCounter(line=((0, 240), (640, 240)))

while True:
    ret, frame = cap.read()
    tracked_objects = tracker.process_frame(frame)   # List[TrackedObject]
    snapshot = counter.update(tracked_objects)         # CountSnapshot

    for obj in tracked_objects:
        event_engine.handle(obj.to_dict())   # {object_type, track_id, confidence, bbox, frame_id, timestamp}
```

No GPS, FastAPI, SQLite, or React code exists in this module — Person 3/4/5 attach `event_id`, `bus_id`, `camera_id`, `event_type`, GPS, and DB writes downstream.

## 10. Troubleshooting

See STEP 17 in the main chat response, or run with `--no-show` / different `--camera` index / lower `--confidence` as needed.

## 11. Limitations

Tracking is affected by occlusion, crowded traffic, motion blur, camera shake, poor lighting, objects leaving/re-entering frame, similar-looking vehicles, and low resolution. A `track_id` is a tracking artifact, not a guaranteed permanent real-world identity.

## 12. Future edge deployment (NOT part of the 5-day MVP)

Later, for production/edge hardware: export to ONNX/TensorRT and run on an NVIDIA Jetson, with INT8/FP16 quantization for lower latency and power draw. None of this is implemented now — the MVP intentionally stays on plain Ultralytics + CPU/GPU auto-detect.
