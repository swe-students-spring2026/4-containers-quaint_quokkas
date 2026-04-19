"""
Speech Practice Tool - Flask backend for recording and analyzing practice sessions.
"""
from datetime import datetime, timedelta
import uuid

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ============================================================================
# ROUTES - Serve the web pages
# ============================================================================


@app.route("/")
def dashboard():
    """Render the dashboard page showing past sessions."""
    return render_template("dashboard.html")


@app.route("/record")
def record():
    """Render the recording page for new practice sessions."""
    return render_template("record.html")


@app.route("/session/<session_id>")
def session_detail(session_id):
    """Render the session results page."""
    return render_template("session.html", session_id=session_id)


# ============================================================================
# API ENDPOINTS - Mock implementations
# ============================================================================


@app.route("/api/analyze/speech", methods=["POST"])
def analyze_speech():
    """
    Mock speech analysis endpoint.
    Returns filler words, WPM, and transcript analysis.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    session_id = request.form.get("session_id", str(uuid.uuid4()))

    # Mock response - will be replaced by real Whisper integration
    mock_transcript = (
        "Thank you for having me today. Um, I'm really excited to talk about this "
        "project. So, like, we spent a lot of time thinking about the user experience. "
        "Actually, you know, the biggest challenge was making sure everything works "
        "smoothly. Uh, we tested it carefully and the performance was really good. "
        "I think basically what we learned is that planning ahead is incredibly "
        "important."
    )

    return jsonify(
        {
            "session_id": session_id,
            "duration_seconds": 245.0,
            "transcript": mock_transcript,
            "word_count": 72,
            "wpm_overall": 128.5,
            "fillers": {
                "total": 8,
                "per_minute": 1.96,
                "breakdown": {
                    "um": 2,
                    "like": 1,
                    "so": 1,
                    "you know": 1,
                    "actually": 1,
                    "uh": 1,
                    "basically": 1,
                },
            },
            "pauses": {"long_pause_count": 3, "filled_pause_count": 2},
        }
    )


@app.route("/api/analyze/facial", methods=["POST"])
def analyze_facial():
    """
    Mock facial analysis endpoint.
    Returns eye contact and expression metrics.
    """
    data = request.get_json()
    session_id = data.get("session_id", str(uuid.uuid4()))

    # Mock response - will be replaced by real MediaPipe analysis
    return jsonify(
        {
            "session_id": session_id,
            "frames_analyzed": 1225,
            "eye_contact": {
                "pct_looking_at_camera": 0.71,
                "longest_break_seconds": 4.2,
            },
            "expression": {
                "smile_mean": 0.14,
                "smile_std": 0.09,
                "neutral_pct": 0.79,
            },
        }
    )


@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    """Fetch all sessions for the dashboard with trend data."""
    # Generate mock session history
    sessions_list = []
    for i in range(1, 11):  # 10 past sessions
        created_at = datetime.now() - timedelta(days=15 - i)

        # Vary metrics slightly for trend visualization
        base_fillers = 2.5 - (i * 0.08)
        base_wpm = 125 + (i * 0.5)
        base_eye_contact = 0.68 + (i * 0.004)

        sessions_list.append(
            {
                "session_id": f"session_{i}",
                "title": f"Practice Session {i}",
                "created_at": created_at.isoformat(),
                "duration_seconds": 245,
                "fillers_per_minute": round(base_fillers, 2),
                "wpm": round(base_wpm, 1),
                "eye_contact_pct": round(base_eye_contact * 100, 1),
            }
        )

    return jsonify(sessions_list)


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    """Fetch a specific session's full analysis data."""
    mock_transcript = (
        "Thank you for having me today. Um, I'm really excited to talk about this "
        "project. So, like, we spent a lot of time thinking about the user experience. "
        "Actually, you know, the biggest challenge was making sure everything works "
        "smoothly. Uh, we tested it carefully and the performance was really good. "
        "I think basically what we learned is that planning ahead is incredibly "
        "important."
    )

    return jsonify(
        {
            "session_id": session_id,
            "title": "Practice Session",
            "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
            "duration_seconds": 245.0,
            "transcript": mock_transcript,
            "word_count": 72,
            "wpm_overall": 128.5,
            "fillers_total": 8,
            "fillers_per_minute": 1.96,
            "fillers_breakdown": {
                "um": 2,
                "like": 1,
                "so": 1,
                "you know": 1,
                "actually": 1,
                "uh": 1,
                "basically": 1,
            },
            "eye_contact_pct": 71.0,
            "longest_break_seconds": 4.2,
            "long_pause_count": 3,
            "filled_pause_count": 2,
            "smile_mean": 0.14,
            "neutral_pct": 79.0,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
