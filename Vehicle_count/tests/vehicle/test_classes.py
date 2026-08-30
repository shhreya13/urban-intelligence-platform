from ai.vehicle.classes import (
    SUPPORTED_CLASSES,
    SUPPORTED_CLASS_IDS,
    class_name_from_id,
    is_supported_class,
)


def test_only_five_classes_supported():
    assert set(SUPPORTED_CLASSES) == {"car", "motorcycle", "bus", "truck", "person"}
    assert len(SUPPORTED_CLASS_IDS) == 5


def test_excluded_classes_are_rejected():
    # bicycle=1, traffic light=9, bench=13, dog=16 in standard COCO ordering
    for excluded_id in (1, 9, 13, 16):
        assert not is_supported_class(excluded_id)


def test_class_name_lookup():
    assert class_name_from_id(2) == "car"
    assert class_name_from_id(0) == "person"
    assert class_name_from_id(999) == "unknown"  # never raises, just falls back
