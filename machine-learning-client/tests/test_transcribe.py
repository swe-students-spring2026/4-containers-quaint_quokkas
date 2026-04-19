"""Tests for video transcription. Whisper and moviepy are mocked."""

from unittest.mock import patch, MagicMock
import transcribe


@patch("transcribe.subprocess.run")
def test_extract_audio(mock_run):
    """extract_audio calls ffmpeg and returns the audio path."""
    result = transcribe.extract_audio("fake.mp4", "out.wav")

    assert result == "out.wav"
    mock_run.assert_called_once()


@patch("transcribe.os.remove")
@patch("transcribe.os.path.exists", return_value=True)
@patch("whisper.load_model")
@patch("transcribe.extract_audio", return_value="temp_audio.wav")
def test_transcribe_video(mock_extract, mock_load, _mock_exists, mock_remove):
    """transcribe_video returns the model's text and cleans up the temp file."""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "um hello world"}
    mock_load.return_value = mock_model

    result = transcribe.transcribe_video("fake.mp4")

    assert result == "um hello world"
    mock_extract.assert_called_once_with("fake.mp4")
    mock_remove.assert_called_once_with("temp_audio.wav")
