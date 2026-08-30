"""
inference.py — Person 1 LIVE CAMERA demo entry point.

Pipeline:

    LIVE CAMERA
        ↓
    YOLO Detection
        ↓
    BoT-SORT Tracking
        ↓
    Current Density + Session Counting

Features:
    - Uses live webcam only
    - No uploaded video required
    - YOLO object detection
    - BoT-SORT multi-object tracking
    - Shows tracking IDs
    - Shows current vehicle/person density
    - Maintains unique session totals
    - Prints final session summary when stopped
    - No counting line
    - No line-crossing logic
"""

import argparse
import logging
import sys
import time

import cv2

from ai.vehicle.classes import SUPPORTED_CLASSES
from ai.vehicle.counter import CountSnapshot, ObjectCounter
from ai.vehicle.detector import ModelLoadError, VehicleDetector
from ai.vehicle.tracker import VehicleTracker


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("ai.vehicle.inference")


# ============================================================
# CONSTANTS
# ============================================================

WINDOW_NAME = "Person 1 - Vehicle Detection + BoT-SORT Tracking"

MAX_CONSECUTIVE_EMPTY_FRAMES = 30


# ============================================================
# ARGUMENTS
# ============================================================

def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description=(
            "Live camera vehicle/person detection "
            "+ BoT-SORT tracking + density counting."
        )
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help=(
            "Camera index to open. "
            "Default: 0."
        ),
    )

    parser.add_argument(
        "--confidence",
        type=float,
        default=0.4,
        help=(
            "YOLO confidence threshold "
            "(0.0 - 1.0). Default: 0.4."
        ),
    )

    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help=(
            "YOLO model name or path. "
            "Default: yolov8n.pt."
        ),
    )

    parser.add_argument(
        "--show",
        dest="show",
        action="store_true",
        default=True,
        help="Show the live annotated camera window.",
    )

    parser.add_argument(
        "--no-show",
        dest="show",
        action="store_false",
        help="Run without displaying the camera window.",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Requested camera width. Default: 640.",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=480,
        help="Requested camera height. Default: 480.",
    )

    return parser.parse_args()


# ============================================================
# CAMERA
# ============================================================

def open_camera(
    index: int,
    width: int,
    height: int,
) -> cv2.VideoCapture:

    """
    Open the live webcam.
    """

    cap = cv2.VideoCapture(index)

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        width,
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        height,
    )

    if not cap.isOpened():

        cap.release()

        print(
            "\nERROR: Unable to open camera.\n\n"
            "Please check:\n"
            "1. Camera is connected.\n"
            "2. Camera permission is enabled.\n"
            "3. Another application is not using the camera.\n"
            "4. Try another camera index using --camera 1.\n"
        )

        sys.exit(1)

    return cap


# ============================================================
# DRAW LIVE CAMERA OVERLAY
# ============================================================

