"""Tests for the ML Client module."""

from unittest.mock import patch, MagicMock

# pylint: disable=missing-function-docstring

import mlclient


@patch("mlclient.time.sleep", side_effect=KeyboardInterrupt)
@patch("mlclient.save_result")
@patch("mlclient.cv2.imencode")
@patch("mlclient.classify_frame")
@patch("mlclient._create_landmarker")
@patch("mlclient.cv2.VideoCapture")
# pylint: disable=too-many-arguments, too-many-positional-arguments
def test_mlclient_main(
    mock_cap, _mock_landmarker, mock_classify, mock_imencode, mock_save, _mock_sleep
):
    mock_vid = MagicMock()
    mock_vid.read.return_value = (True, "dummy_frame")
    mock_cap.return_value = mock_vid

    mock_classify.return_value = ("rock", None)

    mock_buffer = MagicMock()
    mock_buffer.tobytes.return_value = b"fake_jpg_bytes"
    mock_imencode.return_value = (True, mock_buffer)

    mlclient.main()

    mock_cap.assert_called_once_with(0)
    mock_vid.read.assert_called_once()
    mock_classify.assert_called_once()
    mock_imencode.assert_called_once_with(".jpg", "dummy_frame")
    mock_save.assert_called_once()

    assert mock_save.call_args[0][0] == b"fake_jpg_bytes"
    assert mock_save.call_args[0][1] == "rock"

    mock_vid.release.assert_called_once()
