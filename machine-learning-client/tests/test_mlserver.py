"""Tests for mlserver Flask endpoint."""

import io
from unittest.mock import patch, MagicMock
import mlserver


def test_no_video():
    """Missing video file returns 400."""
    client = mlserver.app.test_client()
    resp = client.post("/analyze", data={})
    assert resp.status_code == 400

@patch("app.current_user", MagicMock(id="507f1f77bcf86cd799439011", is_authenticated=True))
@patch("mlserver.analyze_vision", return_value={"eye_contact_score": 90})
@patch("mlserver.analyze_speech", return_value={"transcript": "hi"})
@patch("mlserver.get_duration", return_value=12.5)
def test_analyze_success(mock_dur, _mock_speech, _mock_vision):
    """Valid upload returns speech and vision results."""
    client = mlserver.app.test_client()
    data = {"video": (io.BytesIO(b"fake video"), "test.webm")}
    resp = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["speech"]["duration_seconds"] == 12.5
    assert body["vision"]["eye_contact_score"] == 90
    mock_dur.assert_called_once()


@patch("mlserver.analyze_speech", side_effect=RuntimeError("boom"))
def test_analyze_error(_mock_speech):
    """Exception during analysis returns 500."""
    client = mlserver.app.test_client()
    data = {"video": (io.BytesIO(b"fake"), "test.webm")}
    resp = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert resp.status_code == 500
    assert "boom" in resp.get_json()["error"]


@patch("mlserver.subprocess.run")
def test_get_duration(mock_run):
    """get_duration parses ffprobe output."""
    mock_run.return_value = MagicMock(stdout="0.0\n5.2\n10.4\n")
    assert mlserver.get_duration("fake.webm") == 10.4


@patch("mlserver.subprocess.run")
def test_get_duration_bad_output(mock_run):
    """get_duration returns 0 on bad output."""
    mock_run.return_value = MagicMock(stdout="")
    assert mlserver.get_duration("fake.webm") == 0.0
