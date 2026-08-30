"""
Duplicate-event suppression -- Person 3 module.

PROBLEM: the same physical pothole gets detected on many consecutive
frames as the bus drives past it (frame 100, 101, 102, 103, ...). Without
suppression that's dozens of "events" for one real-world thing.

RULE (deliberately simple -- no tracking algorithm):
    Two detections of the SAME event_type are considered the SAME event if
    BOTH are true:
        1. They happen within DUPLICATE_TIME_WINDOW seconds of each other
           (default 5s).
        2. Their simulated GPS positions are within
           DUPLICATE_DISTANCE_METERS of each other (default 15m).
    Only the FIRST detection in such a cluster becomes an event; every
    later one that still falls inside the time+distance window is
    suppressed.

    This only remembers the LAST ACCEPTED event per event_type and
    compares each new detection to it -- that is enough for one bus with
    one camera per event type, which is exactly the MVP's scope. Both
    thresholds are configurable in config.py.
"""

from datetime import datetime

import config
from gps_simulator import haversine_meters


class DuplicateFilter:
    def __init__(self, time_window=None, distance_meters=None):
        self.time_window = config.DUPLICATE_TIME_WINDOW if time_window is None else time_window
        self.distance_meters = (
            config.DUPLICATE_DISTANCE_METERS if distance_meters is None else distance_meters
        )
        self._last_event = {}  # event_type -> {"timestamp": datetime, "lat":, "lon":}

    def is_duplicate(self, event_type: str, lat: float, lon: float, timestamp: str) -> bool:
        """Returns True if this detection should be SUPPRESSED (it's a
        duplicate of a very recent, very nearby detection of the same
        type). Regardless of the result, this detection is recorded as the
        new 'last seen' for its event_type, so the next call compares
        against the most recent one."""
        ts = datetime.fromisoformat(timestamp)
        last = self._last_event.get(event_type)

        duplicate = False
        if last is not None:
            time_gap = abs((ts - last["timestamp"]).total_seconds())
            distance = haversine_meters((lat, lon), (last["lat"], last["lon"]))
            duplicate = time_gap <= self.time_window and distance <= self.distance_meters

        if not duplicate:
            self._last_event[event_type] = {"timestamp": ts, "lat": lat, "lon": lon}

        return duplicate

    def reset(self):
        self._last_event.clear()
