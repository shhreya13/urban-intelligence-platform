"""
Timestamp utility -- Person 3 module.

Turns (frame_id, fps, video_start_time) into an ISO-8601 timestamp:

    video_time_seconds = frame_id / fps
    timestamp = video_start_time + video_time_seconds

Kept in its own module so every other file (gps_simulator.py,
event_engine.py) computes timestamps exactly the same way -- there is only
ONE place that does this math.
"""

from datetime import datetime, timedelta


def get_video_start_time(video_start_time=None) -> datetime:
    """Returns a datetime to treat as frame 0's real-world time.
    Defaults to 'now' if not given, so a demo run has a sensible timestamp
    without needing any configuration."""
    if video_start_time is None:
        return datetime.now()
    if isinstance(video_start_time, datetime):
        return video_start_time
    return datetime.fromisoformat(video_start_time)  # allow an ISO string too


def generate_timestamp(frame_id: int, fps: float, video_start_time=None) -> str:
    """
    frame_id: frame number of the detection
    fps: frames per second of the source video
    video_start_time: datetime or ISO string marking frame 0's real-world
                       time (defaults to 'now' if not given)

    Returns an ISO-8601 timestamp string with milliseconds, e.g.
        2026-08-30T10:32:14.630
    """
    if fps <= 0:
        raise ValueError(f"fps must be > 0, got {fps}")
    if frame_id < 0:
        raise ValueError(f"frame_id must be >= 0, got {frame_id}")

    start = get_video_start_time(video_start_time)
    video_time_seconds = frame_id / fps
    ts = start + timedelta(seconds=video_time_seconds)
    return ts.isoformat(timespec="milliseconds")


if __name__ == "__main__":
    # Manual check matching the example in the brief:
    #   FPS = 30, frame_id = 1420  ->  video_time = 1420/30 = 47.33s
    example_start = datetime(2026, 8, 30, 10, 31, 27, 300000)
    print(generate_timestamp(frame_id=1420, fps=30, video_start_time=example_start))
