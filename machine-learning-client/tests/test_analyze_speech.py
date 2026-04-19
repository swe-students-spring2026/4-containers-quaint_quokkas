"""Tests for analyze_speech."""

from unittest.mock import patch
import analyze_speech


@patch("analyze_speech.transcribe_video", return_value="um hello world")
def test_analyze_speech(mock_transcribe):
    """analyze_speech stitches transcription and rating together."""
    result = analyze_speech.analyze_speech("fake.mp4")

    assert result["transcript"] == "um hello world"
    assert "rating" in result
    assert result["filler_counts"]["um"] == 1
    mock_transcribe.assert_called_once_with("fake.mp4")
