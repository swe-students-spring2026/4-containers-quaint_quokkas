"""Tests for the Flask web app. Mongo and ML client are mocked."""

# pylint: disable=redefined-outer-name

import io
from unittest.mock import patch, MagicMock
import pytest
import requests as req_lib
import app as webapp
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    """Create a test client."""
    webapp.app.config["TESTING"] = True
    webapp.app.config["LOGIN_DISABLED"] = True
    return webapp.app.test_client()


def test_dashboard(client):
    """Dashboard page loads."""
    resp = client.get("/")
    assert resp.status_code == 200


def test_record_page(client):
    """Record page loads."""
    resp = client.get("/record")
    assert resp.status_code == 200


def test_session_page(client):
    """Session detail page loads."""
    resp = client.get("/session/abc123")
    assert resp.status_code == 200


def test_analyze_no_video(client):
    """Missing video returns 400."""
    resp = client.post("/api/analyze", data={})
    assert resp.status_code == 400


@patch(
    "app.current_user", MagicMock(id="507f1f77bcf86cd799439011", is_authenticated=True)
)
@patch("app.sessions_collection")
@patch("app.requests.post")
def test_analyze_success(mock_post, mock_coll, client):
    """Analyze stores session and returns results."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "speech": {
                "transcript": "hello",
                "total_words": 10,
                "filler_counts": {"um": 2},
                "duration_seconds": 30,
            },
            "vision": {"total_frames": 100, "eye_contact_score": 75},
        },
    )
    mock_post.return_value.raise_for_status = MagicMock()
    mock_coll.count_documents.return_value = 0

    data = {"video": (io.BytesIO(b"fake"), "test.webm"), "session_id": "s1"}
    resp = client.post("/api/analyze", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["session_id"] == "s1"
    assert body["fillers"]["total"] == 2
    mock_coll.update_one.assert_called_once()


@patch("app.requests.post", side_effect=req_lib.exceptions.RequestException("down"))
def test_analyze_ml_down(_mock_post, client):
    """ML client unreachable returns 502."""
    data = {"video": (io.BytesIO(b"fake"), "test.webm")}
    resp = client.post("/api/analyze", data=data, content_type="multipart/form-data")
    assert resp.status_code == 502


@patch("app.requests.post")
def test_analyze_ml_error(mock_post, client):
    """Error in ML response body returns 500."""
    mock_post.return_value = MagicMock(json=lambda: {"error": "bad"})
    mock_post.return_value.raise_for_status = MagicMock()
    data = {"video": (io.BytesIO(b"fake"), "test.webm")}
    resp = client.post("/api/analyze", data=data, content_type="multipart/form-data")
    assert resp.status_code == 500


@patch(
    "app.current_user", MagicMock(id="507f1f77bcf86cd799439011", is_authenticated=True)
)
@patch("app.sessions_collection")
def test_get_sessions(mock_coll, client):
    """Sessions API returns list."""
    cursor = MagicMock()
    cursor.sort.return_value = [
        {
            "session_id": "a",
            "title": "S1",
            "created_at": "now",
            "duration_seconds": 30,
            "fillers": {"per_minute": 4},
            "wpm_overall": 120,
            "eye_contact_pct": 80,
        }
    ]
    mock_coll.find.return_value = cursor
    resp = client.get("/api/sessions")
    assert resp.status_code == 200
    assert resp.get_json()[0]["session_id"] == "a"


@patch(
    "app.current_user", MagicMock(id="507f1f77bcf86cd799439011", is_authenticated=True)
)
@patch("app.sessions_collection")
def test_get_session_not_found(mock_coll, client):
    """Missing session returns 404."""
    mock_coll.find_one.return_value = None
    resp = client.get("/api/sessions/nope")
    assert resp.status_code == 404


@patch(
    "app.current_user", MagicMock(id="507f1f77bcf86cd799439011", is_authenticated=True)
)
@patch("app.sessions_collection")
def test_get_session_found(mock_coll, client):
    """Existing session returns full data."""
    mock_coll.find_one.return_value = {
        "session_id": "s1",
        "title": "S1",
        "created_at": "now",
        "duration_seconds": 30,
        "transcript": "hi",
        "word_count": 10,
        "wpm_overall": 20,
        "fillers": {"total": 2, "per_minute": 4, "breakdown": {"um": 2}},
        "pauses": {"long_pause_count": 1, "filled_pause_count": 0},
        "eye_contact_pct": 90,
    }
    resp = client.get("/api/sessions/s1")
    assert resp.status_code == 200
    assert resp.get_json()["fillers_total"] == 2

@patch("app.users_collection")
def test_register_get(mock_users, client):
    """Register page loads."""
    resp = client.get("/register")
    assert resp.status_code == 200


@patch("app.login_user")
@patch("app.users_collection")
def test_register_post(mock_users, mock_login, client):
    """Successful registration redirects to dashboard."""
    mock_users.find_one.return_value = None
    mock_users.insert_one.return_value = MagicMock(inserted_id="abc123")
    resp = client.post("/register", data={"username": "newuser", "password": "pass123"})
    assert resp.status_code == 302


@patch("app.users_collection")
def test_register_duplicate(mock_users, client):
    """Duplicate username shows error."""
    mock_users.find_one.return_value = {"username": "taken"}
    resp = client.post("/register", data={"username": "taken", "password": "pass"})
    assert resp.status_code == 200
    assert b"already exists" in resp.data


@patch("app.login_user")
@patch("app.users_collection")
def test_login_success(mock_users, mock_login, client):
    """Valid login redirects to dashboard."""
    mock_users.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "username": "testuser",
        "password": generate_password_hash("pass123"),
    }
    resp = client.post("/login", data={"username": "testuser", "password": "pass123"})
    assert resp.status_code == 302


@patch("app.users_collection")
def test_login_fail(mock_users, client):
    """Invalid login shows error."""
    mock_users.find_one.return_value = None
    resp = client.post("/login", data={"username": "bad", "password": "bad"})
    assert resp.status_code == 200
    assert b"Invalid" in resp.data


def test_logout(client):
    """Logout redirects to login."""
    resp = client.get("/logout")
    assert resp.status_code == 302
