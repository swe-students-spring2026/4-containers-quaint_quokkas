import os
import tempfile
from flask import Flask, request, jsonify
from analyze_speech import analyze_speech
from analyze_video import analyze_vision

app = Flask(__name__)


@app.route("/analyze", methods=["POST"])
def analyze():
    if "video" not in request.files:
        return jsonify({"error": "No video file"}), 400

    video = request.files["video"]

    # Save to temp file, analyze, clean up
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
    video.save(tmp.name)
    tmp.close()

    try:
        speech_result = analyze_speech(tmp.name)
        vision_result = analyze_vision(tmp.name)
        return jsonify({"speech": speech_result, "vision": vision_result})
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"error": str(exc)}), 500
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
