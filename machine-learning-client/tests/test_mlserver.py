"""Tests for mlserver Flask endpoint."""

import io
from unittest.mock import patch
import mlserver


def test_no_video():
    """Missing video file returns 400."""
    client = mlserver.app.test_client()
    resp = client.post("/analyze", data={})
    assert resp.status_code == 400


@patch("mlserver.analyze_vision", return_value={"eye_contact_score": 90})
@patch("mlserver.analyze_speech", return_value={"transcript": "hi"})
@patch("mlserver.VideoFileClip")
def test_analyze_success(mock_clip, _mock_speech, _mock_vision):
    """Valid upload returns speech and vision results."""
    mock_clip.return_value.duration = 12.5
    client = mlserver.app.test_client()
    data = {"video": (io.BytesIO(b"fake video"), "test.webm")}
    resp = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["speech"]["duration_seconds"] == 12.5
    assert body["vision"]["eye_contact_score"] == 90


@patch("mlserver.VideoFileClip", side_effect=RuntimeError("boom"))
def test_analyze_error(_mock_clip):
    """Exception during analysis returns 500."""
    client = mlserver.app.test_client()
    data = {"video": (io.BytesIO(b"fake"), "test.webm")}
    resp = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert resp.status_code == 500
    assert "boom" in resp.get_json()["error"]
