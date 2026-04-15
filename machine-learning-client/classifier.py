"""Classify a hand gesture as rock, paper, scissors, or unknown using MediaPipe."""

import os
import math
import mediapipe as mp
import cv2

# Landmark indices: MCP, PIP, DIP, TIP for each finger (excluding thumb)
FINGER_LANDMARKS = {
    "index": (5, 6, 7, 8),
    "middle": (9, 10, 11, 12),
    "ring": (13, 14, 15, 16),
    "pinky": (17, 18, 19, 20),
}

# Per-finger straightness thresholds
STRAIGHTNESS_THRESHOLDS = {
    "index": 0.96,
    "middle": 0.94,
    "ring": 0.94,
    "pinky": 0.96,
}

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task"
)


def _dist(a, b):
    """Euclidean distance between two landmarks."""
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def straightness_ratio(mcp, pip, dip, tip):
    """Compute the straightness ratio of a finger.

    The "straightness ratio" is the dist (MCP->TIP) divided by path distance
    (MCP->PIP->DIP->TIP). A straight finger gets about 1.0, a curled finger
    is lower.

    Initially, I wanted to simply use the PIP joint angle to classify
    straightness. That didn't work very well, even after testing every
    possible angle for each finger. So I came up with this method which
    works much better.
    """
    path = _dist(mcp, pip) + _dist(pip, dip) + _dist(dip, tip)
    if path == 0:
        return 0.0
    direct = _dist(mcp, tip)
    return direct / path


def get_finger_states(landmarks):
    """Return a dict of {finger_name: bool} indicating extended or curled.

    Compares each finger's "straightness ratio" (see straightness_ratio(mcp, pip, dip, tip)
    to the threshold specified in STRAIGHTNESS_THRESHOLDS
    """
    states = {}
    for name, (mcp_idx, pip_idx, dip_idx, tip_idx) in FINGER_LANDMARKS.items():
        ratio = straightness_ratio(
            landmarks[mcp_idx],
            landmarks[pip_idx],
            landmarks[dip_idx],
            landmarks[tip_idx],
        )
        states[name] = ratio >= STRAIGHTNESS_THRESHOLDS[name]
    return states


def classify_gesture(finger_states):
    """Given the finger states, return the gesture.

    Returns one of: "rock", "paper", "scissors", "unknown".

    I elected to disregard the thumb because, if you think about it,
    the thumb can kinda do whatever it wants in rock/paper/scissors.

    A thumbs-up is still a rock; a German three (re: Inglorious Basterds)
    is still scissors; an American four is still paper.
    """
    index = finger_states["index"]
    middle = finger_states["middle"]
    ring = finger_states["ring"]
    pinky = finger_states["pinky"]

    extended_count = sum(finger_states.values())

    # Paper: all four extended
    if extended_count >= 4:
        return "paper"

    # Scissors: index and middle extended, ring and pinky curled
    if index and middle and not ring and not pinky:
        return "scissors"

    # Rock: all four curled
    if extended_count == 0:
        return "rock"

    return "unknown"


def _create_landmarker(model_path=None):
    """Create a HandLandmarker instance using the Tasks API."""
    path = model_path or MODEL_PATH
    base_options = mp.tasks.BaseOptions(model_asset_path=path)
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.5,
    )
    return mp.tasks.vision.HandLandmarker.create_from_options(options)


def classify_frame(frame, landmarker=None):
    """Classify the gesture in an OpenCV BGR frame.

    Args:
        frame: A BGR numpy array from OpenCV.
        landmarker: An optional pre-created HandLandmarker instance.
            If None, a new one is created (and closed) each call.

    Returns:
        (str, list | None): A tuple of (gesture, landmarks).
        gesture is one of "rock", "paper", "scissors", "unknown", "no_hand".
        landmarks is the list of 21 landmark objects, or None if no hand found.
    """
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # pylint: disable=no-member
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    owns_landmarker = landmarker is None
    if owns_landmarker:
        landmarker = _create_landmarker()

    try:
        result = landmarker.detect(mp_image)
    finally:
        if owns_landmarker:
            landmarker.close()

    if not result.hand_landmarks:
        return "no_hand", None

    landmarks = result.hand_landmarks[0]
    finger_states = get_finger_states(landmarks)
    gesture = classify_gesture(finger_states)

    return gesture, landmarks
