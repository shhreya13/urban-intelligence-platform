"""
GPS Simulator -- Person 3 module.

No physical GPS hardware for the MVP. Instead the bus is simulated as
driving at a constant speed (config.BUS_SPEED_KMPH) along a fixed route
(config.ROUTE), and we interpolate its position for any given frame.

HOW IT WORKS (kept deliberately simple):
    1. video_time_seconds = frame_id / fps            -> how far into the video are we
    2. distance_travelled = video_time_seconds * speed  -> how far has the bus driven
    3. Walk the route waypoint by waypoint, subtracting each segment's
       length from distance_travelled, until we find the segment the bus
       is currently on.
    4. Linearly interpolate between that segment's two waypoints using how
       far into the segment the bus is (0.0 = at the first point, 1.0 = at
       the second).
    5. Add a little random jitter, because real GPS fixes are noisy too.

If the bus "drives" past the end of the route, it loops back to the start
-- good enough for a demo where the video is longer than the sample route.
"""

import math
import random

import config

_rng = random.Random(42)  # fixed seed -> reproducible demo output


def haversine_meters(p1, p2) -> float:
    """Great-circle distance between two (lat, lon) points, in meters."""
    R = 6371000.0
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _segment_lengths(route):
    return [haversine_meters(route[i], route[i + 1]) for i in range(len(route) - 1)]


def _add_jitter(lat, lon, jitter_meters):
    if jitter_meters <= 0:
        return lat, lon
    dlat = (_rng.uniform(-1, 1) * jitter_meters) / 111320.0
    dlon = (_rng.uniform(-1, 1) * jitter_meters) / (111320.0 * math.cos(math.radians(lat)))
    return lat + dlat, lon + dlon


def get_gps_position(frame_id: int, fps: float, route=None, speed_kmph=None, jitter_meters=None):
    """
    Returns the simulated (latitude, longitude) of the bus at the given
    frame.

        elapsed_seconds = frame_id / fps
        distance = elapsed_seconds * speed
        (lat, lon) = interpolate(route, distance)
    """
    route = route or config.ROUTE
    speed_kmph = config.BUS_SPEED_KMPH if speed_kmph is None else speed_kmph
    jitter_meters = config.GPS_JITTER_METERS if jitter_meters is None else jitter_meters

    if fps <= 0:
        raise ValueError(f"fps must be > 0, got {fps}")
    if len(route) < 2:
        raise ValueError("ROUTE must contain at least 2 waypoints")

    seg_lengths = _segment_lengths(route)
    total_length = sum(seg_lengths)
    speed_mps = speed_kmph * 1000 / 3600

    elapsed_seconds = frame_id / fps
    distance = elapsed_seconds * speed_mps
    if total_length > 0:
        distance = distance % total_length  # loop the route

    covered = 0.0
    for i, seg_len in enumerate(seg_lengths):
        if covered + seg_len >= distance or i == len(seg_lengths) - 1:
            frac = 0.0 if seg_len == 0 else (distance - covered) / seg_len
            frac = max(0.0, min(1.0, frac))
            p1, p2 = route[i], route[i + 1]
            lat = p1[0] + (p2[0] - p1[0]) * frac
            lon = p1[1] + (p2[1] - p1[1]) * frac
            return _add_jitter(lat, lon, jitter_meters)
        covered += seg_len

    return _add_jitter(route[-1][0], route[-1][1], jitter_meters)


if __name__ == "__main__":
    for frame in (0, 30, 150, 300, 600):
        lat, lon = get_gps_position(frame, fps=30)
        print(f"frame {frame:5d}  lat={lat:.6f}  lon={lon:.6f}")
