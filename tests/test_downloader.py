import pytest
from unittest.mock import patch, MagicMock
from downloader import _find_subtitle_file, process_uploaded_file, download_video

def test_find_subtitle_file(tmp_path):
    video_path = tmp_path / "video.mp4"
    video_path.touch()
    
    # Subtitle doesn't exist yet
    assert _find_subtitle_file(str(video_path)) is None
    
    # Create sub
    sub_path = tmp_path / "video.id.srt"
    sub_path.touch()
    
    assert _find_subtitle_file(str(video_path)) == str(sub_path)

@pytest.mark.asyncio
@patch('downloader.ffmpeg.probe')
async def test_process_uploaded_file(mock_probe):
    mock_probe.return_value = {
        'format': {'duration': '10.5'},
        'streams': [{'codec_type': 'video', 'width': 1920, 'height': 1080}]
    }
    
    meta = await process_uploaded_file("dummy.mp4")
    assert meta.duration == 10.5
    assert meta.is_landscape is True
    assert meta.has_youtube_subs is False

@pytest.mark.asyncio
@patch('downloader._download_sync')
async def test_download_video(mock_download_sync):
    mock_download_sync.return_value = "dummy_meta"
    meta = await download_video("http://url")
    assert meta == "dummy_meta"
