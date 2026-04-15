"""Tests for classifier module."""

from unittest.mock import MagicMock
from types import SimpleNamespace
import numpy as np
from classifier import (
    straightness_ratio,
    get_finger_states,
    classify_gesture,
    classify_frame,
    FINGER_LANDMARKS,
)


def _lm(x, y, z=0.0):
    """Make a fake landmark."""
    return SimpleNamespace(x=x, y=y, z=z)


def _make_landmarks(extended):
    """Make fake landmarks with given fingers straight."""
    landmarks = [_lm(0.5, 0.5)] * 21
    for name, (mcp, pip, dip, tip) in FINGER_LANDMARKS.items():
        if name in extended:
            landmarks[mcp] = _lm(0.5, 0.3)
            landmarks[pip] = _lm(0.5, 0.4)
            landmarks[dip] = _lm(0.5, 0.5)
            landmarks[tip] = _lm(0.5, 0.6)
        else:
            landmarks[mcp] = _lm(0.5, 0.3)
            landmarks[pip] = _lm(0.5, 0.5)
            landmarks[dip] = _lm(0.7, 0.5)
            landmarks[tip] = _lm(0.7, 0.3)
    return landmarks


def _mock_landmarker(landmarks):
    """Make a mock landmarker returning given landmarks."""
    result = SimpleNamespace(
        hand_landmarks=[landmarks] if landmarks else [],
        handedness=([[SimpleNamespace(category_name="Right")]] if landmarks else []),
    )
    mock = MagicMock()
    mock.detect.return_value = result
    return mock


def test_straight_finger_ratio():
    """Straight finger should have ratio near 1."""
    r = straightness_ratio(_lm(0, 0), _lm(0, 0.1), _lm(0, 0.2), _lm(0, 0.3))
    assert abs(r - 1.0) < 0.001


def test_curled_finger_ratio():
    """Curled finger should have ratio far below 1."""
    r = straightness_ratio(_lm(0, 0), _lm(0, 0.2), _lm(0.2, 0.2), _lm(0.2, 0))
    assert r < 0.5


def test_zero_path_ratio():
    """Points at same spot should all return 0."""
    p = _lm(0.5, 0.5)
    assert straightness_ratio(p, p, p, p) == 0.0


def test_all_extended():
    """Straight fingers should be labeled as extended."""
    states = get_finger_states(_make_landmarks({"index", "middle", "ring", "pinky"}))
    assert all(states.values())


def test_all_curled():
    """No fingers straight should all be curled."""
    states = get_finger_states(_make_landmarks(set()))
    assert not any(states.values())


def test_scissors_fingers():
    """Index and middle extended, ring and pinky curled."""
    states = get_finger_states(_make_landmarks({"index", "middle"}))
    assert states["index"] and states["middle"]
    assert not states["ring"] and not states["pinky"]


def test_rock():
    """All curled should be rock."""
    states = {
        "index": False,
        "middle": False,
        "ring": False,
        "pinky": False,
    }
    assert classify_gesture(states) == "rock"


def test_paper():
    """All extended should be paper."""
    states = {
        "index": True,
        "middle": True,
        "ring": True,
        "pinky": True,
    }
    assert classify_gesture(states) == "paper"


def test_scissors():
    """Index and middle extended should be scissors."""
    states = {
        "index": True,
        "middle": True,
        "ring": False,
        "pinky": False,
    }
    assert classify_gesture(states) == "scissors"


def test_unknown():
    """Only index extended should be unknown."""
    states = {
        "index": True,
        "middle": False,
        "ring": False,
        "pinky": False,
    }
    assert classify_gesture(states) == "unknown"


def test_no_hand():
    """No hand detected should return no_hand."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    gesture, lm = classify_frame(frame, landmarker=_mock_landmarker(None))
    assert gesture == "no_hand"
    assert lm is None


def test_rock_frame():
    """Frame with all fingers curled should classify as rock."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    gesture, _ = classify_frame(
        frame, landmarker=_mock_landmarker(_make_landmarks(set()))
    )
    assert gesture == "rock"


def test_paper_frame():
    """Frame with all fingers extended should classify as paper."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    lm = _make_landmarks({"index", "middle", "ring", "pinky"})
    gesture, _ = classify_frame(frame, landmarker=_mock_landmarker(lm))
    assert gesture == "paper"


def test_scissors_frame():
    """Frame with index+middle extended should be scissors."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    lm = _make_landmarks({"index", "middle"})
    gesture, _ = classify_frame(frame, landmarker=_mock_landmarker(lm))
    assert gesture == "scissors"
