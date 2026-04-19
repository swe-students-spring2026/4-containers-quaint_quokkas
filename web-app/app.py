"""
Speech Practice Tool - Flask backend for recording and analyzing practice sessions.
"""

import os
import uuid
from datetime import datetime

import requests
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

mongo_client = MongoClient(os.environ.get("MONGO_URI"))
db = mongo_client["speech_practice"]
sessions_collection = db["sessions"]

ML_CLIENT_URL = os.environ.get("ML_CLIENT_URL", "http://ml-client:8000")


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


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Receive a video upload, forward it to the ML client, and store the results."""
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    session_id = request.form.get("session_id", str(uuid.uuid4()))
    video_file = request.files["video"]

    try:
        ml_response = requests.post(
            f"{ML_CLIENT_URL}/analyze",
            files={"video": ("recording.webm", video_file.stream, "video/webm")},
            timeout=600,
        )
        ml_response.raise_for_status()
        ml_result = ml_response.json()
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": f"ML client unreachable: {exc}"}), 502

    if "error" in ml_result:
        return jsonify({"error": ml_result["error"]}), 500

    speech = ml_result.get("speech", {})
    vision = ml_result.get("vision", {})

    filler_counts = speech.get("filler_counts", {})
    total_fillers = sum(filler_counts.values())
    duration_seconds = speech.get("duration_seconds", 0)
    fillers_per_minute = (
        round((total_fillers / duration_seconds) * 60, 2)
        if duration_seconds > 0
        else 0.0
    )

    session_number = sessions_collection.count_documents({}) + 1

    result = {
        "session_id": session_id,
        "title": f"Practice Session {session_number}",
        "created_at": datetime.now().isoformat(),
        "duration_seconds": duration_seconds,
        "transcript": speech.get("transcript", ""),
        "word_count": speech.get("total_words", 0),
        "wpm_overall": round(speech.get("total_words", 0) / (duration_seconds / 60), 1) if duration_seconds > 0 else 0,
        "fillers": {
            "total": total_fillers,
            "per_minute": fillers_per_minute,
            "breakdown": filler_counts,
        },
        "pauses": {"long_pause_count": 0, "filled_pause_count": 0},
        "frames_analyzed": vision.get("total_frames", 0),
        "eye_contact_pct": vision.get("eye_contact_score", 0),
        "longest_break_seconds": 0,
        "smile_mean": 0,
        "neutral_pct": 0,
    }

    sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": result},
        upsert=True,
    )

    return jsonify(result)


@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    """Fetch all sessions for the dashboard, newest first."""
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
