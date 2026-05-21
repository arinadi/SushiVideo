import pytest
from unittest.mock import patch, MagicMock
from video_editor import process_segments
from bot_classes import VideoMeta, Segment

@pytest.mark.asyncio
@patch('video_editor._render_clip')
async def test_process_segments(mock_render, tmp_path):
    mock_render.return_value = None
    
    meta = VideoMeta(local_path="v.mp4", duration=10, width=1920, height=1080, is_landscape=True, original_filename="v", has_youtube_subs=False)
    segments = [Segment(index=1, start_time="0", end_time="1", title="test title", reason="", caption="", srt_content="1\n")]
    
    out_dir = tmp_path / "out"
    files = await process_segments(meta, segments, str(out_dir))
    
    assert len(files) == 1
    assert "clip_1_test_title.mp4" in files[0]
    mock_render.assert_called_once()
