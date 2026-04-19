"""Tests for analyze_video. cv2 and mediapipe are mocked."""

from unittest.mock import patch, MagicMock
import numpy as np
import analyze_video


@patch("analyze_video.vision")
@patch("analyze_video.python")
@patch("analyze_video.cv2")
def test_no_frames(mock_cv2, _mock_python, mock_vision):
    """Empty video returns empty dict."""
    cap = MagicMock()
    cap.isOpened.return_value = True
    cap.read.return_value = (False, None)
    mock_cv2.VideoCapture.return_value = cap
    mock_vision.FaceLandmarker.create_from_options.return_value.__enter__.return_value = (
        MagicMock()
    )

    assert not analyze_video.analyze_vision("fake.mp4")


@patch("analyze_video.vision")
@patch("analyze_video.python")
@patch("analyze_video.mp")
@patch("analyze_video.cv2")
def test_looking_at_camera(mock_cv2, _mock_mp, _mock_python, mock_vision):
    """Frame with face looking straight gets Excellent."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cap = MagicMock()
    cap.isOpened.return_value = True
    cap.read.side_effect = [(True, frame), (False, None)]
    mock_cv2.VideoCapture.return_value = cap
    mock_cv2.COLOR_BGR2RGB = 0
    mock_cv2.cvtColor.return_value = frame
    mock_cv2.solvePnP.return_value = (True, np.zeros((3, 1)), None)
    mock_cv2.Rodrigues.return_value = (np.eye(3), None)
    mock_cv2.RQDecomp3x3.return_value = ([0.0, 0.0, 0.0], None, None, None, None, None)

    detector = MagicMock()
    lm = [MagicMock(x=0.5, y=0.5) for _ in range(300)]
    detector.detect.return_value.face_landmarks = [lm]
    mock_vision.FaceLandmarker.create_from_options.return_value.__enter__.return_value = (
        detector
    )

    result = analyze_video.analyze_vision("fake.mp4")
    assert result["total_frames"] == 1
    assert result["looking_frames"] == 1
    assert result["feedback"] == "Excellent"


@patch("analyze_video.vision")
@patch("analyze_video.python")
@patch("analyze_video.mp")
@patch("analyze_video.cv2")
def test_not_looking(mock_cv2, _mock_mp, _mock_python, mock_vision):
    """Head turned far to the side counts as not looking."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cap = MagicMock()
    cap.isOpened.return_value = True
    cap.read.side_effect = [(True, frame), (False, None)]
    mock_cv2.VideoCapture.return_value = cap
    mock_cv2.COLOR_BGR2RGB = 0
    mock_cv2.cvtColor.return_value = frame
    mock_cv2.solvePnP.return_value = (True, np.zeros((3, 1)), None)
    mock_cv2.Rodrigues.return_value = (np.eye(3), None)
    mock_cv2.RQDecomp3x3.return_value = (
        [30.0, 40.0, 0.0],
        None,
        None,
        None,
        None,
        None,
    )

    detector = MagicMock()
    lm = [MagicMock(x=0.5, y=0.5) for _ in range(300)]
    detector.detect.return_value.face_landmarks = [lm]
    mock_vision.FaceLandmarker.create_from_options.return_value.__enter__.return_value = (
        detector
    )

    result = analyze_video.analyze_vision("fake.mp4")
    assert result["looking_frames"] == 0
    assert result["feedback"] == "Needs work"