def draw_overlay(
    frame,
    tracked_objects,
    snapshot: CountSnapshot,
    fps: float,
) -> None:

    """
    Draw tracking boxes, IDs and density/session information.

    IMPORTANT:
        No yellow counting line is drawn.
        No line-crossing information is displayed.
    """

    # --------------------------------------------------------
    # DRAW TRACKED OBJECTS
    # --------------------------------------------------------

    for obj in tracked_objects:

        x1, y1, x2, y2 = obj.bbox

        # Bounding box
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 200, 0),
            2,
        )

        # Object label
        label = (
            f"{obj.object_type} "
            f"{obj.confidence:.2f} "
            f"ID:{obj.track_id}"
        )

        cv2.putText(
            frame,
            label,
            (x1, max(0, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 200, 0),
            2,
        )

    # --------------------------------------------------------
    # INFORMATION PANEL
    # --------------------------------------------------------

    panel_x = 10
    panel_y = 24
    line_height = 20

    def put(
        text: str,
        color=(255, 255, 255),
    ) -> None:

        nonlocal panel_y

        cv2.putText(
            frame,
            text,
            (panel_x, panel_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
        )

        panel_y += line_height

    # --------------------------------------------------------
    # FPS
    # --------------------------------------------------------

    put(
        f"FPS: {fps:.1f}",
        (0, 255, 255),
    )

    # --------------------------------------------------------
    # CURRENT DENSITY
    # --------------------------------------------------------

    put(
        "CURRENT",
        (255, 255, 255),
    )

    put(
        f"Vehicles: {snapshot.vehicle_current}"
    )

    put(
        f"Persons: {snapshot.person_current}"
    )

    put(
        f"Total Objects: {snapshot.current_total}",
        (0, 255, 255),
    )

    # --------------------------------------------------------
    # SESSION TOTALS
    # --------------------------------------------------------

    put(
        "SESSION",
        (255, 255, 255),
    )

    put(
        f"Vehicles Observed: {snapshot.vehicle_session}"
    )

    put(
        f"Persons Observed: {snapshot.person_session}"
    )

    put(
        f"Total Observed: {snapshot.session_total}",
        (0, 255, 255),
    )


# ============================================================
# FINAL SESSION SUMMARY
# ============================================================

def print_session_summary(
    snapshot: CountSnapshot,
) -> None:

    """
    Print the final session statistics after
    the user stops the camera.
    """

    print("\n")
    print("=" * 50)
    print("              SESSION SUMMARY")
    print("=" * 50)

    print(
        f"Cars Observed        : "
        f"{snapshot.session_by_class.get('car', 0)}"
    )

    print(
        f"Motorcycles Observed : "
        f"{snapshot.session_by_class.get('motorcycle', 0)}"
    )

    print(
        f"Buses Observed       : "
        f"{snapshot.session_by_class.get('bus', 0)}"
    )

    print(
        f"Trucks Observed      : "
        f"{snapshot.session_by_class.get('truck', 0)}"
    )

    print(
        f"Persons Observed     : "
        f"{snapshot.session_by_class.get('person', 0)}"
    )

    print("-" * 50)

    print(
        f"Total Vehicles       : "
        f"{snapshot.vehicle_session}"
    )

    print(
        f"Total Persons        : "
        f"{snapshot.person_session}"
    )

    print(
        f"Total Objects        : "
        f"{snapshot.session_total}"
    )

    print("=" * 50)


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    args = parse_args()

    # --------------------------------------------------------
    # LOAD YOLO
    # --------------------------------------------------------

    try:

        detector = VehicleDetector(
            model_name=args.model,
            confidence=args.confidence,
        )

    except ModelLoadError as exc:

        print(
            f"\nERROR: {exc}\n"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # INITIALIZE BoT-SORT
    # --------------------------------------------------------

    tracker = VehicleTracker(
        detector
    )

    # --------------------------------------------------------
    # INITIALIZE COUNTER
    # --------------------------------------------------------

    counter = ObjectCounter()

    # Create an empty initial snapshot.
    # This makes sure the final summary always has valid values.
    snapshot = counter.update([])

    # --------------------------------------------------------
    # OPEN LIVE CAMERA
    # --------------------------------------------------------

    cap = open_camera(
        args.camera,
        args.width,
        args.height,
    )

    logger.info(
        "Camera %d opened.",
        args.camera,
    )

    logger.info(
        "Press Q or ESC in the camera window to stop."
    )

    # --------------------------------------------------------
    # FPS VARIABLES
    # --------------------------------------------------------

    prev_time = time.time()

    fps = 0.0

    consecutive_empty_frames = 0

    # --------------------------------------------------------
    # CAMERA LOOP
    # --------------------------------------------------------

    try:

        while True:

            # Read a frame from the live camera
            ret, frame = cap.read()

            # ------------------------------------------------
            # HANDLE EMPTY FRAME
            # ------------------------------------------------

            if not ret or frame is None:

                consecutive_empty_frames += 1

                logger.warning(
                    "Empty frame from camera (%d in a row).",
                    consecutive_empty_frames,
                )

                if (
                    consecutive_empty_frames
                    >= MAX_CONSECUTIVE_EMPTY_FRAMES
                ):

                    print(
                        "\nERROR: Camera stopped returning "
                        "frames. Exiting.\n"
                    )

                    break

                continue

            consecutive_empty_frames = 0

            # ------------------------------------------------
            # YOLO + BoT-SORT
            # ------------------------------------------------

            try:

                tracked_objects = (
                    tracker.process_frame(frame)
                )

            except Exception as exc:

                logger.error(
                    "Detection/tracking failed "
                    "on this frame: %s",
                    exc,
                )

                tracked_objects = []

            # ------------------------------------------------
            # UPDATE COUNTS
            # ------------------------------------------------

            snapshot = counter.update(
                tracked_objects
            )

            # ------------------------------------------------
            # FPS CALCULATION
            # ------------------------------------------------

            now = time.time()

            instant_fps = (
                1.0
                / max(
                    now - prev_time,
                    1e-6,
                )
            )

            # Smooth FPS value
            if fps:

                fps = (
                    fps * 0.9
                    + instant_fps * 0.1
                )

            else:

                fps = instant_fps

            prev_time = now

            # ------------------------------------------------
            # DISPLAY LIVE CAMERA
            # ------------------------------------------------

            if args.show:

                draw_overlay(
                    frame,
                    tracked_objects,
                    snapshot,
                    fps,
                )

                cv2.imshow(
                    WINDOW_NAME,
                    frame,
                )

                key = cv2.waitKey(1) & 0xFF

                # Q or ESC
                if (
                    key == ord("q")
                    or key == 27
                ):

                    logger.info(
                        "Quit key pressed."
                    )

                    break

    except KeyboardInterrupt:

        logger.info(
            "Interrupted by user using Ctrl+C."
        )

    finally:

        # ----------------------------------------------------
        # RELEASE CAMERA
        # ----------------------------------------------------

        cap.release()

        cv2.destroyAllWindows()

        # ----------------------------------------------------
        # PRINT FINAL RESULTS
        # ----------------------------------------------------

        print_session_summary(
            snapshot
        )

        logger.info(
            "Camera released. Clean shutdown."
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()