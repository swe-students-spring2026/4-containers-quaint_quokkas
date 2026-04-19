import os
import tempfile
import subprocess 
from flask import Flask, request, jsonify
from analyze_speech import analyze_speech
from analyze_video import analyze_vision

app = Flask(__name__)

def get_duration(video_path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-select_streams", "a:0",
            "-show_entries", "packet=pts_time",
            "-of", "csv=p=0",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    lines = result.stdout.strip().split("\n")
    try:
        return float(lines[-1])
    except (ValueError, IndexError):
        return 0.0

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
        speech_result["duration_seconds"] = round(get_duration(tmp.name), 1)
        vision_result = analyze_vision(tmp.name)
        return jsonify({"speech": speech_result, "vision": vision_result})
    except Exception as exc:  # pylint: disable=broad-except
        import traceback                                                                                                                                                                                        
        traceback.print_exc()                                                                                                                                                                                   
        return jsonify({"error": str(exc)}), 500 
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
