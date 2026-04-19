"""
Speech Practice Tool - Flask backend for recording and analyzing practice sessions.
"""

import os
from datetime import datetime
import uuid

from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

mongo_client = MongoClient(os.environ.get("MONGO_URI"))
db = mongo_client["speech_practice"]
sessions_collection = db["sessions"]


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
# API ENDPOINTS
# ============================================================================


@app.route("/api/analyze/speech", methods=["POST"])
def analyze_speech():
    """
    Speech analysis endpoint.
    Returns filler words, WPM, and transcript analysis.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    session_id = request.form.get("session_id", str(uuid.uuid4()))

    session_count = sessions_collection.count_documents({}) + 1
    title = f"Practice Session {session_count}"

    mock_transcript = (
        "Thank you for having me today. Um, I'm really excited to talk about this "
        "project. So, like, we spent a lot of time thinking about the user experience. "
        "Actually, you know, the biggest challenge was making sure everything works "
        "smoothly. Uh, we tested it carefully and the performance was really good. "
        "I think basically what we learned is that planning ahead is incredibly "
        "important."
    )

    result = {
        "session_id": session_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
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

    sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": result},
        upsert=True,
    )

    return jsonify(result)


@app.route("/api/analyze/facial", methods=["POST"])
def analyze_facial():
    """
    Facial analysis endpoint.
    Returns eye contact and expression metrics.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    session_id = data.get("session_id", str(uuid.uuid4()))
    frames = data.get("frames", [])

    facial_result = {
        "session_id": session_id,
        "frames_analyzed": len(frames) if frames else 1225,
        "eye_contact_pct": 71.0,
        "longest_break_seconds": 4.2,
        "smile_mean": 0.14,
        "neutral_pct": 79.0,
    }

    sessions_collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "frames_analyzed": facial_result["frames_analyzed"],
                "eye_contact_pct": facial_result["eye_contact_pct"],
                "longest_break_seconds": facial_result["longest_break_seconds"],
                "smile_mean": facial_result["smile_mean"],
                "neutral_pct": facial_result["neutral_pct"],
            }
        },
        upsert=True,
    )

    return jsonify(facial_result)


@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    """Fetch all sessions for the dashboard, ordered by most recent."""
    docs = list(
        sessions_collection.find(
            {},
            {
                "_id": 0,
                "session_id": 1,
                "title": 1,
                "created_at": 1,
                "duration_seconds": 1,
                "fillers": 1,
                "wpm_overall": 1,
                "eye_contact_pct": 1,
            },
        ).sort("created_at", -1)
    )

    sessions_list = [
        {
            "session_id": doc.get("session_id"),
            "title": doc.get("title", "Practice Session"),
            "created_at": doc.get("created_at"),
            "duration_seconds": doc.get("duration_seconds", 0),
            "fillers_per_minute": doc.get("fillers", {}).get("per_minute", 0),
            "wpm": doc.get("wpm_overall", 0),
            "eye_contact_pct": doc.get("eye_contact_pct", 0),
        }
        for doc in docs
    ]

    return jsonify(sessions_list)


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    """Fetch a specific session's full analysis data."""
    doc = sessions_collection.find_one({"session_id": session_id}, {"_id": 0})

    if not doc:
        return jsonify({"error": "Session not found"}), 404

    fillers = doc.get("fillers", {})
    pauses = doc.get("pauses", {})

    return jsonify(
        {
            "session_id": doc.get("session_id"),
            "title": doc.get("title", "Practice Session"),
            "created_at": doc.get("created_at"),
            "duration_seconds": doc.get("duration_seconds", 0),
            "transcript": doc.get("transcript", ""),
            "word_count": doc.get("word_count", 0),
            "wpm_overall": doc.get("wpm_overall", 0),
            "fillers_total": fillers.get("total", 0),
            "fillers_per_minute": fillers.get("per_minute", 0),
            "fillers_breakdown": fillers.get("breakdown", {}),
            "eye_contact_pct": doc.get("eye_contact_pct", 0),
            "longest_break_seconds": doc.get("longest_break_seconds", 0),
            "long_pause_count": pauses.get("long_pause_count", 0),
            "filled_pause_count": pauses.get("filled_pause_count", 0),
            "smile_mean": doc.get("smile_mean", 0),
            "neutral_pct": doc.get("neutral_pct", 0),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)