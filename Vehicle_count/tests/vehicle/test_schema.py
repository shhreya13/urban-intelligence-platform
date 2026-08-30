import dataclasses

from ai.vehicle.tracker import TrackedObject


def test_tracked_object_schema_matches_event_engine_contract():
    obj = TrackedObject(
        object_type="car",
        track_id=17,
        confidence=0.91,
        bbox=(120, 80, 300, 250),
        frame_id=1234,
        timestamp="2026-08-30T11:20:15.230+05:30",
    )
    data = obj.to_dict()

    expected_keys = {"object_type", "track_id", "confidence", "bbox", "frame_id", "timestamp"}
    assert set(data.keys()) == expected_keys
    assert dataclasses.is_dataclass(obj)


def test_person_uses_object_type_not_vehicle_type():
    obj = TrackedObject(
        object_type="person",
        track_id=23,
        confidence=0.88,
        bbox=(400, 100, 470, 290),
        frame_id=1234,
        timestamp="2026-08-30T11:20:15.230+05:30",
    )
    data = obj.to_dict()
    assert "vehicle_type" not in data
    assert data["object_type"] == "person"
