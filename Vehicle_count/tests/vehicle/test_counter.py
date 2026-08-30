from ai.vehicle.counter import ObjectCounter
from ai.vehicle.tracker import TrackedObject


def _obj(track_id, y, object_type="car", frame_id=1):
    return TrackedObject(
        object_type=object_type,
        track_id=track_id,
        confidence=0.9,
        bbox=(10, y - 5, 30, y + 5),
        frame_id=frame_id,
        timestamp="2026-08-30T12:00:00.000+05:30",
    )


def test_current_visible_count_deduplicates_by_track_id():
    """The same car ID appearing in 100 frames must count as ONE visible
    object in the CURRENT frame, not as 100 detections."""
    counter = ObjectCounter(line=((0, 100), (200, 100)))
    snapshot = None
    for frame_number in range(1, 6):
        snapshot = counter.update([_obj(track_id=7, y=50, frame_id=frame_number)])

    assert snapshot.current_by_class["car"] == 1
    assert snapshot.current_total == 1


def test_current_visible_count_drops_to_zero_when_object_leaves():
    counter = ObjectCounter()
    counter.update([_obj(track_id=1, y=50)])
    snapshot = counter.update([])  # object no longer detected this frame
    assert snapshot.current_by_class["car"] == 0
    assert snapshot.current_total == 0


def test_line_crossing_counted_once_per_track_id():
    counter = ObjectCounter(line=((0, 100), (200, 100)))

    counter.update([_obj(track_id=1, y=50)])              # above the line
    snapshot = counter.update([_obj(track_id=1, y=150)])   # crosses below -> +1
    assert snapshot.crossings_by_class["car"] == 1

    # Wobbling near the line afterwards must NOT increment the count again.
    snapshot = counter.update([_obj(track_id=1, y=160)])
    assert snapshot.crossings_by_class["car"] == 1

    snapshot = counter.update([_obj(track_id=1, y=50)])  # crosses back upward
    assert snapshot.crossings_by_class["car"] == 1  # same ID, never double-counted


def test_different_track_ids_counted_independently():
    counter = ObjectCounter(line=((0, 100), (200, 100)))
    counter.update([_obj(track_id=1, y=50), _obj(track_id=2, y=50, object_type="truck")])
    snapshot = counter.update([_obj(track_id=1, y=150), _obj(track_id=2, y=150, object_type="truck")])
    assert snapshot.crossings_by_class["car"] == 1
    assert snapshot.crossings_by_class["truck"] == 1
