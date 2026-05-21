import pytest
import os
from unittest.mock import patch, mock_open, MagicMock
from bot_classes import VideoMeta, TranscriptSource
from transcriber import _process_existing_srt, get_transcript, _generate_whisper_transcript

@pytest.mark.asyncio
async def test_process_existing_srt():
    mock_srt_content = "1\n00:00:01,000 --> 00:00:05,000\nHello World\n"
    with patch('builtins.open', mock_open(read_data=mock_srt_content)):
        transcript = await _process_existing_srt('dummy.srt', TranscriptSource.USER_UPLOAD)
        
        assert transcript.source == TranscriptSource.USER_UPLOAD
        assert transcript.srt_content == mock_srt_content
        assert transcript.transcript_text == "Hello World"

@pytest.mark.asyncio
@patch('transcriber._process_existing_srt')
@patch('os.path.exists')
async def test_get_transcript_priority_user_srt(mock_exists, mock_process):
    mock_exists.return_value = True
    mock_process.return_value = "user_transcript"
    
    meta = VideoMeta(local_path="v.mp4", duration=10, width=1, height=1, is_landscape=True, original_filename="v", has_youtube_subs=False)
    
    res = await get_transcript(meta, user_srt_path="custom.srt")
    assert res == "user_transcript"
    mock_process.assert_called_once()

@pytest.mark.asyncio
@patch('transcriber.WhisperModel')
async def test_generate_whisper_transcript(mock_whisper_class, tmp_path):
    
    mock_model = MagicMock()
    mock_whisper_class.return_value = mock_model
    
    mock_segment = MagicMock()
    mock_segment.start = 1.0
    mock_segment.end = 2.0
    mock_segment.text = "Hello whisper"
    
    mock_info = MagicMock()
    mock_info.language = "en"
    
    mock_model.transcribe.return_value = ([mock_segment], mock_info)
    
    video_path = tmp_path / "video.mp4"
    video_path.touch()
    
    transcript = await _generate_whisper_transcript(str(video_path))
    
    assert transcript.source == TranscriptSource.WHISPER
    assert "Hello whisper" in transcript.transcript_text
    assert "00:00:01,000 --> 00:00:02,000" in transcript.srt_content
