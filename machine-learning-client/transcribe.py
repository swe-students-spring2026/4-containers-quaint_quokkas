"""Generate a transcript from a video using Whisper."""
import os
import whisper
from moviepy import VideoFileClip


def extract_audio(video_path, audio_path="temp_audio.wav"):
    """Pull the audio track out of a video file and write it to disk."""
    video = VideoFileClip(video_path)
    if video.audio is None:
        video.close()
        raise ValueError(f"No audio track found in {video_path}")
    video.audio.write_audiofile(audio_path, logger=None)
    video.close()
    return audio_path


def transcribe_video(video_path, model_name="base"):
    """Transcribe the speech in a video and return the text."""
    audio_path = extract_audio(video_path)
    try:
        model = whisper.load_model(model_name)
        # The initial prompt nudges Whisper to keep disfluencies like "um"/"uh"
        # instead of cleaning them out of the transcript.
        result = model.transcribe(
            audio_path,
            initial_prompt="Um, uh, like, you know, I mean, so...",
        )
        return result["text"]
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
