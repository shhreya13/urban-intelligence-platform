from unittest.mock import MagicMock, patch

import pytest

from ai.vehicle import inference


def test_open_camera_exits_gracefully_when_camera_unavailable():
    """Simulates an unavailable camera (no physical webcam needed) and checks
    the module exits cleanly with a helpful message instead of crashing."""
    fake_cap = MagicMock()
    fake_cap.isOpened.return_value = False

    with patch("cv2.VideoCapture", return_value=fake_cap):
        with pytest.raises(SystemExit):
            inference.open_camera(index=5, width=640, height=480)

    fake_cap.release.assert_called_once()


def test_default_line_is_centered_horizontally():
    line = inference.default_line(frame_width=640, frame_height=480)
    (x1, y1), (x2, y2) = line
    assert y1 == y2 == 240
    assert x1 == 0
    assert x2 == 640
