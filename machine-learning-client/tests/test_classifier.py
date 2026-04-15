"""Tests for classifier module."""

from unittest.mock import MagicMock
from types import SimpleNamespace
import numpy as np
from classifier import straightness_ratio, get_finger_states, classify_gesture, classify_frame, FINGER_LANDMARKS


def _lm(x, y, z=0.0):
    return SimpleNamespace(x=x, y=y, z=z)


def _make_landmarks(extended):
    """Make fake landmarks. extended is a set of finger names that should be straight."""
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
    result = SimpleNamespace(
        hand_landmarks=[landmarks] if landmarks else [],
        handedness=[[SimpleNamespace(category_name="Right")]] if landmarks else [],
    )
    mock = MagicMock()
    mock.detect.return_value = result
    return mock


# straightness ratio tests

def test_straight_finger_ratio():
    r = straightness_ratio(_lm(0, 0), _lm(0, 0.1), _lm(0, 0.2), _lm(0, 0.3))
    assert abs(r - 1.0) < 0.001

def test_curled_finger_ratio():
    r = straightness_ratio(_lm(0, 0), _lm(0, 0.2), _lm(0.2, 0.2), _lm(0.2, 0))
    assert r < 0.5

def test_zero_path_ratio():
    p = _lm(0.5, 0.5)
    assert straightness_ratio(p, p, p, p) == 0.0


# get_finger_states tests

def test_all_extended():
    states = get_finger_states(_make_landmarks({"index", "middle", "ring", "pinky"}))
    assert all(states.values())

def test_all_curled():
    states = get_finger_states(_make_landmarks(set()))
    assert not any(states.values())

def test_scissors_fingers():
    states = get_finger_states(_make_landmarks({"index", "middle"}))
    assert states["index"] and states["middle"]
    assert not states["ring"] and not states["pinky"]


# classify_gesture tests

def test_rock():
    assert classify_gesture({"index": False, "middle": False, "ring": False, "pinky": False}) == "rock"

def test_paper():
    assert classify_gesture({"index": True, "middle": True, "ring": True, "pinky": True}) == "paper"

def test_scissors():
    assert classify_gesture({"index": True, "middle": True, "ring": False, "pinky": False}) == "scissors"

def test_unknown():
    assert classify_gesture({"index": True, "middle": False, "ring": False, "pinky": False}) == "unknown"


# classify_frame tests

def test_no_hand():
    gesture, lm = classify_frame(np.zeros((480, 640, 3), dtype=np.uint8), landmarker=_mock_landmarker(None))
    assert gesture == "no_hand"
    assert lm is None

def test_rock_frame():
    gesture, _ = classify_frame(np.zeros((480, 640, 3), dtype=np.uint8), landmarker=_mock_landmarker(_make_landmarks(set())))
    assert gesture == "rock"

def test_paper_frame():
    gesture, _ = classify_frame(np.zeros((480, 640, 3), dtype=np.uint8), landmarker=_mock_landmarker(_make_landmarks({"index", "middle", "ring", "pinky"})))
    assert gesture == "paper"

def test_scissors_frame():
    gesture, _ = classify_frame(np.zeros((480, 640, 3), dtype=np.uint8), landmarker=_mock_landmarker(_make_landmarks({"index", "middle"})))
    assert gesture == "scissors"