import pytest
from unittest.mock import patch, MagicMock
from video_editor import process_segments, _render_clip
from bot_classes import VideoMeta, Segment
import os

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

@pytest.mark.asyncio
@patch('video_editor.asyncio.to_thread')
async def test_render_clip(mock_to_thread, tmp_path):
    mock_to_thread.return_value = None
    
    meta = VideoMeta(local_path="v.mp4", duration=10, width=1920, height=1080, is_landscape=True, original_filename="v", has_youtube_subs=False)
    seg = Segment(index=1, start_time="00:00:01,000", end_time="00:00:02,000", title="A", reason="B", caption="C", srt_content="1\n00:00:01,000 --> 00:00:02,000\nA")
    
    out_path = str(tmp_path / "out.mp4")
    srt_path = str(tmp_path / "sub.srt")
    
    with open(srt_path, "w") as f:
        f.write("dummy")
        
    await _render_clip(
        source_path=meta.local_path,
        start=seg.start_time,
        end=seg.end_time,
        srt_path=srt_path,
        output_path=out_path,
        is_landscape=meta.is_landscape,
        speed=1.0
    )
    
    mock_to_thread.assert_called_once()
