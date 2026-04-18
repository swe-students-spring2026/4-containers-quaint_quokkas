"""Return transcript and filler-word analysis for a video."""
import json
import sys

from transcribe import transcribe_video
from filler_words import rate_transcript


def analyze_speech(video_path):
    """Return transcript and filler-word analysis for a video."""
    transcript = transcribe_video(video_path)
    analysis = rate_transcript(transcript)
    return {"transcript": transcript, **analysis}


if __name__ == "__main__":
    print(json.dumps(analyze_speech(sys.argv[1]), indent=2))
